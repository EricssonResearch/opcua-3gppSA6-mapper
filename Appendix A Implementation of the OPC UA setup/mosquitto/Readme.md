# MQTT bokrer configuration files
Configuration files for using Mosquitto MQTT broker in the tests or run manually for manual testing.

## Configurations

They allow anonymous connections to avoid possible problems with authentication as it is only for prototyping and proof of concept.
Create listener(s) with specified port(s) to listen to.
Proxy broker uses topic bridges to forward traffic in differnt network flows to the Cloud broker side.

## How to Run
Proxy broker on the Provider side to create unique network flows:

```
mosquitto -c proxy.conf
```

Remote broker in the cloud for connecting provider and subscriber/user:

```
mosquitto -c virtual_host.conf
```

The codes will be also used in the OPC UA using test (will uploaded later in June 2025).
