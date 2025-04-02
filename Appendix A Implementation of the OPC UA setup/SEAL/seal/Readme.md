 Here are the codes that are connected to the Service Enabled Architechture Layer, like the Topic Watcher. 
 
 The topic watcher monitors the changes in the bandwidth usage of topics, the publisher(s) and subscriber(s) connected to it.
 It uniquely identifies network flows with 5-tuple of the publisher-subscriber pairs.
 It creates and sends requests to the the SEAL request handling server (NRM server) managing the network resources allowed to the communcation channels on the network.
 
 There is also the bandwidth monitoring (bw.py) code that runs on the service provider (publisher) machine, and the 5-tuple collecting (five_tuple_sub Python) script running on the broker between the publsiher and subscriber machine. (They will be uploaded after testing is finished and everythin is finalized.)

 The seal_user Python script is for testing the NRM server simulated using Connexion, which accepts 3GPP APIs for unicast/multicast subscriptions, group-management, location reporting and location area information retrival. The latter is done, but will be uploaded after testing for bugs and unhandled errors.

 The QoS_mapper script is for mapping the MQTT requests to the 3GPP QCI specifications, using some of the options specified in the 5QI specifications.

 The required other scripts will be uploaded here too.
 
