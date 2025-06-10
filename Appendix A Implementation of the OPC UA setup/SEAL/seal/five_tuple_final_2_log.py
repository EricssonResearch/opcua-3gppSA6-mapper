# © Ericsson AB 2024 - All Rights Reserved. No part of this software may be reproduced in any form without the written permission of the copyright owner.
# Distribution error
# No

# Disclaimer
# Controlled by agreement

# Change clause
# Controlled by agreement

import json
import paho.mqtt.client as paho
from socket import inet_aton
from struct import unpack
from filelock import FileLock
#from numpy import uint8,uint16

FIVE_TUPLE_CLIENT_ID = "UNF_SYS_TEST"
LOG_FILE = "/tmp/mosquitto.log"
broker_cloud="10.0.1.2"
broker_local_test_cloud="127.0.0.1"
broker = broker_local_test_cloud
broker = "127.0.0.1"
port3=8883 #port1 = 8881, port2 = 8882, port3 = 8883 #First two for connecting to mosquitto broker and port3 is for subscriptions
newdest = False
completesrc = False
completedst = False
connect = False
disconnect = False
stack = []
#number_sub = 0
#number_pub = 0
last_subscribe_not_end = False
dst_client_id = ""

UDPV4 = 1
UDPV6 = 2
TCPV4 = 3
TCPV6 = 4
UNICAST = 1
MULTICAST = 2

#ToDo: create dictiniary/hash to store 5-tuple
#Filling it up with some place holder data
addressdir = {
    "Src": {"Addr": '-1', "Port": '-1', "ClientID": "id"},
    "Dest": {"Addr": '-2', "Port": '-2', "ClientID": "id"},
    "Protocol" : "TCP",
    "ClientID": "id",
    "Topic" : str, #only in src/dest list
    "QoS": -1   #only in src/dest list
}
delete_addressdir = {
    "Src": {"Addr": '-1', "Port": '-1', "ClientID": "id"},
    "Dest": {"Addr": '-2', "Port": '-2', "ClientID": "id"},
    "Protocol" : "TCP",
    "ClientID": "id",
    "Topic" : str,
    "QoS": -1
}

Locator = {
    "UNICAST" : UNICAST,
    "MULTICAST": MULTICAST,
    "cast" : int(0),

    "UDPV4": UDPV4,
    "UDPV6": UDPV6,
    "TCPV4": TCPV4,
    "TCPV6": TCPV6,
    "kind": int(0),

    "address": [int(0)]*16,
    "port": int(0),
}
Locator2 = {
    "UNICAST" : UNICAST,
    "MULTICAST": MULTICAST,
    "cast" : int(0),

    "UDPV4": UDPV4,
    "UDPV6": UDPV6,
    "TCPV4": TCPV4,
    "TCPV6": TCPV6,
    "kind": int(0),

    "address": [int(0)]*16,
    "port": int(0),
}

msgdir = {
    "ADDED": int(1),
    "REMOVED": int(2),
    "event_type": int(0),
    "topic": str,
    "source": Locator,
    "destination": Locator2,
}

srclist = {}
destlist = {}


def five_tuple_new_or_delete(client,addressdir):
    global msgdir
    global connect
    global newdest

    if addressdir['Protocol'] == 'TCP':
            msgdir['source']['kind'] = msgdir['source']['TCPV4']
            msgdir['source']['cast'] = msgdir['source']['UNICAST']
            msgdir['destination']['kind'] = msgdir['source']['TCPV4']
            msgdir['destination']['cast'] = msgdir['source']['UNICAST']
    else:
            msgdir['source']['kind'] = msgdir['source']['UDPV4']
            msgdir['source']['cast'] = msgdir['source']['UNICAST']
            msgdir['destination']['kind'] = msgdir['source']['UDPV4']
            msgdir['destination']['cast'] = msgdir['source']['UNICAST']
    if connect:
            msgdir['event_type'] = msgdir['ADDED']
    else:
            msgdir['event_type'] = msgdir['REMOVED']

    #print(addressdir)
    msgdir["topic"] = addressdir["Topic"]
    #print(int(addressdir['Src']['Port']))
    msgdir['source']['address'][12:] = unpack('BBBB',inet_aton(addressdir['Src']['Addr']))#[0:3]
    msgdir['source']['port'] = int(addressdir['Src']['Port'])
    msgdir['destination']['address'][12:] = unpack('BBBB',inet_aton(addressdir['Dest']['Addr']))
    msgdir['destination']['port'] = int(addressdir['Dest']['Port'])
    #print(int(addressdir['Dest']['Port']))
    print(msgdir)
    data_out = json.dumps(msgdir,separators=(',', ':'))
    print(client.publish("unique_network_flow",data_out, 1))
    newdest = False


def on_subscribe(client, userdata, mid, granted_qos):             #create function for callback
    #print("subscribed to SYS topic\n")
    pass

def on_message(client, msg):  # The callback for when a PUBLISH message is received from the server. 
    #ToDo: Look for specific lines and get the IP:Port out of it
    #according to, which is the destination and which is the source

    global newdest
    global completedst
    global completesrc
    global connect
    global disconnect
    global addressdir
    global msgdir
    global stack
    global last_subscribe_not_end
    global dst_client_id
    

    #Find bridge and save its enpoint
    try:
        string = msg.payload.decode('utf-8')
    except:
        string = msg
    tmp1 = "New bridge connected from "
    tmp2 = "New connection from "
    tmp3 = "New client connected from"
    if (((tmp1 in string) or (tmp2 in string) or (tmp3 in string))) and (".b" in string)  :
    	if "Topic_Watcher" not in string:
                begin = string.find("as")+3
                end = string.find("(p")-1
                src_client_id = string[begin:end]
                srclist[src_client_id] = {}

                begin = string.find("from")+5
                end = string.find(":")
                srclist[src_client_id]["Addr"] = string[begin:end]

                begin = string.find(":")+1
                end = string.find(" .b")
                srclist[src_client_id]["Port"] = string[begin:end]

                begin = string.find(":")+1
                end = string.find(" as")
                srclist[src_client_id]["Port"] = string[begin:end]
                srclist[src_client_id]["Topics"] = {}
                print("\nsrclist New connection")
                print(srclist)
                #srclist[src_client_id]["Topics"] = {"topic":"topic1","qos":1}
                #print(string)


    #Connected Publisher fill in their topics
    tmp1 = "Received PUBLISH from "
    #print(string)
    if (tmp1 in string) and ("$SYS" not in string) and ("Topic_Watcher" not in string) and (FIVE_TUPLE_CLIENT_ID not in string):
        begin = string.find("from")+5
        end = string.find(" (d")
        src_client_id = string[begin:end]
        begin = string.find(", '")+3
        end = string.find("',")
        topic = string[begin:end]
        begin = string.find(", q")+3
        qos = int(string[begin])
        if src_client_id in srclist:
            if topic not in srclist[src_client_id]["Topics"]:
                srclist[src_client_id]["Topics"][topic] = qos
                print("\nsrclist")
                print(srclist)



    #Find Client and save its enpoint
    tmp1 = "New client connected from "  
    tmp2 = "Topic_Watcher"
    if (tmp1 in string) and (".b" not in string) and (".vissza" not in string) and (tmp2 not in string) and (FIVE_TUPLE_CLIENT_ID not in string):     
        if string.find(tmp2) != 1:
            newdest = True
            connect = True
            #print(string)

            begin = string.find(" as")+4
            end = string.find(" (p")
            #print(string[begin:end])
            if end == -1:
                pass
            else:
                client_id = string[begin:end]
                destlist[client_id] = {}
                begin = string.find("from ")+5
                end = string.find(":")
                #print("-"+client_id+"-")
                destlist[client_id]["Addr"] = string[begin:end]
                begin = string.find(":")+1
                end = string.find(" as")
                destlist[client_id]["Port"] = string[begin:end]
                destlist[client_id]["Topics"] = {}
                print("\ndestlist New connection")
                print(destlist)
                #destlist[client_id]["Topics"] = {"topic":"topic1","qos":1}
                #print("Addressdir (dst): \n",addressdir)
                #print(string)

    #print("####"+string)
    tmp1 = "Received SUBSCRIBE from "
    if (tmp1 in string):
        if (FIVE_TUPLE_CLIENT_ID not in string) and ("Topic_Watcher" not in string):
            begin = string.find("from")+5
            end = len(string)-1
            dst_client_id = string[begin:end]            
            # if dst_client_id in destlist:
            #     print(string)
            #     print(dst_client_id)
            last_subscribe_not_end = True

    tmp1 = "Sending SUBACK to "
    if (tmp1 in string) and (FIVE_TUPLE_CLIENT_ID not in string) and ("Topic_Watcher" not in string):
        begin = string.find("to")+3
        end = len(string)-1
        dst_client_id = ""
        last_subscribe_not_end = False
    #print("+"+dst_client_id+"+")
    



    if (last_subscribe_not_end):
        if(string[0:(len(dst_client_id))] == dst_client_id): #and ("Topic_Watcher" not in string):
            #print(destlist)
            begin = len(dst_client_id) + 3
            #begin = string.find(" ") + 3
            end = len(string)-1
            topic = string[begin:end]
            #print(topic)
            if dst_client_id in destlist:
                if topic not in destlist[dst_client_id]["Topics"]:
                    qos = int(string[begin-2])
                    destlist[dst_client_id]["Topics"][topic] = qos
                    print("\ndestlist")
                    print(destlist)

    

    tmp1 = "Client "
    #Client disconnect1
    tmp2 = " closed its connection."
    #Client disconnect2
    tmp3 = " disconnected."
    if tmp1 in string and (tmp2 in string or tmp3 in string) and ("Topic_Watcher" not in string) and (FIVE_TUPLE_CLIENT_ID not in string) and (".vissza" not in string):
            newdest = True
            connect = False
            # Not good, has to be changed
            begin = len(tmp1)
            if tmp2 in string:
                end = string.find(tmp2)
            else:
                end = string.find(tmp3)
                
            client_id = string[begin:end]
            #print(client_id)

            #Exiting client is the publisher, terminating every 5-tuple flow that has the publisher and one of it's topics
            if client_id in srclist:
                delete_addressdir["Src"]["Addr"] = srclist[client_id]["Addr"]
                delete_addressdir["Src"]["Port"] = srclist[client_id]["Port"]
                delete_addressdir["Protocol"] = "TCP"
                for dest_client_id in destlist:
                    for dest_topic in destlist[dest_client_id]["Topics"]:
                        if (dest_topic in srclist[client_id]["Topics"]):
                            delete_addressdir["Dest"]["Addr"] = destlist[dest_client_id]["Addr"]
                            delete_addressdir["Dest"]["Port"] = destlist[dest_client_id]["Port"]
                            delete_addressdir["Topic"] = dest_topic
                            delete_addressdir["QoS"] = destlist[dest_client_id]["Topics"][dest_topic]
                            if str(delete_addressdir) in stack:
                                connect = False
                                completedst = True
                                completesrc = True
                                newdest = True
                                five_tuple_new_or_delete(client,delete_addressdir)
                                stack.remove(str(delete_addressdir))
                #Deleting from srclist
                if client_id in srclist:
                    srclist.pop(client_id)

            #Exiting client is the subscriber, terminating every 5-tuple flow related
            elif client_id in destlist:
                delete_addressdir["Dest"]["Addr"] = destlist[client_id]["Addr"]
                delete_addressdir["Dest"]["Port"] = destlist[client_id]["Port"]
                delete_addressdir["Protocol"] = "TCP"
                for src_client_id in srclist:
                    for src_topic in srclist[src_client_id]["Topics"]:
                        if (src_topic in destlist[client_id]["Topics"]):
                                delete_addressdir["Src"]["Addr"] = srclist[src_client_id]["Addr"]
                                delete_addressdir["Src"]["Port"] = srclist[src_client_id]["Port"]
                                delete_addressdir["Topic"] = src_topic
                                delete_addressdir["QoS"] = srclist[src_client_id]["Topics"][src_topic]
                                delete_addressdir["Protocol"] = "TCP"

                                if str(delete_addressdir) in stack:
                                    connect = False
                                    completedst = True
                                    completesrc = True
                                    newdest = True
                                    five_tuple_new_or_delete(client,delete_addressdir)
                                    stack.remove(str(delete_addressdir))
                #Deleting from destlist
                if client_id in destlist:
                    destlist.pop(client_id)
            else:
                 print("Disconnected %s wasn't in either srclist or destlist",client_id)
    

    #Check for new connections, that are not in stack
    for src_client_id in srclist:
         if (srclist[src_client_id]["Topics"] != {}):
            for dest_client_id in destlist:        
                 if (destlist[dest_client_id]["Topics"] != {}):
                      
                      for src_topic in srclist[src_client_id]["Topics"]:
                           for dest_topic in destlist[dest_client_id]["Topics"]:
                                if (src_topic == dest_topic):
                                    addressdir["Src"]["Addr"] = srclist[src_client_id]["Addr"]
                                    addressdir["Src"]["Port"] = srclist[src_client_id]["Port"]
                                    addressdir["Dest"]["Addr"] = destlist[dest_client_id]["Addr"]
                                    addressdir["Dest"]["Port"] = destlist[dest_client_id]["Port"]
                                    addressdir["Topic"] = src_topic
                                    #addressdir["Topic"] = destlist[dest_client_id]["Topics"][src_topic]
                                    #print(dest_topic)
                                    addressdir["QoS"] = destlist[dest_client_id]["Topics"][src_topic]
                                    addressdir["Protocol"] = "TCP"
                                     
                                    if str(addressdir) not in stack:
                                        connect = True
                                        completedst = True
                                        completesrc = True
                                        newdest = True
                                    else:
                                        newdest = False

                                    if addressdir['Dest']['Addr'] != '-2' and addressdir['Dest']['Port'] != '-2':
                                        completedst = True
                                    else:
                                        completedst = False

                                    if addressdir['Src']['Addr'] != '-1' and addressdir['Src']['Port'] != '-1':
                                        completesrc = True
                                    else:
                                        completesrc = False

                                    #print(completedst,completesrc,newdest)
                                    #print(addressdir)
                                    #Check whether 5-tuple is complete   
                                    #YES? Send it to TOPIC WATCHER... (for later) (Completed)
                                    if completesrc and completedst and newdest and connect:
                                        stack.append(str(addressdir))
                                        five_tuple_new_or_delete(client,addressdir)



def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker 
    #print("Connected with result code {0}".format(str(rc)))
    print("\nConnected with result code "+ str(rc)+"\n")  




client1= paho.Client(FIVE_TUPLE_CLIENT_ID)                           #create client object
#client1.on_subscribe = on_subscribe                          #assign function to callback #Subscribe won't be happening
#client1.on_message = on_message
client1.on_connect = on_connect


client1.connect(broker,port3)                                 #establish connection
####   Unused because of the usage of log file
#client1.subscribe("topic1",0)                                      #subscribe
#client1.subscribe("topic2",0)                                      #subscribe

open_success = False
try:
     log = open(LOG_FILE,mode="r")
     open_success=True
     log.close()
except :     
     print("No such file as: ",LOG_FILE)

if open_success:
    try:
        while True:
            #Open log file to read a line
            with open(LOG_FILE, 'r') as log:
                #read lines
                log_lines = log.readlines()

                #Delete read lines
                with open(LOG_FILE, 'w') as log_delete:
                    test = log.readline()
                    #print("Test: '" + test+"'")
                    
                    #Only if there is no new line
                    if len(test) == 0:
                        log_delete.write("")
                    else:
                        new_lines = log.readlines()
                        log_delete.write(test)
                        log_delete.writelines(new_lines)
                    

            #if line is not last or empty then process it
            for log_line in log_lines:
                #It is advised to save the srclist, destlist and stack 
                # to be used on restart after crash
                on_message(client1,log_line)
                    

               
                                    
    except KeyboardInterrupt:
        print("Exiting becausese of Ctrl-C...\n")
        log.close()
