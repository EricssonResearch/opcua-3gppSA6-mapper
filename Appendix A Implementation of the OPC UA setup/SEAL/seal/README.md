 # SEAL function related codes
 
 Here are the codes that are connected to the Service Enabled Architechture Layer, like the Topic Watcher. 


 ## Codes and decsription
 
 The topic watcher monitors the changes in the bandwidth usage of topics, the publisher(s) and subscriber(s) connected to it.
 It uniquely identifies network flows with 5-tuple of the publisher-subscriber pairs.
 It creates and sends requests to the the SEAL request handling server (NRM server) managing the network resources allowed to the communcation channels on the network.
 
 There is also the bandwidth monitoring code that runs on the service provider (publisher) machine, and the 5-tuple collecting (five_tuple_sub Python) script running on the broker between the publsiher and cloud broker machine. 

 The 5-tuple collecting code has two versions.
 Versions:
 * five_tuple_final_2_log
 * five_tuple_final_2_sub
 The "five_tuple_final_2_log" uses the logging feature of the Mosquitto MQTT broker. This was created to avoid remote access to the debug topics of the broker.
 The "five_tuple_final_2_sub" subscribes to the MQTT broker's debug topics and collects data for 

 The "seal_user" Python script is for testing the NRM server simulated using Connexion, which accepts 3GPP APIs for unicast/multicast subscriptions, group-management, location reporting and location area information retrival. The latter is done, but will be uploaded after testing for bugs and unhandled errors.

 The "QoS_mapper" script is for mapping the MQTT requests to the 3GPP QCI specifications, using some of the options specified in the 5QI specifications.

 The "seal_user_NRM_tester" Python script creates and sends SEAL requests implemented in the NRM server simulation code. It tries out multiple settings, except the for the QCI.

 The "topic_watcher" receives the collected 5-tuple and network flow statistics informations and SEAL requests using them. This code creates unicast-subscriptions and requests bandwidth and QCI for 5-tuple based on the communication's demands.

 The required other scripts will be uploaded here too.
 

 ## How to run

 All codes can be stated individually, but the OPC UA using Mininet test will run them in one network (,which will be uploaded later).
 
 Topic Watcher:
 ```
 python3 topic_watcher.py
 ```
 
 5-tuple collecting MQTT subscriber:
 ```
 python3 five_tuple_final_2_sub.py
 ```

 5-tuple collecting from logs:
 ```
 python3 five_tuple_final_2_log.py
 ```

 Unique network flow statistics calculating subscriber:
 ```
 python3 bw.py
 ```

 SEAL function using NRM tester:
 ```
 python3 seal_user_NRM_tester.py
 ```
