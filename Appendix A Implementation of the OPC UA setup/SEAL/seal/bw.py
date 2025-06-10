# © Ericsson AB 2024 - All Rights Reserved. No part of this software may be reproduced in any form without the written permission of the copyright owner.
# Distribution error
# No

# Disclaimer
# Controlled by agreement

# Change clause
# Controlled by agreement

#https://github.com/mqtt/mqtt.org/wiki/SYS-Topics

import paho.mqtt.client as paho
import time
import json
from numpy import uint64,float64

DEFAULT_WINDOW_SIZE = 100

bandwidth = [[-1] * DEFAULT_WINDOW_SIZE, [-1] * DEFAULT_WINDOW_SIZE]
#msg_bytes = [[[-1] * DEFAULT_WINDOW_SIZE], [[-1] * DEFAULT_WINDOW_SIZE]]
#msg_time = [-1] * DEFAULT_WINDOW_SIZE

broker="10.0.1.1"
broker="127.0.0.1"
port1=1883
i=0
hundred = False
timeresolution = 3
totalbytes = 0
last_time_stamp = 0


msgdirstat = {
    "topic" : str,
    "start" : float(0.0),
    "num_messages" : uint64,
    "num_bytes" : uint64,
    "window_duration_secs" : float64,
    "window_bandwidth" : float64,
    "window_rate" : float64,
    "window_avarage_delta" : float64,
    "min_s" : uint64,
    "max_s" : uint64,
    "mean" : float
}

def str_bytes(num_bytes):
    return f'{num_bytes:.0f} B'


def str_kilobytes(num_bytes):
    return f'{num_bytes/1000:.2f} KB'


def str_megabytes(num_bytes):
    return f'{num_bytes/1000/1000:.2f} MB'

def on_subscribe(client, userdata, mid, granted_qos):             #create function for callback
    print("subscribed to topic(s) \n")
    pass

def on_message(client, userdata, msg):  
    # The callback for when a PUBLISH message is received from the server. 
    # print(msg.payload)
    # print(len('Hello_qos'))
    # print(len(msg.payload))
    # print(msg.payload)
    global i
    global hundred
    global timeresolution
    global msgdirstat
    global totalbytes
    global last_time_stamp
    
    if userdata == 1:
        msgdirstat['start'] = time.perf_counter
        last_time_stamp = msgdirstat['start']
    #global bandwidth
    bandwidth[0][i] = len(msg.payload)
    bandwidth[1][i] = time.perf_counter()
    #bandwidth[1][i] = time.time() + time.perf_counter_ns()

    i+=1

    if i==DEFAULT_WINDOW_SIZE:
         hundred = True
         i=0

    if ((bandwidth[0][1] > -1) and (bandwidth[1][1] > -1)):
        # for j in range(len(bandwidth[0])):
        #       bw += bandwidth[0][j]
        #       time += bandwidth[1][j]
         tn = max(bandwidth[1])
         t0 = bandwidth[1][0]

         max_s = max(bandwidth[0])
         min_s = bandwidth[0][0]
         total = 0
         n = 0
         totalbytes = totalbytes + len(msg.payload)

        #n = len(self.times)
        #tn = self.clock.now()
        #t0 = self.times[0]
        #if tn <= t0:
        #   print('WARNING: time is reset!', file=sys.stderr)
        #   self.times = []
        #   self.sizes = []
        #   return None, None, None, None, Nonen 


         if hundred:
              t0 = min(bandwidth[1])
              min_s = min(bandwidth[0])
              n = DEFAULT_WINDOW_SIZE
              total = sum(bandwidth[0])
         else:
             for j in range(0,DEFAULT_WINDOW_SIZE):
                if bandwidth[0][j] > -1:
                     total += bandwidth[0][j]
                     if n < DEFAULT_WINDOW_SIZE:
                         n += 1
                if bandwidth[1][j] > -1 and bandwidth[1][j] < t0:
                     t0 = bandwidth[1][0]
                if bandwidth[0][j] <= -1 or bandwidth[1][j] <= -1:
                     break

         mean = total/n
         if ((tn - t0) >= timeresolution) and ((tn-last_time_stamp) >= timeresolution):
             bytes_per_s = total / (tn-t0)
             # min/max and even mean are likely to be much smaller,
             # but for now I prefer unit consistency
             bw_0 = bytes_per_s
             mean_0 = mean
             min_s_0 = min_s
             max_s_0 = max_s
             if bytes_per_s < 1000:
                 bw, mean, min_s, max_s = map(str_bytes, (bytes_per_s, mean, min_s, max_s))
             elif bytes_per_s < 1000000:
                 bw, mean, min_s, max_s = map(str_kilobytes, (bytes_per_s, mean, min_s, max_s))
             else:
                 bw, mean, min_s, max_s = map(str_megabytes, (bytes_per_s, mean, min_s, max_s))
             # Bandwidth is per second 
             bw += "/s"
             print("Bandwith: ",bytes_per_s," bytes/s")

             msgdirstat['num_messages'] = userdata
             msgdirstat['num_bytes'] = totalbytes
             msgdirstat['topic'] = msg.topic
             msgdirstat['window_avarage_delta'] = 1
            #  msgdirstat['window_bandwidth'] = bw_0
             msgdirstat['window_bandwidth'] = bw
             msgdirstat['window_duration_secs'] = tn-t0
             if hundred == False:
                msgdirstat['window_rate'] = i/(tn-t0)
             else:   
                msgdirstat['window_rate'] = 100/(tn-t0)
            #  msgdirstat['min_s'] = min_s_0
            #  msgdirstat['max_s'] = max_s_0
            #  msgdirstat['mean'] = mean_0
             msgdirstat['min_s'] = min_s
             msgdirstat['max_s'] = max_s
             msgdirstat['mean'] = mean
             dataout = json.dumps(msgdirstat,separators=(',', ':'))
             print(msgdirstat)
             last_time_stamp = tn
             client.publish('unique_network_flow_stats', dataout, 1)



client1= paho.Client("BW_TEST")                                     #create client object
client1.on_subscribe = on_subscribe                                 #assign function to run on subscribtion
client1.on_message = on_message                                     #assign function to run on message
client1.connect(broker,port1)                                       #connect to broker
client1.subscribe('topic1',1)                                       #subscribe
#client1.subscribe("unique_network_flow",1)                         #subscribe
#client1.subscribe("topic2",0)                                      #subscribe
client1.loop_forever()                                              #run client loop        ###stops at keyboard interrupt
