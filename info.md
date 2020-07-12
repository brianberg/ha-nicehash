[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]](hacs)
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

_Component to integrate with [NiceHash][nicehash]_



{% if not installed %}

## Installation

<!-- 1. Click install
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "NiceHash" -->

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
     rigs: true # (default = false) - Enable rig sensors
     devices: true # (default = false) - Enable device sensors
     payouts: true # (default = false) - Enable payout sensors
   ```

{% endif %}

<!-- ## Configuration is done in the UI -->

<!---->

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
