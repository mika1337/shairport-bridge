# shairport-bridge
Websocket bridge with [`shairport-sync`](https://github.com/mikebrady/shairport-sync) MQTT interface.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## References
This projet is based on [`shairport-sync-mqtt-display`](https://github.com/idcrook/shairport-sync-mqtt-display)

## Requirements
- [Python paho-mqtt](https://www.eclipse.org/paho/)
- [Python websockets](https://websockets.readthedocs.io/en/stable/)
- [shairport-sync](https://github.com/mikebrady/shairport-sync) (>=3.3) with MQTT enabled (see [configuration](#configuration))
- MQTT broker ([mosquitto](https://mosquitto.org) for instance)

## Configuration
To enable shairport-sync MQTT interface, add the following content to `/etc/shairport-sync.conf`:
```
mqtt =
{
        enabled = "yes";
        hostname = "localhost"; // Hostname of the MQTT Broker
        port = 1883;
        topic = "shairport-sync/rpih1"; //MQTT topic where this instance of shairport-sync should publish. If not set, the general.name value is used.
        publish_parsed = "yes"; //whether to publish a small (but useful) subset of metadata under human-understandable topics
        publish_cover = "yes"; //whether to publish the cover over mqtt in binary form. This may lead to a bit of load on the broker
        enable_remote = "yes"; //whether to remote control via MQTT. RC is available under `topic`/remote.
};
```

## Documentation
TODO ...

## Licensing
This project is licensed under the MIT license.
