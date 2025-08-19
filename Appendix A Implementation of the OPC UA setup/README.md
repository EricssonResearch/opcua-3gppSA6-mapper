# Table of contents
- A_7 3GPP NRM emulation [a relative link](<A_7 3GPP NRM emulation/README.md>)
 - connexion [a relative link](<A_7 3GPP NRM emulation/connexion/README.md>)
  - Connexion.py and API specifactions (connexion-example-master/yaml [a relative link](<A_7 3GPP NRM emulation/connexion/connexion-example-master/yaml>))
- CAPIF [a relative link](CAPIF/README.md)
- Mininet [a relative link](Mininet/README.md)
- OPC-UA PubSub [a relative link](OPC-UA%20PubSub/README.md)
- SEAL [a relative link](SEAL/seal/README.md)
- mosquitto [a relative link](mosquitto/README.md)

# Small Summary

## A_7 3GPP NRM emulation
The A_7 3GPP NRM emulation directory contains the codes and configuration files, that make it possible for the emulated NRM server to accept and handle SEAL requests made by authorized user(s).
The NRM server is written using Connexion, to simplify development and understanding the working of the server by focusing on the request handling.
Used YAML configurations are expected to have the actual Python scripts name in the operation id. The scheme ApplicationName.OpeartionId. Which is ApplicationName.py and the function name in it is the OperationId exactly.

## CAPIF
The CAPIF directory does not contain code as of now, but will be updated with the code that communicating with OPC-UA PubSub shares the messaging interval of publisher, with the subscriber machine.

## Mininet
This directory contains the test cases used to test the completed codes on an emulated network with Mininet.

## OPC-UA PubSub
Contains the modified OPC UA publisher and subscriber codes and executables, used to generate trafic, from which the 5-tuple and statistics are collected, then SEAL request is formed using them.
The codes were from a previous dev build, the actual hash of the commit can be found in the README.md if you want build your own version.

## SEAL
The SEAL/seal subdirectory contains the Python scripts used to collect 5-tuple and unique network flow statistics informations, which is used by the topic_watcher to make SEAL request through the SEAL class found in the SEAL.py script.

## mosquitto
Contains the Mosquitto MQTT broker configurations used for testing OPC-UA communication, creating multiple flows using topic bridges.


# Demo video for the Mininet test case:NRM_sim_server_short_test_no_vlan_ordered_links.py
Link to the demo on YouTube: 

[![Video Title](https://img.youtube.com/vi/DcJuJ1ulcW8/0.jpg)](https://www.youtube.com/watch?v=DcJuJ1ulcW8)

Or just the link in non-embeded format: [YouTube link](https://youtu.be/DcJuJ1ulcW8)
