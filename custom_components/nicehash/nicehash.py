"""
NiceHash API interface

References:
 - https://docs.nicehash.com/main/index.html
 - https://github.com/nicehash/rest-clients-demo/blob/master/python/nicehash.py
"""
from datetime import datetime
from hashlib import sha256
import hmac
import json
import requests_async as requests
import sys
from time import mktime
import uuid

from .const import NICEHASH_API_URL


class NiceHashPublicClient:
    async def get_exchange_rates(self):
        exchange_data = await self.request("GET", "/main/api/v2/exchangeRate/list")
        return exchange_data["list"]

    async def request(self, method, path, query=None, body=None):
        url = NICEHASH_API_URL + path

        if query is not None:
            url += f"?{query}"

        async with requests.Session() as session:
            if body:
                data = json.dumps(body)
                response = await session.request(method, url, data=data)
            else:
                response = await session.request(method, url)

            if response.status_code == 200:
                return response.json()
            else:
                err_messages = [str(response.status_code), response.reason]
                if response.content:
                    err_messages.append(str(response.content))
                    raise Exception(": ".join(err_messages))


class NiceHashPrivateClient:
    def __init__(self, organization_id, key, secret, verbose=False):
        self.organization_id = organization_id
        self.key = key
        self.secret = secret
        self.verbose = verbose

    async def get_accounts(self):
        return await self.request("GET", "/main/api/v2/accounting/accounts2")

    async def get_mining_rigs(self):
        return await self.request("GET", "/main/api/v2/mining/rigs2")

    async def get_mining_rig(self, rig_id):
        return await self.request("GET", f"/main/api/v2/mining/rig2/{rig_id}")

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

        async with requests.Session() as session:
            session.headers = headers

            url = NICEHASH_API_URL + path
            if query:
                url += "?" + query

            if self.verbose:
                print(method, url)

            if data:
                response = await session.request(method, url, data=data)
            else:
                response = await session.request(method, url)

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
