# © Ericsson AB 2024 - All Rights Reserved. No part of this software may be reproduced in any form without the written permission of the copyright owner.
# Distribution error
# No
#
# Disclaimer
# Controlled by agreement
#
# Change clause
# Controlled by agreement


from mimetypes import init
from operator import ne
import struct
import traceback
import time
import paho.mqtt.client as paho
import json
from enum import Enum
import http.client as http_client


from QoS_mapper import QoSmapper
from SEAL import SEAL
#from SEAL_state_machine import SEAL_state_machine
from numpy import uint8,uint16, uint64

class qos_profil:
    reliability = 0
    lifespan_miliseconds = 0
    duration_miliseconds = 0
    liveliness = 0
    lease_duration_nanoseconds = 0 *1000



networkexposure = SEAL()
#self2 = 
local_test = 0
#url_SEAL = 'http://172.16.7.10:5500'
active_topics = {}
ros2_domain_id = 0
seal_sm = None
broker="10.0.1.2"
broker="127.0.0.1"
port1=8883


##Connexion Mockup szerver
CONNEXION_IP = "127.0.0.1" ## Will be different in Mininet test
PORT = 8000
connexion_http_client = http_client.HTTPSConnection



def universal_bw (msgdirstat2):
    if type(active_topics[msgdirstat2['topic']][5]) is str:
        bw_info = active_topics[msgdirstat2['topic']][5].split()
        current_bw = float(bw_info[0])
        multiplier = bw_info[1]
        if "MB" in multiplier:
            current_bw = current_bw * 1000 * 1000
        elif "KB" in multiplier:
            current_bw = current_bw * 1000

    else:
        current_bw = active_topics[msgdirstat2['topic']][5]

    return current_bw




class Ros2QoS_parser:
    # qos_profile = qos_profil
    # qos_profile.reliability = 0
    # qos_profile.lifespan_miliseconds = 60000
    # qos_profile.duration_miliseconds = 60000
    # qos_profile.liveness = 900000
    # qos_profile.lease_duration_nanoseconds = 900000 *1000
    #qos_profile = qos_profil
    def __init__(self, qos):
        self.qos_profile = qos_profil
        self.qos_profile.reliability = 0
        self.qos_profile.lifespan_miliseconds = 60000000
        self.qos_profile.duration_miliseconds = 60000000
        self.qos_profile.liveliness = 900000
        self.qos_profile.lease_duration_nanoseconds = 900000 *1000
        
        print("qos_profile:"+str(self.qos_profile))

    def get_qos(self, qos):
        self.qos_profile.reliability = qos
        return self.qos_profile

    def parseQoS(self, qos_profile, rate):
        print("--- Parse QoS function ---")
        """Map QCI values from Resource Type (RT), Priority Level (PL), Packet Delay Budget (PDB), Packet Error Loss Rate (PELR), Maximum Data Burst Volume (MDBV), Data Rate Averaging Window (DRAW)"""
        PDB = 500
        PELR = 1e-2
        #History
        #    Keep last: only store up to N samples, configurable via the queue depth option.
        #    Keep all: store all samples, subject to the configured resource limits of the underlying middleware.

        #Depth
        #    Queue size: only honored if the “history” policy was set to “keep last”.

        #Reliability
        #    Best effort: attempt to deliver samples, but may lose them if the network is not robust.
        #    Reliable: guarantee that samples are delivered, may retry multiple times.

        # the DDS does this functionality by itself, should this be supported by the network by low PELR or switch on e.g., HARQ?
        if qos_profile.reliability == 0:
            print("Best effort")
            PELR = 1e-2
        elif qos_profile.reliability == 1:
            print("Reliable")
            PELR = 1e-6
        elif qos_profile.reliability == 2:
            print("Sending messages exactly once")
        
        print("PELR " + str(PELR))


        #Durability
        #    Transient local: the publisher becomes responsible for persisting samples for “late-joining” subscriptions.
        #    Volatile: no attempt is made to persist samples.




        #Lifespan
        #    Duration: the maximum amount of time between the publishing and the reception of a message without the message being considered stale or expired (expired messages are silently dropped and are effectively never received).
        self.qos_profile.lifespan_miliseconds = qos_profile.lifespan_miliseconds #qos_profile.lifespan.nanoseconds / 10e9
        PDB = min(PDB, self.qos_profile.lifespan_miliseconds)
        print("PDB " + str(PDB))


        #Deadline
        #    Duration: the expected maximum amount of time between subsequent messages being published to a topic
        # NOTE: this is part of the profile, which might be not setup properly, it could be measured by Hz
        # valszeg csak egy Warning-ot lehetne kiadni h nincs a mert Hz-el aranyban
        
        #60 seconds is the default normally (can be changed, but broker doesn't communicate it)
        
        self.qos_profile.duration_miliseconds = qos_profile.lifespan_miliseconds #qos_profile.deadline.nanoseconds / 10e9
        if self.qos_profile.duration_miliseconds < (rate / 1000):
            print("WARNING: QoS profile duration is set lower than the publishing rate") #biztos h a publishing-et nezem, nem a subscribert?
        # PDB = min(PDB, duration_miliseconds)
        # print("PDB " + str(PDB))



        #Liveliness
        #    Automatic: the system will consider all of the node’s publishers to be alive for another “lease duration” when any one of its publishers has published a message.
        #    Manual by topic: the system will consider the publisher to be alive for another “lease duration” if it manually asserts that it is still alive (via a call to the publisher API).
        self.qos_profile.liveliness = qos_profile.liveliness #qos_profile.liveliness

        #Lease Duration
        #    Duration: the maximum period of time a publisher has to indicate that it is alive before the system considers it to have lost liveliness (losing liveliness could be an indication of a failure).
        # ha lejar ez es ledobjak akkor lehet h a connectivity-t is meg lehetne szuntetni, nem tudom errol ki dob nekem callback-et
        self.qos_profile.lease_duration_nanoseconds = qos_profile.lease_duration_nanoseconds #qos_profile.liveliness_lease_duration
        # if lease_duration_nanoseconds 

        print("--------- ros2qos_parser END ----------")
        return (PDB, PELR)



addressdir = {
    "Src": {"Addr": '-1', "Port": '-1', "ClientID": "id"},
    "Dest": {"Addr": '-2', "Port": '-2', "ClientID": "id"},
    "Protocol" : "TCP",
    "ClientID": "id",
    "Topic" : str,
    "QoS": -1
}
# addressdir2 = {
#     "Src": {"Addr": '-1', "Port": '-1'},
#     "Dest": {"Addr": '-2', "Port": '-2'},
#     "Protocol" : "TCP",
#     "ClientID" : "id"
# }
Locator = {
    "UNICAST" : int(1),
    "MULTICAST": int(2),
    "cast" : int(0),

    "UDPV4":int(1),
    "UDPV6":int(2),
    "TCPV4":int(3),
    "TCPV6":int(4),
    "kind": int(0),

    "address": [int(0)]*16,
    "port": int(0),
}
Locator2 = {
    "UNICAST" : int(1),
    "MULTICAST": int(2),
    "cast" : int(0),

    "UDPV4":int(1),
    "UDPV6":int(2),
    "TCPV4":int(3),
    "TCPV6":int(4),
    "kind": int(0),

    "address": [int(0)]*16,
    "port": int(0),
}
msgdir = {
    "ADDED" : int(1),
    "REMOVED" : int(2),
    "event_type" : int(0),
    "topic" : str,
    "source" : Locator,
    "destination" : Locator2,
}

msgdirstat = {
    "topic" : str,
    "start" : float,
    "num_messages" : uint64,
    "num_bytes" : uint64,
    "window_duration_secs" : float,
    "window_bandwidth" : float,
    "window_rate" : float,
    "window_avarage_delta" : float,
    "min_s" : uint64,
    "max_s" : uint64,
    "mean" : float
}

# msgdirstats = {
#     "stamp" : float,
#     "stats": msgdirstat[]
# }

# def on_message(client, userdata, msg):
#     topic=msg.topic
#     m_decode=str(msg.payload.decode("utf-8","ignore"))
#     print("data Received type",type(m_decode))
#     print("data Received",m_decode)
#     print("Converting from Json to Object")
#     m_in=json.loads(m_decode) #decode json data
#     print(type(m_in))
#     print("broker 2 address = ",m_in["broker2"])


def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed to topic", mid)


def on_message(client, userdata, msg):
        global msgdir
        global msgdirstat
        global active_topics
        global seal_sm
        global networkexposure
        #print(msg)
        print(msg.topic)
        print(active_topics)
        if msg.topic == 'unique_network_flow':
            print("msg: ", msg)
            m_decode = str(msg.payload.decode("utf-8","ignore"))
            msgdir2 = json.loads(m_decode)
            print("event_type: ", msgdir2["event_type"])

            
            if msgdir2["event_type"]== msgdir2["ADDED"]: #ADDED
                # src, dst, hz, bw
                active_topics[msgdir2["topic"]] = (msgdir2["source"]["address"],msgdir2["source"]["port"], msgdir2["destination"]["address"], msgdir2["destination"]["port"], 1, 1)
                

            if msgdir2["event_type"] == msgdir2["REMOVED"]: #REMOVED
                try:
                    active_topics[msgdir2["topic"]].pop() 
                    if active_topics[msgdir2["topic"]] is None:
                        active_topics.pop(msgdir2["topic"])
                    # active_topics[msgdir["topic"]].pop(msgdir[destination])
                except KeyError:
                    pass
            print(active_topics)

        if msg.topic == 'unique_network_flow_stats':
            m_decode2 = str(msg.payload.decode("utf-8","ignore"))
            print("msg: ", msg)
            msgdirstat2 = json.loads(m_decode2)
            print("window_bandwidth: ",msgdirstat2["window_bandwidth"])

            print('I heard stats: "%s"' % msgdirstat2['topic'])
            #unique_flow_topic_relay.msg.UniqueTopicFlowStat(topic='/chatter', 
            # start=builtin_interfaces.msg.Time(sec=1664460164, nanosec=353911678), 
            # num_messages=6, num_bytes=144, window_duration_secs=4.999121933, 
            # window_bandwidth=28.805058554269916, window_rate=1.000175644245483, 
            # window_average_delta=0.9998243866000001)"
            
            

            #Was the topic published to the active topics
            if msgdirstat2['topic'] in active_topics:
                res = active_topics[msgdirstat2['topic']]

                #res = active_topics[msgdirstat2['topic']]
                #print("res: "+res)
                if res is not None:
                    print("res: ")
                    print(res)
                    print("window rate: " + str(msgdirstat2['window_rate']))
                    # srcaddress = res[0]
                    # srcport = res[1]
                    # dstaddress = res[2]
                    # dstport = res[3]
                    # current_rate = res[4]
                    # current_bw = res[5]
                    print(msgdirstat2['topic'])
                    srcaddress = active_topics[msgdirstat2['topic']][0]
                    srcport = active_topics[msgdirstat2['topic']][1]
                    dstaddress = active_topics[msgdirstat2['topic']][2]
                    dstport = active_topics[msgdirstat2['topic']][3]
                    current_rate = active_topics[msgdirstat2['topic']][4]

                    current_bw = universal_bw(msgdirstat2)


                    print("src: "+ str(srcaddress)+":"+str(srcport))
                    print("dst: "+ str(dstaddress)+":"+str(dstport))
                    print("current_rate: "+ str(current_rate))
                    print("current_bw: "+ str(current_bw))

                    #def update_NRM(self, topic):
                    # we received the bw measurement on the topic
                    # lehet h kellene vmi topic update, nem csak added meg deleted
                    #ret_hz, ret_bw = ((10, 9, 8, 7, 6), (20, 19, 18, 17, 16, 15))
                    #if ret_hz is None or ret_bw is None:
                    #    continue
                        
                    #pub_info_by_pub = self.get_publishers_info_by_topic(msgdirstat["topic"])
                    # just for testing
                    #pub_info_by_pub = self.get_publishers_info_by_topic("unique_topic_flow")
                    # for publisher in pub_info_by_pub:
                    qos = msg.qos
                    # print(pub_info)
                    #print(qos_profile)
                    print("reliability: " + str(qos))
                    ros2qos_parser = Ros2QoS_parser(qos)
                    qos_profile = ros2qos_parser.get_qos(qos)
                    PDB_Ros2, PELR_Ros2 = ros2qos_parser.parseQoS(qos_profile,current_rate)
                    #PDB_Ros2, PELR_Ros2 = 0 ,0 #retRos2QoS
                        
                    print("PDB_Ros2: "+ str(PDB_Ros2))
                    print("PELR_Ros2: "+ str(PELR_Ros2))
                    #print(*pub_info, sep = "| *** |")
                    qos_mapper = QoSmapper()
                    RT = None
                    PL = 2
                    #PDB = 80

                    # Resource Type (RT) (GBR/NON-GBR)
                    # Priority Level (PL)
                    # Packet Delay Budget (PDB)
                    # Packet Error Loss Rate (PELR)
                    # Maximum Data Burst Volume (MDBV)
                    # Data Rate Averaging Window (DRAW)
                    #rate, min_delta, max_delta, rate_std_dev, window = ret_hz
                    #PDB_measured = 1. /rate / 10e9
                    # calculate ms from Hz
                    PDB_measured = 1. / current_rate * 10e3
                    print("PDB_measured: "+ str(PDB_measured))
                    if PDB_measured > PDB_Ros2:
                        print("WARNING: ROS2 lifespan/MQTT keepalive setting is too low")
                    # ezt az erteket ki kellene talalni
                    
                    if abs(current_rate/msgdirstat2['window_rate']-1) < 0.1:
                        RT = "GBR"
                    else:
                        RT = "Non-GBR"
                    print("RT: "+ RT)

                    #bw, mean, min_s, max_s, mean_packet_size, max_burst_res = ret_bw
                    #MDBV = mean_packet_size
                    # DRAW-t honnan szivjam?
                    DRAW = 2000
                    # be lehetne allitani prioritast ket hasonlo topic kozott, es a PL-nek azt adni
                    # PL = ???

                    # a DRAW egyelore mindent 2000 ms-es window-ra szamit mindent
                    qos_mapper_result = qos_mapper.getQCI(RT, PL, PDB_measured, PELR_Ros2, current_bw, DRAW)

                    qci, example_service = qos_mapper_result
                    if qci is None:
                        qci = -1
                    if example_service is None:
                        example_service = "no proper service found"
                    print("QCI:" + str(qci))
                    print("Example service: " + example_service)
                        
                    #downlinkMaxBitRate: ROS2 flows are UDP unidirectional, in theory there is not even any signaling, or ACK packets there, but some minimal bw can be given
                    # ha az nagy sporoloas lenne, lehet h UNIDIRECTIONAL-lal is elmenne
                    uplinkMaxBitRate = max(current_bw, float((msgdirstat2["window_bandwidth"].split())[0]))
                    #max(current_bw, float(msgdirstat2["window_bandwidth"]))

                    sourceIPv4 = str(srcaddress[12]) + "." + str(srcaddress[13]) + "." + str(srcaddress[14]) + "." + str(srcaddress[15])
                    #sourceIPv4 = src["Addr"]
                    #sourcePort = src["Port"]
                    sourcePort = str(srcport)
                    destinationIPv4 = str(dstaddress[12]) + "." + str(dstaddress[13]) + "." + str(dstaddress[14]) + "." + str(dstaddress[15])
                    #destinationIPv4 = dst["Addr"]
                    destinationPort = str(dstport)
                    #destinationPort = dst["Port"]
                    #currently one initialization of the unicast resource is possible, if there is unicast patch and put calls then this could be done frequently
                    
                    #seal_sm = SEAL_state_machine('seal',networkexposure,'DOMAIN_ID_TEST')
                    #print("seal_sm.state: "+seal_sm.state)
                    
                    #if seal_sm.state == 'connection_in_group':
                    #    seal_sm.nrm_posted()

                    #ugly, the call should be in the state machine
                    downlinkMaxBitRate = 1000
                    networkexposure.NetworkResourceAdaptation(qci, uplinkMaxBitRate, downlinkMaxBitRate, destinationIPv4, destinationPort,sourceIPv4, sourcePort, "TCP", "directional")

                    active_topics[msgdirstat2["topic"]] = (srcaddress, srcport, dstaddress, dstport, msgdirstat2["window_rate"], msgdirstat2["window_bandwidth"])
                    print("\n\n")




def main(args=None):
    global seal_sm
    global networkexposure
    global ros2_domain_id
    client = paho.Client("Topic_Watcher")
    client.on_message = on_message
    client.on_subscribe = on_subscribe

    networkexposure.local_test = local_test
    qos_mapper = QoSmapper()

    PL = 2
    RT = "GBR"
    PDB_measured = 1. / 2 * 10e3
    PELR_Ros2 = 1e-6
    current_bw = 500
    DRAW = 2000
    qci, example_service= qos_mapper.getQCI(RT, PL, PDB_measured, PELR_Ros2, current_bw, DRAW)

    networkexposure.NetworkResourceAdaptation(qci, 10, 30, "127.0.0.1", 100, "127.0.0.1", 200, "TCP", "directional")
    #networkexposure.NetworkResourceAdaptation()
    #seal_sm = SEAL_state_machine("seal", networkexposure, ros2_domain_id)
    
    #seal = SEAL()
    client.connect(broker,port1)
    
    client.subscribe('unique_network_flow',1)
    client.subscribe('unique_network_flow_stats',1)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Received Keyboard interrupt. Exiting...")

if __name__ == '__main__':
    main()
