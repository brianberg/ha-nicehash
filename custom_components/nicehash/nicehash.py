"""
NiceHash API interface

References:
 - https://docs.nicehash.com/main/index.html
 - https://github.com/nicehash/rest-clients-demo/blob/master/python/nicehash.py
"""
from datetime import datetime
from hashlib import sha256
import hmac
import httpx
import json
import logging
import re
import sys
from time import mktime
import uuid

from .const import MAX_TWO_BYTES, NICEHASH_API_URL

_LOGGER = logging.getLogger(__name__)


def parse_device_name(raw_name):
    name = re.sub(
        r"(\s?\(r\))|(\s?\(tm\))|(\s?cpu)|(\s?graphics)|(\s?@.*ghz)",
        "",
        raw_name,
        flags=re.IGNORECASE,
    )

    return name


class MiningAlgorithm:
    def __init__(self, data: dict):
        self.name = data.get("title")
        self.speed = float(data.get("speed"))
        unit = data.get("displaySuffix")
        self.unit = f"{unit}/s"


class MiningRigDevice:
    def __init__(self, data: dict):
        self.id = data.get("id")
        self.name = parse_device_name(data.get("name"))
        self.status = data.get("status").get("description")
        self.temperature = int(data.get("temperature")) % MAX_TWO_BYTES
        self.load = float(data.get("load"))
        self.rpm = float(data.get("revolutionsPerMinute"))
        self.speeds = data.get("speeds")


class MiningRig:
    def __init__(self, data: dict):
        self.id = data.get("rigId")
        self.name = data.get("name")
        self.status = data.get("minerStatus")
        self.status_time = data.get("statusTime")
        self.profitability = data.get("profitability")
        self.unpaid_amount = data.get("unpaidAmount")
        devices = data.get("devices")
        if devices is not None:
            self.num_devices = len(devices)
            self.devices = dict()
            for device_data in devices:
                device = MiningRigDevice(device_data)
                self.devices[f"{device.id}"] = device
        else:
            self.num_devices = 0
            self.devices = dict()

    def get_algorithms(self):
        algorithms = dict()
        for device in self.devices.values():
            if len(device.speeds) > 0:
                algo = MiningAlgorithm(device.speeds[0])
                existingAlgo = algorithms.get(algo.name)
                if existingAlgo:
                    existingAlgo.speed += algo.speed
                else:
                    algorithms[algo.name] = algo

        return algorithms


class Payout:
    def __init__(self, data: dict):
        self.id = data.get("id")
        self.currency = "Unknown"
        self.created = data.get("created")
        self.amount = float(data.get("amount"))
        self.fee = float(data.get("feeAmount"))
        self.account_type = "Unknown"
        # Currency
        currency = data.get("currency")
        if currency:
            self.currency = currency.get("enumName")
        # Account Type
        account_type = data.get("accountType")
        if account_type:
            self.account_type = account_type.get("enumName")


class NiceHashPublicClient:
    async def get_exchange_rates(self):
        exchange_data = await self.request("GET", "/main/api/v2/exchangeRate/list")
        return exchange_data.get("list")

    async def request(self, method, path, query=None, body=None):
        url = NICEHASH_API_URL + path

        if query is not None:
            url += f"?{query}"

        _LOGGER.debug(url)

        async with httpx.AsyncClient() as client:
            if body:
                data = json.dumps(body)
                response = await client.request(method, url, data=data)
            else:
                response = await client.request(method, url)

            if response.status_code == 200:
                return response.json()
            else:
                err_messages = [str(response.status_code), response.reason]
                if response.content:
                    err_messages.append(str(response.content))
                    raise Exception(": ".join(err_messages))


class NiceHashPrivateClient:
    def __init__(self, organization_id, key, secret):
        self.organization_id = organization_id
        self.key = key
        self.secret = secret

    async def get_accounts(self):
        return await self.request("GET", "/main/api/v2/accounting/accounts2")

    async def get_mining_rigs(self):
        return await self.request("GET", "/main/api/v2/mining/rigs2")

    async def get_mining_rig(self, rig_id):
        return await self.request("GET", f"/main/api/v2/mining/rig2/{rig_id}")

    async def get_rig_payouts(self, size=84):
        query = f"size={size}"
        return await self.request("GET", "/main/api/v2/mining/rigs/payouts", query)

    async def request(self, method, path, query="", body=None):
        xtime = self.get_epoch_ms_from_now()
        xnonce = str(uuid.uuid4())

        message = f"{self.key}\00{str(xtime)}\00{xnonce}\00\00{self.organization_id}\00\00{method}\00{path}\00{query}"

        data = None
        if body:
            data = json.dumps(body)
            message += f"\00{data}"

        digest = hmac.new(self.secret.encode(), message.encode(), sha256).hexdigest()
        xauth = f"{self.key}:{digest}"

        headers = {
            "X-Time": str(xtime),
            "X-Nonce": xnonce,
            "X-Auth": xauth,
            "Content-Type": "application/json",
            "X-Organization-Id": self.organization_id,
            "X-Request-Id": str(uuid.uuid4()),
        }

        async with httpx.AsyncClient() as client:
            client.headers = headers

            url = NICEHASH_API_URL + path
            if query:
                url += f"?{query}"

            _LOGGER.debug(url)

            if data:
                response = await client.request(method, url, data=data)
            else:
                response = await client.request(method, url)

            if response.status_code == 200:
                return response.json()
            else:
                err_messages = [str(response.status_code), response.reason]
                if response.content:
                    err_messages.append(str(response.content))
                    raise Exception(": ".join(err_messages))

    def get_epoch_ms_from_now(self):
        now = datetime.now()
        now_ec_since_epoch = mktime(now.timetuple()) + now.microsecond / 1000000.0
        return int(now_ec_since_epoch * 1000)
