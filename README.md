# NiceHash Home Assistant Integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

_Component to integrate with [NiceHash][nicehash]_

**This component will set up the following platforms.**

Platform | Description
-- | --
`binary_sensor` | Show something `True` or `False`.
`sensor` | Show info from NiceHash API.
`switch` | Switch something `True` or `False`.

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `nicehash`.
4. Download _all_ the files from the `custom_components/nicehash/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "NiceHash"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/nicehash/.translations/en.json
custom_components/nicehash/.translations/nb.json
custom_components/nicehash/.translations/sensor.nb.json
custom_components/nicehash/__init__.py
custom_components/nicehash/binary_sensor.py
custom_components/nicehash/config_flow.py
custom_components/nicehash/const.py
custom_components/nicehash/manifest.json
custom_components/nicehash/sensor.py
custom_components/nicehash/switch.py
```

## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)


[nicehash]: https://nicehash.com
[buymecoffee]: https://www.buymeacoffee.com/brianberg
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/custom-components/nicehash.svg?style=for-the-badge
[commits]: https://github.com/custom-components/nicehash/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/custom-components/nicehash.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Brian%20Berg%20%40brianberg-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/custom-components/nicehash.svg?style=for-the-badge
[releases]: https://github.com/custom-components/nicehash/releases

