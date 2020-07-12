[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]](hacs)
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

A [Home Assistant][homeassistant] integration that creates a collection of [NiceHash][nicehash] account balance, rig, and individual device sensors.

![Preview](https://user-images.githubusercontent.com/5121741/87257533-b4135f00-c469-11ea-82ca-e9614ead4e26.png)

## Sensors
  - Account Balances (BTC and USD/EUR)
    - Total
    - Pending
    - Available
  - Rigs
    - Status
    - Temperature
    - Profitability
  - Devices
    - Status
    - Algorithm
    - Speed
    - Temperature
    - Load
    - RPM
  - Most Recent Mining Payout

None of the sensors are added by default. See installation instructions for available configuration options.

{% if not installed %}

## Installation

### HACS (recommended)

1. Open HACS > Integrations
1. Add https://github.com/brianberg/ha-nicehash as a custom repository as Category: Integration
1. Click install under "NiceHash" in the Integrations tab
1. Generate [NiceHash][nicehash] API key
   - Supported API Permissions
     - Wallet Permissions > View balances...
     - Mining Permissions > View mining data...
   - See this [repository](https://github.com/nicehash/rest-clients-demo) for assistance
1. Add `nicehash` to `configuration.yaml`
   ```
   nicehash:
     organization_id: # <org_id>
     api_key: # <api_key_code>
     api_secret: #<api_secret_key_code>
     currency: EUR # (default = USD)
     balances: true # (default = false) - Enable balance sensors
     rigs: true # (default = false) - Enable rig sensors
     devices: true # (default = false) - Enable device sensors
     payouts: true # (default = false) - Enable payout sensors
   ```
1. Restart Home Assistant

### Manual

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `nicehash`.
1. Download _all_ the files from the `custom_components/nicehash/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Generate [NiceHash][nicehash] API key
   - Supported API Permissions
     - Wallet Permissions > View balances...
     - Mining Permissions > View mining data...
   - See this [repository](https://github.com/nicehash/rest-clients-demo) for assistance
1. Add `nicehash` to `configuration.yaml`
   ```
   nicehash:
     organization_id: # <org_id>
     api_key: # <api_key_code>
     api_secret: #<api_secret_key_code>
     currency: EUR # (default = USD)
     balances: true # (default = false) - Enable balance sensors
     rigs: true # (default = false) - Enable rig sensors
     devices: true # (default = false) - Enable device sensors
     payouts: true # (default = false) - Enable payout sensors
   ```
1. Restart Home Assistant

{% endif %}

<!-- ## Configuration is done in the UI -->

<!---->

[homeassistant]: https://github.com/home-assistant/home-assistant
[nicehash]: https://nicehash.com
[buymecoffee]: https://www.buymeacoffee.com/brianberg
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/brianberg/ha-nicehash.svg?style=for-the-badge
[commits]: https://github.com/brianberg/ha-nicehash/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/brianberg/ha-nicehash?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Brian%20Berg%20%40brianberg-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/v/release/brianberg/ha-nicehash?style=for-the-badge
[releases]: https://github.com/brianberg/ha-nicehash/releases
