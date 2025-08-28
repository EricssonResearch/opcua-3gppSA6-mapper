
# Intorudction

This library contains the modified code and executables used to create unique flow topics with Open Platform Communication United Architecture PubSub.
Used open62541 an open source implementation of OPC UA. The development build was used, with the commit hash (695864553127fb2f67dbbec848e38bd40f7e4d59).
This was chose, because when first working with OPC UA PubSub it was this version, that had included examples for the publisher and subscriber as well.
The original examples were modified to publish/subscribe to multiple topics with specified names and different QoS settings to the appropriate MQTT broker.
The publisher publishes to the proxy broker, which sends the topics through different topic bridges. 

The publisher has another modified version that also makes use of UNIX sockets to publish it's internal API for changing the publishing interval. This API was created based on the Common API Framework (CAPIF) by EVOLVED-5G as proof of concept for the standardization of API sharing, which was later moved under OpenCAPIF. The original repo was archived and the OpenCAPIF maintained by ETSI Labs is the one to be used. The publisher communicates with a JavaScript code, that registers to the the CAPIF Core Services and after proper authentication publishes it's API. The published API is discovered by another JavaScript code, that can invoke it on the subscriber's needs. 

Everything was written and tested on Ubuntu 22.04 LTS.


# Usage

There are the executables, that can be ran with "./name_of_the_executable", and the source code, that can be used to build executables in the open62541 repository.
These are MQTT publisher and subscriber, which needs broker. First run the broker, before running the executables.
The library contains the subdirectories of publisher and subscriber. Each contains the source code and executable necessary for testing on the network, Mininet or locally.
The local_test subdirectory contains the codes that are used for testing with one machine.

For running the publisher:
```
./tutorial_pubsub_mqtt_publish
```

For starting the subscriber:
```
./tutorial_pubsub_mqtt_subscribe
```


Running with custom IPs and ports:
```
./tutorial_pubsub_mqtt_publish --url opc.mqtt://127.0.0.1:1883 --topic topic1 topic2 --freq 600 500
./tutorial_pubsub_mqtt_subscribe --url opc.mqtt://10.1.2.2:8083 --topic topic1 topic2 --freq 600 500
```

Usage:
```
"Usage: tutorial_pubsub_mqtt_publish [--url <opc.mqtt://hostname:port>] "
        "[--topic <1 or 2 mqttTopics, with space in between>] "
        "[--freq <1 or 2 frequencies in ms, with space in between>]"
        "[--json]\n"
        "  Defaults are:\n"
        "  - Url: opc.mqtt://127.0.0.1:1883\n"
        "  - Topic: topic1 topic2\n"
        "  - Frequency: 600 500\n"
        "  - JSON: Off\n"
```

```
"Usage: tutorial_pubsub_mqtt_subscribe [--url <opc.mqtt://hostname:port>] "
        "[--topic <1 or 2 mqttTopics, with space in between>] "
        "[--freq <1 or 2 frequencies in ms, with space in between>]"
        "[--json]\n"
        "  Defaults are:\n"
        "  - Url: opc.mqtt://127.0.0.1:1883\n"
        "  - Topic: topic1 topic2\n"
        "  - Frequency: 600 500\n"
        "  - JSON: Off\n"
```