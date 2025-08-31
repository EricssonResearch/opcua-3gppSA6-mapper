# Table of contents
- [A_7 3GPP NRM emulation](<A_7 3GPP NRM emulation/README.md>)
	- [connexion (contains the Connexion.py and the APIs)](<A_7 3GPP NRM emulation/connexion/README.md>)
		- [API specifactions (connexion-example-master/yaml](<A_7 3GPP NRM emulation/connexion/connexion-example-master/yaml>))
- [CAPIF](CAPIF/README.md)
- [Mininet](Mininet/README.md)
- [OPC-UA PubSub](OPC-UA%20PubSub/README.md)
- [SEAL](SEAL/seal/README.md)
- [mosquitto](mosquitto/README.md)


# Introduction
This directory contains the implementation details for setting up the OPC UA environment, including the necessary configurations and code structure.
These set of codes and tools explore the passibility of creating and managing unique network flows in OPC UA Publisher-Subscriber MQTT communication.
It builds on the concepts introduced in ROS2 as unique flow topic relay [ROS2 unique flow topic relay](<https://github.com/Ericsson/ros2-3gppSA6-mapper/tree/main>). It does not demultiplex/multiplex the topics for path switching, but creates multiple 5-tuple communication flows.
To work like the mentioned ROS2 unique flow topic relay, the MQTT broker would need a plugin built in that does this automatically, if set to use.
This repository explores the potential of making TCP based MQTT communication more efficient and reliable, based on the needs of the communicating devices.
Because of the nature of MQTT, the QoS (Quality of Service) setting is quite limited (best effort, reliable, only once). 
This implementation aims to provide a more flexible and efficient way to manage communication flows in OPC UA MQTT communications, by using QoS Class Identifiers introduced in 3GPP 3GPP Long Term Evolution (LTE) networks.


Everything was developed and tested on Ubuntu 22.04 LTS. Necessary packages are in the requirements.txt file, but the used software and versions can be found in the appropriate directories in the README.

# Short Summary of subdirectories

- ## A_7 3GPP NRM emulation
The A_7 3GPP NRM emulation directory contains the codes and configuration files, that make it possible for the emulated NRM server to accept and handle SEAL requests made by authorized user(s).
The NRM server is written using Connexion, to simplify development and understanding the working of the server by focusing on the request handling.
Used YAML configurations are expected to have the actual Python scripts name in the operation id. The scheme ApplicationName.OpeartionId. Which is ApplicationName.py and the function name in it is the OperationId exactly.

- ## CAPIF
The CAPIF directory does not contain code as of now, but will be updated with the code that communicating with OPC-UA PubSub and shares the messaging interval of publisher, with the subscriber machine.

- ## Mininet
This directory contains the test cases used to test the completed codes on an emulated network with Mininet.

- ## OPC-UA PubSub
Contains the modified OPC UA publisher and subscriber codes and executables, used to generate trafic, from which the 5-tuple and statistics are collected, then SEAL request is formed using them.
The codes were from a previous dev build, the actual hash of the commit can be found in the README.md if you want build your own version.

- ## SEAL
The SEAL/seal subdirectory contains the Python scripts used to collect 5-tuple and unique network flow statistics informations, which is used by the topic_watcher to make SEAL request through the SEAL class found in the SEAL.py script.

- ## mosquitto
Contains the Mosquitto MQTT broker configurations used for testing OPC-UA communication, creating multiple flows using topic bridges.




# Basic Usage

For simple testing it advised to use the Mininet test scripts.[link folder](<A_7 3GPP NRM emulation/Mininet/tests/>)

Example:
```
sudo python3 NRM_sim_server_short_test_no_vlan_ordered_links.py
```

```
sudo python3 NRM_sim_server_short_test_with_vlan.py
```

```
sudo python3 NRM_sim_opc-ua_test.py
```

# Advanced Usage

For advanced testing the user can start everything manually, for this the original codes were updated to take arguments for specifying IPs, without modifying the source code(s) every time.
For MQTT broker the Eclipse Mosquitto MQTT broker was chosen, which uses topic bridges to create multiple network flows from the topics published by the OPC UA publisher.
The setup involves using 2 MQTT brokers. One MQTT broker (Proxy broker) on the publisher side to demultiplex the topics published and send them to the second MQTT broker (Virtual host broker) through topic bridges.
The second broker acts just like any MQTT broker, it receives the demultiplexed topics and the statistics collected from the network flows.
These collected statistics alongside with the 5-tuple information of communication is used to make 3GPP SEAL requests (Network Resource Adaption API requests).
This allows a higher QoS management of chosen topics and not just use the simple QoS implemented by most MQTT bokers (QoS best effort, at most once, at least once).


Start order:
First start the NRM server, if topic watcher will not be used in local-test mode, if not start from the second.
For second, the second MQTT broker, or virtual host broker. For third, the topic watcher, then start as fourth, the 5-tuple collecting code.
For fifth start the MQTT broker known as the proxy broker. After this everything can be started in any preferred order.
But advising an order: Start the publisher, then the statistics collecting code, then the subscriber.


## Publisher host

Starting the Proxy broker:
```
mosquitto -c mosquitto/proxy.conf
# or for local (one machine) testing
mosquitto -c mosquitto/local_test/proxy.conf
```

Starting the OPC UA Publisher:
```
# For local (one machine) testing 
./OPC-UA\ PubSub/publisher/local_test/tutorial_pubsub_mqtt_publish #--topic topic1 topic 2 --freq 600 500
# For multi device testing
./OPC-UA\ PubSub/publisher/tutorial_pubsub_mqtt_publish #--url <opc.mqtt://hostname:port> --topic topic1 topic 2 --freq 600 500
```

Starting the unique network flow statistics collector code:
```
python3 /OPC-UA\ PubSub/publisher/bw.py
# or it can be found in the seal folder as well
python3 /SEAL/seal/bw.py 127.0.0.1 8080
```




## MQTT host

Starting the Virtual host broker:
```
mosquitto -c mosquitto/virtual_host.conf
# or for local (one machine) testing
mosquitto -c mosquitto/local_test/virtual_host.conf
```

Starting the topic watcher:
```
python3 /SEAL/seal/topic_watcher.py
```

Starting the 5-tuple collecting code:
```
#For collecting 5-tuple information from the log file of the MQTT broker
python3 /SEAL/seal/five_tuple_final_2_log.py 

#For collecting 5-tuple information from the SYS topics of the MQTT broker
python3 /SEAL/seal/five_tuple_final_2_sub.py 10.1.1.1 8081
```




## Network Resource Manager host

Here the NRM server is prepared for no connection from the UNIX socket acting as the network controller or the MySQL database being down.
The NRM server does not really start until, the code was able estabilish connection with the database and the UNIX socket.

Starting the NRM server emulation, but if topic watcher is set to:
```
python3 /A_7 3GPP NRM emulation/connexion/Connexion.py 10.2.2.2 7000
```

Mininet emulating code, that accepts the NRM server's network resource allocation:
```
python3 /A_7 3GPP NRM emulation/connexion/mininet_unix_server_sim.py
```


## Subscriber host

Start the OPC UA Subscriber.
```
# For local (one machine) testing 
./OPC-UA\ PubSub/subscriber/local_test/tutorial_pubsub_mqtt_subscribe
# For multi device testing
./OPC-UA\ PubSub/subscriber/tutorial_pubsub_mqtt_subscribe 10.1.1.1 8083
```


# Demo video for the Mininet test case: NRM_sim_server_short_test_no_vlan_ordered_links.py
Link to the demo on YouTube: 

[![3GPP SEAL emulation server](https://img.youtube.com/vi/DcJuJ1ulcW8/0.jpg)](https://www.youtube.com/watch?v=DcJuJ1ulcW8)

Or just the link in non-embeded format: [https://youtu.be/DcJuJ1ulcW8](https://youtu.be/DcJuJ1ulcW8)



# Possible Improvements

Making the remapping of topics and creation of topic bridges automatic, or making the MQTT topic bridges publish the unique flow topics with unique identifier (OPC UA: Wirter Group and/or Reader Group identifier, which in theory is unique) to the virtual host broker.


