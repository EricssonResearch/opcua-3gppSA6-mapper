import socket
import sys
import os
from connexion import AsyncApp, ConnexionMiddleware, request, App, request
from connexion.resolver import RelativeResolver
from connexion.context import context 
from pathlib import Path
from secrets import choice
import string
import random
from math import radians, sin, cos, acos
from geopy.distance import geodesic as GD

import time
import datetime
import connexion
from connexion.lifecycle import ConnexionResponse
from threading import Timer
import json
import mysql.connector

#vi /var/lib/mysql/mysql-init-password ALTER USER 'admin'@'localhost' IDENTIFIED BY 'Admin1Pass'
#sudo chmod 400 /var/lib/mysql/mysql-init-passwords
#sudo chown mysql:mysql /var/lib/mysql/mysql-init-password

MAXIMUM_SUB_ID = 18
MINIMUM_SUB_ID = MAXIMUM_SUB_ID - 4
SUB_REQ_MAX_LENGHT = 10002
MAXIMUM_VALGROUP = 20
MINIMUM_VALGROUP = MAXIMUM_VALGROUP -4
VALGORUP_MAX_LENGTH = 8112
MAXIMUM_LOCATION_ID = 20
MINIMUM_LOCATION_ID = MAXIMUM_LOCATION_ID-4
LOCATION_MAX_LENGTH = 8025

DATABASE_NAME = "NetworkResourceDB_mn"
TABLENAME = "subscriptions_mn"
TABLE_GROUPMANAGEMENT = "GroupManagement_mn"
TABLE_LOCATION = "LocationManagement_mn"

########################################################
#Data requested or written to DATABASE - Locally stored version for faster request handling
subs_database = {}
group_database = {} #For setting VLAN and other settings for groups of devices
vlan_group_connection = {}
loc_rep_database = {}
valuser_current_loc_database = {} #For storing reported locations of valUsers registered at LocationReporting


########################################################
enodeB_database = []
##Hard coding a few values for testing delay setting through location
#Budapest
enodeB_database.append({"mcc": 216, "mnc": 30, "region": 12007, "cellid": 91402, "enodeBId": 357, "lat": 47.472333, "lon": 19.063968}) #eNB id: 165 (hex), 357
enodeB_database.append({"mcc": 216, "mnc": 30, "region": 12007, "cellid": 91399, "enodeBId": 357, "lat": 47.471039, "lon": 19.062555}) #eNB id: 165 (hex), 357
enodeB_database.append({"mcc": 216, "mnc": 30, "region": 12007, "cellid": 1240838, "enodeBId": 4847, "lat": 47.472153, "lon": 19.059677}) #eNB id: 12ef (hex), 4847
enodeB_database.append({"mcc": 216, "mnc": 30, "region": 12007, "cellid": 114945, "enodeBId": 449, "lat": 47.469061, "lon": 19.061516}) #eNB id: 1c1 (hex), 449
enodeB_database.append({"mcc": 216, "mnc": 30, "region": 12007, "cellid": 850436, "enodeBId": 3322, "lat": 47.469081, "lon": 19.075587}) #eNB id: cfa (hex), 3322
enodeB_database.append({"mcc": 216, "mnc": 30, "region": 12007, "cellid": 1288198, "enodeBId": 5032, "lat": 47.475604, "lon": 19.059576}) #eNB id: 13a8 (hex), 5032
enodeB_database.append({"mcc": 216, "mnc": 30, "region": 12007, "cellid": 133639, "enodeBId": 522, "lat": 47.478488, "lon": 19.055594}) #eNB id: 20a (hex), 522
enodeB_database.append({"mcc": 216, "mnc": 30, "region": 12008, "cellid": 80641, "enodeBId": 315, "lat": 47.50997, "lon": 19.063136}) #eNB id: 13b (13b), 315
enodeB_database.append({"mcc": 216, "mnc": 30, "region": 12009, "cellid": 96009, "enodeBId": 315, "lat": 47.463721, "lon": 19.14976}) #eNB id: 13b (hex), 315
enodeB_database.append({"mcc": 216, "mnc": 30, "region": 12013, "cellid": 134152, "enodeBId": 524, "lat": 47.432083, "lon": 19.07148}) #eNB id: 20c (hex), 524
#Nyiregyhaza
enodeB_database.append({"mcc": 216, "mnc": 30, "region": 30652, "cellid": 785667, "enodeBId": 3069, "lat": 47.954348, "lon": 21.673059}) #eNB id: bfd (hex), 3069
#Szeged
enodeB_database.append({"mcc": 216, "mnc": 30, "region": 31431, "cellid": 326150, "enodeBId": 1274, "lat": 46.251634, "lon": 20.141578}) #eNB id: 4fa (hex), 1274
enodeB_database.append({"mcc": 216, "mnc": 30, "region": 31431, "cellid": 325638, "enodeBId": 1272, "lat": 46.261432, "lon": 20.137679}) #eNB id: 4f8 (hex), 1272
#Pecs
enodeB_database.append({"mcc": 216, "mnc": 30, "region": 3250, "cellid": 286729, "enodeBId": 1120, "lat": 46.073234, "lon": 18.222894}) #eNB id: 460 (hex), 1120
enodeB_database.append({"mcc": 216, "mnc": 30, "region": 3250, "cellid": 292358, "enodeBId": 1142, "lat": 46.074749, "lon": 18.203436}) #eNB id: 476 (hex), 1142


#########################################################
#DATABASE CONNECTION: CREATE Database, Tables if necessary
db = None
cursor = None
try :
    db = mysql.connector.connect(
        #unix_socket = "/var/run/mysqld/mysqld.sock",
        host="10.123.123.1",
        # host="127.0.0.1",
        port="3306",
        user="admin",
        password="Admin1Pass",
        database=DATABASE_NAME,
        auth_plugin='mysql_native_password'
    )
    cursor = db.cursor(buffered=True)
except:
    #Database doesn't exist
    db = mysql.connector.connect(
        # unix_socket = "/var/run/mysqld/mysqld.sock",
        host="10.123.123.1",
        # host="127.0.0.1",
        port="3306",
        user="admin",
        password="Admin1Pass",
        auth_plugin='mysql_native_password'
    )
    #Creating database
    print(f"Creating Database: {DATABASE_NAME}")
    cursor = db.cursor(buffered=True)
    cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(DATABASE_NAME))
    db.database = DATABASE_NAME



sql2 = "SHOW TABLES;"
cursor.execute(sql2)
tables = cursor.fetchall()
print(tables)

subs = False
groups = False
locations = False

subs = False
groups = False
locations = False
decoded = False


#Empty database, then create tables     
if (not tables):
    cursor.execute("CREATE TABLE %s (address VARCHAR(%d), subscriptionRequest VARCHAR(%d), subType VARCHAR(60))" % (TABLENAME, MAXIMUM_SUB_ID,SUB_REQ_MAX_LENGHT))
    cursor.execute("CREATE TABLE %s (address VARCHAR(%d), valGroupId VARCHAR(60), groupDocsRequest VARCHAR(%d), subType VARCHAR(60))" % (TABLE_GROUPMANAGEMENT, MAXIMUM_VALGROUP,VALGORUP_MAX_LENGTH))
    cursor.execute("CREATE TABLE %s (address VARCHAR(%d), locationReportingRequest VARCHAR(%d), subType VARCHAR(60))" % (TABLE_LOCATION, MAXIMUM_LOCATION_ID, LOCATION_MAX_LENGTH))
else:
    #Check if some of the tables are missing
    try:
        #If code is run by sudo or in mininet
        tables = [x[0].decode('utf-8') for x in tables]
        decoded = True
    except (UnicodeDecodeError, AttributeError):
        #If bytearray -> string conversion error, than it is string, so let it pass
        pass

    for x in tables:
        if (TABLENAME in x):
            subs = True
        elif (TABLE_GROUPMANAGEMENT in x):
            groups = True
        elif (TABLE_LOCATION in x):
            locations = True
    
    #Create if the 
    if (not subs):
        cursor.execute("CREATE TABLE %s (address VARCHAR(%d), subscriptionRequest VARCHAR(%d), subType VARCHAR(60))" % (TABLENAME, MAXIMUM_SUB_ID,SUB_REQ_MAX_LENGHT))
    if (not groups):
        cursor.execute("CREATE TABLE %s (address VARCHAR(%d), valGroupId VARCHAR(60), groupDocsRequest VARCHAR(%d), subType VARCHAR(60))" % (TABLE_GROUPMANAGEMENT, MAXIMUM_VALGROUP,VALGORUP_MAX_LENGTH))
    if (not locations):
        cursor.execute("CREATE TABLE %s (address VARCHAR(%d), locationReportingRequest VARCHAR(%d), subType VARCHAR(60))" % (TABLE_LOCATION, MAXIMUM_LOCATION_ID, LOCATION_MAX_LENGTH))
#########################################################
# cursor.execute("SELECT * FROM ")
#########################################################
#Get IP address:port and define socket path, accepted TOKEN 
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
AppPort = 7777

hostname = '10.1.2.50'
# hostname = '0.0.0.0'
# hostname = '192.168.100.50'
# hostname = '127.0.0.1'

# Define the path for the Unix socket
socket_path = '/tmp/mininet_control2.s'
socket_recv_path = '/tmp/mininet_resp.s'
# socket_path = '/tmp/mininet_control3.s'
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImZvbyIsInBhc3N3b3JkIjoiYmFyIiwiaWF0IjoxNjY4MDg0NDI1fQ.lT4ABOQSHyJdIiF9rso06qcwrBkIxRFyolIgdBAI4l0"
PASSWD = {"admin": "secret", "foo": "bar"}
#########################################################


#### Create a Unix socket
client_socket = None
client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) #For Mininet
# client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) #For mininet_unix_server_sim2.py
#### Wait till socket is up
while (True):
    try:    
        client_socket.connect(socket_path)
        client_socket.settimeout(1)
        print('Connected to Mininet controller')
        break
    except:
        time.sleep(3)
        print("Problem with connecting to the server")


#To receive response
if os.path.exists(socket_recv_path):
      os.remove(socket_recv_path)
client_socket.bind(socket_recv_path)
os.chmod(socket_recv_path, 0o777)




#Sending commands to mininet controller - socket stream
def socket_send_sock_stream(request):
    global client_socket
    # delay = 0.0
    # bw = 0.0
    # vlan = 0

    if (client_socket is None):
        print(client_socket)
        print((client_socket is None))
        try:    
            client_socket.connect(socket_path)
            client_socket.settimeout(1)
        except:
            print("Problem with connecting to the server")
    
    if (client_socket is not None):
        try:
            #TODO: find what we want to change (check if it is not corrupted)
            if (request['min_con'] == "delay"):
                msg = "L8 delay {}\n".format(request['delay'])
                if ((isinstance(request['delay'], float) == False)):
                    if (isinstance(request['delay'], int) == False):
                        print("Invalid type")
                        return -300
                    else:
                        request['delay'] = float(request['delay'])
                print("L8 delay %f ms" %request['delay'])
                client_socket.send(msg.encode("utf-8"))
                data = client_socket.recv(4096)
                if (data):
                    print(data)
                    return 200
                


            elif request['min_con'] == "bandwidth" :
                msg = "L8 bandwidth {}\n".format(request['bw'])
                if ((isinstance(request['bw'], float) == False)):
                    if (isinstance(request['bw'], int) == False):
                        print("Invalid type")
                        return -300
                    else:
                        request['bw'] = float(request['bw'])
                print("L8 bandwidth %f" %request['bw'])
                print(request['flowID'])
                print(str(request['flowID']))
                print(str(request['flowID']).encode('utf-8'))
                print((msg.encode('utf-8')))
                print((msg.encode("utf-8"),str(request['flowID']).encode("utf-8")))
                client_socket.send((msg.encode('utf-8')))
                # client_socket.send((msg.encode("utf-8"),str(request['flowID']).encode("utf-8")))
                # client_socket.send(request['flowID'].encode("utf-8"))
                data = client_socket.recv(4096)
                if (data):
                    print(data)
                    return 200
                


            elif request['min_con'] == "group0" :
                msg = "publisher vlan {}\n".format(request['vlan'])
                if ((isinstance(request['vlan'], int) == False)):  
                    print("Invalid type")
                    return -300
                print("H1 new vlan %d" %request['vlan'])
                client_socket.send(msg.encode("utf-8"))
                data = client_socket.recv(4096)
                if (data):
                    print(data)
                    return 200
                
            else:
                print("Invalid/unsupported request: {}".format(request))
                return -1
            
            return -2
        
        except Exception as e:
            print(f"Socket Error: {e}")
            return -2
    else:
        print("client_socket failed to create connection")
        return -2





#Sending commands to mininet controller - socket datagramm
def socket_send(request):
    global client_socket, socket_path
    # delay = 0.0
    # bw = 0.0
    # vlan = 0

    try:
        #TODO: find what we want to change (check if it is not corrupted)
        if (request['min_con'] == "delay"):
            msg = "L8 delay {}\n".format(request['delay'])
            # msg = "L8 delay {} {}\n".format(request['delay'], request['delay_ext'])
            if (isinstance(request["delay"], float) == False):
                if ((isinstance(request["delay"], int) == False)):
                    print("Invalid type")
                    return -300
                else:
                    request['delay'] = round(float(request['delay']), 3)

            print(f"L8 delay {request['delay']}{request['delay_ext']}")
            message = request
            message['command'] = msg
            print(message)
            # client_socket.sendto( json.dumps(message, indent=4, separators=(',', ': ')).encode('utf-8'), socket_path )
            client_socket.sendto( json.dumps(message, indent=4, separators=(',', ': ')).encode("utf-8"), socket_path  )
            data,address = client_socket.recvfrom(4096)
            if (data):
                print(data)
                return 200
            


        elif request['min_con'] == "bandwidth" :
            msg = "L8 bandwidth {}\n".format(request['bw'])
            if ((isinstance(request['bw'], float) == False)):
                if (isinstance(request['bw'], int) == False):
                    print("Invalid type")
                    return -300
                else:
                    request['bw'] = float(request['bw'])
            print("L8 bandwidth %f" %request['bw'])
            message = request
            message['command'] = msg
            # print(json.dumps(message, indent=2).encode('utf-8'))
            print(json.dumps(message, indent=4, separators=(',', ': ')).encode('utf-8'))
            # client_socket.send( msg.encode("utf-8"), socket_path  )
            client_socket.sendto( json.dumps(message, indent=4, separators=(',', ': ')).encode('utf-8'), socket_path )
            data,address = client_socket.recvfrom(4096)
            if (data):
                print(data,address)
                return 200
            return 200
            


        elif request['min_con'] == "group0" :
            msg = "publisher vlan {}\n".format(request['vlan'])
            if ((isinstance(request['vlan'], int) == False)):  
                print("Invalid type")
                return -300
            print("H1 new vlan %d" %request['vlan'])
            message = request
            message['command'] = msg
            # client_socket.sendto( json.dumps(message, indent=4, separators=(',', ': ')).encode('utf-8'), socket_path )
            client_socket.sendto( msg.encode("utf-8"), socket_path )
            data,address = client_socket.recvfrom(4096)
            if (data):
                print(data)
                return 200


        else:
            print("Invalid/unsupported request: {}".format(request))
            return -1
        
        return -2 
    except Exception as e:
        print(f"Socket Error: {e}")
        print("client_socket failed to create connection")
        return -2

        


def socket_send_delay(delay):
    global client_socket

    if (client_socket is not None):
        try:
            msg = "L8 delay {}ms".format(delay)
            client_socket.sendall(msg.encode())
            print("L8 delay %fms" %delay)
        except Exception as e:
            print(f"Socket Error: {e}")
        finally:
            try:
                client_socket.listen(1)
                datagram = client_socket.recv(1024)
                if datagram:
                    print(datagram.strip().split())
            except Exception as error:
                print(f"Error during reading socket: {error}")
    else:
        print("client_socket failed to create connection")

def socket_send_bandwidth(bw):
    global client_socket
    if (client_socket is not None):
        try:
            msg = "L8 bandwidth {}mbps".format(bw)
            client_socket.sendall(msg.encode())
            print("L8 bandwidth %fmb/s" %bw)
        except Exception as e:
            print(f"Socket Error: {e}")
        finally:
            try:
                client_socket.listen(1)
                datagram = client_socket.recv(1024)
                if datagram:
                    print(datagram.strip().split())
            except Exception as error:
                print(f"Error during reading socket: {error}")
    else:
        print("client_socket failed to create connection")

def socket_send_vlan(vlan):
    global client_socket
    if (client_socket is not None):
        try:
            msg = "H1 vlan {}".format(vlan)
            client_socket.sendall(msg.encode())
            print("H1 new vlan %d" %vlan)
        except Exception as e:
            print(f"Socket Error: {e}")
        finally:
            try:
                client_socket.listen(1)
                datagram = client_socket.recv(1024)
                if datagram:
                    print(datagram.strip().split())
            except Exception as error:
                print(f"Error during reading socket: {error}")
    else:
        print("client_socket failed to create connection")



####Calculate sphere surface distance from coordinates
def calculate_gps_dist_for_small_range(poz1, poz2):
    if ("lat" not in poz1 or "lon" not in poz1):
        print("Poz1 not parsed correctly")
        return -1
    elif ("lat" not in poz2 or "lon" not in poz2):
        print("Poz2 not parsed correctly")
        return -1
    elif ((poz1['lat'] < -90 or poz1['lat'] > 90) or (poz1['lon'] < -180 or poz1['lon'] > 180)):
        print("Poz1 invalid value")
        return -1
    elif ((poz2['lat'] < -90 or poz2['lat'] > 90) or (poz2['lon'] < -180 or poz2['lon'] > 180)):
        print("Poz2 invalid value")
        return -1
    
    f_lat = radians(float(poz1['lat']))
    f_lon = radians(float(poz1['lon']))
    s_lat = radians(float(poz2['lat']))
    s_lon = radians(float(poz2['lon']))

    print("Distance (m):", 6371.01 * acos(sin(f_lat)*sin(s_lat) + cos(f_lat)*cos(s_lat)*cos(f_lon - s_lon)))

    return 6371.01 * acos(sin(f_lat)*sin(s_lat) + cos(f_lat)*cos(s_lat)*cos(f_lon - s_lon))

####Calculate Geo distance from coordinates
def calculate_gps_dist_for_larger_range(poz1, poz2):
    if ("lat" not in poz1 or "lon" not in poz1):
        print("Poz1 not parsed correctly")
        return -1
    elif ("lat" not in poz2 or "lon" not in poz2):
        print("Poz2 not parsed correctly")
        return -1
    elif ((poz1['lat'] < -90 or poz1['lat'] > 90) or (poz1['lon'] < -180 or poz1['lon'] > 180)):
        print("Poz1 invalid or out of range value")
        return -1
    elif ((poz2['lat'] < -90 or poz2['lat'] > 90) or (poz2['lon'] < -180 or poz2['lon'] > 180)):
        print("Poz2 invalid or out of range value")
        return -1
    
    print("Distance (km):", GD((poz1['lat'],poz1['lon']),(poz2['lat'],poz2['lon'])).km)

    return GD((poz1['lat'],poz1['lon']),(poz2['lat'],poz2['lon'])).km

####Get coordinates from cell_id
def cellid_to_gps(enb_id):
    global enodeB_database
    pozlat = -100
    pozlon = -200

    # if enb_id.mcc != 216:
    #     print("Wrong MCC")
    #     return -1
    
    # if enb_id.mnc != 30:
    #     print("Not supported carrier")
    #     return -2
    
    # if enb_id.region not in enodeB_database:
    #     print("Unknown Region")
    #     return -3

    for base in enodeB_database:
        if base['cellid'] == enb_id['cellid']:
            pozlat = base['lat']
            pozlon = base['lon']
            break
    
    if (pozlat < -90 or pozlon < -180):
        print("No data on cellid: \n{enb_id}")
        return -4

    return {"lat": pozlat, "lon": pozlon}

####Get coordinates form enb_id - First enb_id matching is used
def enodeb_to_gps(enb_id):
    global enodeB_database
    pozlat = -100
    pozlon = -200

    for base in enodeB_database:
        if base['enodeBId'] == enb_id['enodeBId']:
            pozlat = base['lat']
            pozlon = base['lon']
            break
    
    if (pozlat < -90 or pozlon < -180):
        print("No data on cellid: \n{enb_id}")
        return -4

    return {"lat": pozlat, "lon": pozlon}


####Calculate delay based on distance
def distance_delay (distance: float, metric: string):
    delay = 0.0

    if (metric == "meter"):
        if (distance <= 1000):
            delay = 2.0
        elif (distance <= 5000):
            delay = 5.0
        else:
            delay = 5.0 + 1 * (distance - 5000)/1000/50

    elif (metric == "kilometer"):
        if (distance <= 1):
            delay = 2.0
        elif (distance <= 5):
            delay = 5.0
        else:
            delay = 5.0 + 1 * (distance - 5)/(50)

    elif (metric == "miles"):
        if (distance <= 1/1.609):
            delay = 2.0
        elif (distance <= 5/1.609):
            delay = 5.0
        else:
            delay = 5.0 + 1 * (distance - 5/1.609)/(50/1.69)

    else:
        print("Wrong metric")
        return -1

    return delay


####Turn all BW into MB
def bw_round_2_dec(string):
    speed, level  = string.strip().split(" ")
    print(speed, level)
    if type(speed) is str:
        speed = float(speed)
        # print(speed)

    level = level.lower()


    if level == "bit/s" or level == "Bit/s":
        if speed >= 1000*1000:
            speed = round(speed/1000/1000, 2)
            level = "mbit"
            # print(f"{speed} {level}")
            return speed, level
        elif speed >= 1000:
            speed = round(speed/1000, 2)
            level = "kbit"
            # print(f"{speed} {level}")
            return speed, level
        else:
            speed = round(speed, 2)
            level = "bit"
            # print(f"{speed} {level}")
            return speed, level
    elif level == "kbit/s" or level == "Kbit/s":
        if speed >= 1000:
            speed = round(speed/1000, 2)
            level = "mbit"
            # print(f"{speed} {level}")
            return speed, level
        else:
            speed = round(speed, 2)
            level = "kbit"
            # print(f"{speed} {level}")
            return speed, level
    elif level == "mbit/s" or level == "Mbit/s":
        speed = round(speed, 2)
        level = "mbit"
        # print(f"{speed} {level}")
        return speed, level
    
    else:
        if level == "B/s" or level == "b/s":
            if speed >= 1000000:
                speed = round((speed/1024/1024), 2)
                level = "mbit"
                return speed*8, level
            elif speed >= 1000:
                speed = round(speed/1024, 2)
                level = "kbit"
                return speed, level
            else:
                speed = round(speed, 2)
                level = "bit"
                return speed, level
            
        elif level == "KB/S" or level == "KB/s" or level == "kb/s" or level == "kB/s":
            if speed >= 1000:
                speed = round(speed/1024, 2)
                level = "mbit"
            else:
                speed = round(speed, 2)
                level = "kbit"
        
        elif level == "MB/S" or level == "MB/s" or level == "mb/s" or level == "mB/s":
            speed = round(speed, 2)
            level = "mbit"

        else:
            speed = round(speed, 2)
            level = "mbit"


        # print(f"{speed} {level} (byte)")
        # print(f"{speed*8} {level}")
        return speed*8, level


def bw_adder(ul, ul_type, dl, dl_type):
    bw_ext = None
    if ul_type == "mbit" or dl_type == "mbit":
        bw_ext = "mbit"
        if ul_type != "mbit":
            if ul_type == "kbit":
                ul = ul / 1024
            else:
                ul = ul / 1024 / 1024
        elif dl_type != "mbit":
            if dl_type == "kbit":
                dl = dl / 1024
            else:
                dl = dl / 1024 / 1024

    elif ul_type == "kbit" or dl_type == "kbit":
        bw_ext = "kbit"
        if ul_type != "kbit":
                ul = ul / 1024
        else:
                dl = dl / 1024

    else:
        bw_ext = "bit"

    return round((ul + dl), 4), bw_ext






#GroupManagement block
def CreateValGroupDoc(body):
    global cursor, db, group_database
    codes = [201, 400, 401, 404, 411, 429, 500, 503]
    start = time.time() * 1000
    subtype = "group-management"

    #print(body)
    print(body['valGroupId'])
    try:
        auth_token = request.headers['authorization'].split(" ")[1]
        #location = kwargs.get("request").headers['Location']
        #body = kwargs.get("body")
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}
    
    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        headers = {"Authorization":auth_token}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )
    
    accepted = time.time()

    response_data = {
                # "Location":"",
                # "valGroupId": "",
                # "grpDesc": "grpDesc",
                # "members": [],
                # "valGrpConf": "",
                # "valServiceIds": [],
                # "valSvcInf": "string",
                # "suppFeat": "FFFF",
                # "resUri": "https://"+IPAddr+":"+str(AppPort)+"/ss-gm/v1/group-documents/",
                # "locInfo":"",
                # "addLocInfo":"",
                # "extGrpId":"",
                # "com5GLanType":"",
                }
    if ("valGroupId" in body):
        response_data['valGroupId'] = body['valGroupId']
    if ("valGrpConf" in body):
        response_data['valGrpConf'] = body['valGrpConf']
    if ("valServiceIds" in body):
        response_data['valServiceIds'] = body['valServiceIds']
    if ("members" in body):
        response_data['members'] = body['members']
    if ("suppFeat" in body):
        response_data['suppFeat'] = body['suppFeat']
    if ("grpDesc" in body):
        response_data['grpDesc'] = body['grpDesc']
    # if ("deviceID" in body):
    #     response_data['deviceID'] = body['deviceID']
    if ("locInfo" in body):
        response_data['locInfo'] = body['locInfo']
    if ("addLocInfo" in body):
        response_data['addLocInfo'] = body['addLocInfo']
    if ("extGrpId" in body):
        response_data['extGrpId'] = body['extGrpId']
    if ("com5GLanType" in body):
        response_data['com5GLanType'] = body['com5GLanType']
    if ("valSvcInf" in body):
        response_data['valSvcInf'] = body['valSvcInf']
    if ("resUri" in body):
        response_data['resUri'] = "https://"+IPAddr+":"+str(AppPort)+"/ss-gm/v1/group-documents/"

    # print(response_data)
    # response_data = body
    
    if (len(json.dumps(response_data)) > (SUB_REQ_MAX_LENGHT-2)):
        print("Response too long: %d"%len(json.dumps(response_data)))
        response_data = {"reason":"From request the generated response is too long"}
        return ConnexionResponse(
        status_code=codes[1],
        content_type='application/json',
        #headers={"Location": groupDocId},
        body=response_data)
    else:
        N = random.randint(MINIMUM_VALGROUP,MAXIMUM_VALGROUP)
        groupDocId = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
        # Make sure groupDocId generated is not used
        while(cursor.execute("SELECT * FROM "+TABLE_GROUPMANAGEMENT+" WHERE address = %s", (groupDocId,)) is not None):
            print("Subscription ID is in use. Creating new ID...")
            groupDocId = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
        
        response_data['resUri'] = "https://"+IPAddr+":"+str(AppPort)+"/ss-gm/v1/group-documents/"+groupDocId
        response_data['Location'] = groupDocId

        sql = "INSERT INTO "+TABLE_GROUPMANAGEMENT+" (address, valGroupId, groupDocsRequest, subType) VALUES (%s, %s, %s, %s)"
        val = (groupDocId, response_data['valGroupId'], json.dumps(response_data), subtype)
        
        group_database[groupDocId] = {
            "groupDocsRequest":response_data,
            "subType": subtype,
            "timestamp":datetime.datetime.now()
        }

        print("CREATE FIRST ENTRY.")
        cursor.execute(sql, val)
        db.commit()
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        response_data['Location'] = groupDocId
        print(tables)

        vlan = 0
        while ((vlan in vlan_group_connection) or (vlan == 0) or (vlan == 100)):
            vlan = random.randrange(start=2,stop=4094)
        vlan_group_connection[groupDocId] = vlan

        set_vlan_for_group = {
            "min_con" : "group0",
            "vlan": vlan
        }
        print(set_vlan_for_group)
        socket_send(set_vlan_for_group)

        if 'locInfo' in body.keys():
            gps = None
            dist = None
            ##Set current location, calculate distance and set delay
            i = random.randint(1,len(enodeB_database)-1) #Randomly set new location
            home_gps_loc = {"lat": enodeB_database[0]['lat'], "lon": enodeB_database[0]['lon']}


            ##Set current location, calculate distance and set delay
            if ('cellid' in body['locInfo'].keys()):
                valuser_current_loc_database[groupDocId] = {"accuracy":"cellid", 
                                                                    "locInfo" : {
                                                                        "cellid": body['locInfo']['cellid'],
                                                                    },
                                                                    "timestamp":datetime.datetime.now()
                                                                }
                gps = cellid_to_gps({"cellid": valuser_current_loc_database[groupDocId]['cellid']})
                dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
            elif ('ENODEB' in body['locInfo'].keys()):
                valuser_current_loc_database[groupDocId] = {"accuracy":"ENODEB",
                                                                    "locInfo": {
                                                                        "enodeBId": body['locInfo']['enodeBId']
                                                                        },
                                                                    "timestamp":datetime.datetime.now(),
                                                                    }
                gps = enodeb_to_gps({'enodeBId': valuser_current_loc_database[groupDocId]['locInfo']['enodeBId']})
                dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
            elif ('GEO_AREA' in body['locInfo'].keys()):
                valuser_current_loc_database[groupDocId] = {"accuracy":"GEO_AREA", 
                                                                    "locInfo": {
                                                                        "geographicArea": {
                                                                            "point":{
                                                                                "lat": body['locInfo']['geographicArea']['point']['lat'], 
                                                                                "lon": body['locInfo']['geographicArea']['point']['lon']
                                                                                },
                                                                            "shape" : "POINT",
                                                                            }
                                                                        },
                                                                    "timestamp":datetime.datetime.now(),  
                                                                }
                gps = valuser_current_loc_database[groupDocId]['locInfo']['geographicArea']['point']
                dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
            else:
                valuser_current_loc_database[groupDocId] = {"accuracy":"GEO_AREA", 
                                                                    "locInfo": {
                                                                        "geographicArea": {
                                                                            "point":{
                                                                                "lat": enodeB_database[i]['lat'], 
                                                                                "lon": enodeB_database[i]['lon']
                                                                                },
                                                                            "shape" : "POINT",
                                                                            }
                                                                        },
                                                                    "timestamp":datetime.datetime.now(),
                                                                }
                gps = valuser_current_loc_database[groupDocId]['locInfo']['geographicArea']['point']
                dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
            #Since only valid ids and locations can be set here, this part is not needed
            # if gps == None or dist == None:
            #     print("The Location is unknown.")
            #     response_data = {
            #         "reason":"Location is not valid or unknown"
            #     }
            #     denied = time.time() *1000
            #     print("Sending response denied: %f ms" %denied)
            #     print("Full message processing time: %f ms" %(denied-start))
            #     return ConnexionResponse(
            #         status_code=codes[1],
            #         content_type='application/json',
            #         headers={"Location": configurationId},
            #         body=response_data) 


    end = time.time() * 1000
    print("Received request: %f ms" %start)
    print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
    print("Sending response: %f ms" %end)
    print("Full message processing time: %f ms" %(end-start))


    return ConnexionResponse(
            status_code=codes[0],
            content_type='application/json',
            headers={"Location":groupDocId},
            body=response_data)

def RetrieveValGroupDocs():
    global cursor, db, group_database
    codes = [200, 400, 401, 404, 411, 429, 500, 503]
    start = time.time() * 1000
    subtype = "group-management"
    
    try:
        val_service_id = request.query_params['val-service-id']
        val_group_id = request.query_params['val-group-id']
        print("val_service_id: ",val_service_id)
        print("val_group_id: ",val_group_id)
    except:
        print("Empty query")

    try:
        auth_token = request.headers['authorization'].split(" ")[1]
        
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}
    
    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        headers = {"Authorization":auth_token}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )
    
    accepted = time.time()
    resp = []
    i = 0


    if (val_service_id):
        if ( (group_database[val_group_id]['groupDocsRequest'] is not None) and (group_database[val_group_id]['subType'] == subtype) ) :
            accepted = time.time() * 1000
            resp += group_database[val_group_id]['groupDocsRequest']
            groupDocId = val_group_id
        
        else:
            # sql = "SELECT * FROM %s WHERE address = %s AND subType = %s AND valGroupId = %s"
            # val = (TABLE_GROUPMANAGEMENT, val_service_id, subtype, val_group_id)
            sql = "SELECT * FROM "+ TABLE_GROUPMANAGEMENT +" WHERE subType = %s AND valGroupId = %s"
            val = (subtype, val_group_id)
            cursor.execute(sql, val)
            search = cursor.fetchall()

            if (search):
                accepted = time.time() * 1000
                for x in search:
                    print(x)
                    if (x[0] != val_service_id):
                        print("Wrong entry, address doesn't match val_service_id(\"%s\")" % val_service_id)
                    elif (x[3] != subtype):
                        #This shouldn't be a problem, because there can be no other subtype
                        #Just in case for value being corrupted or saved to wrong table
                        print("Wrong subscription type... (not \"%s\")" % subtype)
                    elif (x[1] != val_group_id):
                        print("Wrong entry, valGroupId doesn't match val_group_id(%s)" % val_group_id)
                    elif (x[0] == val_service_id and x[1] == val_group_id):
                        resp += x[2]
                        groupDocId = x[0]
            else:
                print("The groupDocId (%s) is not valid."%groupDocId)
                response_data = {
                    "reason":"Subscription ID is not valid"
                }
                denied = time.time() *1000
                print("Sending response denied for 1 ID: %f ms" %denied)
                print("Full message processing time: %f ms" %(denied-start))
                #Only valid groupDocId is expected any wrong ID results in no valid data being sent back
                return ConnexionResponse(
                    status_code=codes[1],
                    content_type='application/json',
                    body=resp)
                
    print("\n----------------")
    print(resp)
    print("----------------\n")

    headers = {"Location": groupDocId}
    content_type = {"Content-Type": "application/json"}

    end = time.time() * 1000
    print("Received request: %f ms" %start)
    print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
    print("Sending response: %f ms" %end)
    print("Full message processing time: %f ms" %(end-start))
    return ConnexionResponse(
        status_code=codes[0],
        content_type='application/json',
        body=resp)


def RetrieveIndValGroupDoc(groupDocId):
    global cursor, group_database
    start = time.time() * 1000
    codes = [200, 400, 401, 404, 411, 429, 500, 503]
    subtype = "group-management"

    try:
        auth_token = request.headers['Authorization'].split(" ")[1]
        #location = kwargs.get("request").headers['Location']
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}

    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        headers = {"Authorization":auth_token, "Location": groupDocId}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )


    if ((group_database[groupDocId]['groupDocsRequest'] is not None) and (group_database[groupDocId]['subType'] == subtype)):
        accepted = time.time() * 1000
        response_data = group_database[groupDocId]['groupDocsRequest']
        print("\n----------------")
        print(response_data)
        print("----------------\n")
         
        end = time.time() * 1000
        print("Received request: %f ms" %start)
        print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
        print("Sending response: %f ms" %end)
        print("Full message processing time: %f ms" %(end-start))

        return ConnexionResponse(
            status_code=codes[0],
            content_type="application/json",
            headers={"Location": groupDocId},
            body=response_data)

    else:
        sql = "SELECT * FROM "+ TABLE_GROUPMANAGEMENT +" WHERE address = %s AND subType = %s"
        val = (groupDocId, subtype)
        cursor.execute(sql,  val)
        search = cursor.fetchall()
        if (search):
            #print(search[0])
            if (search[0][0] != groupDocId):
                print("Wrong entry, address doesn't match groupDocId(%s)"%groupDocId)
            elif (search[0][3] != subtype):
                print("Wrong subscription type... (not \"%s\")"%subtype)
            else:
                accepted = time.time() * 1000
                response_data = json.loads(search[0][2])
                print("\n----------------")
                print(response_data)
                print("----------------\n")

                #print(search[0][0]==groupDocId)
                headers = {"Location": groupDocId}
                content_type = {"Content-Type": "application/json"}

                end = time.time() * 1000
                print("Received request: %f ms" %start)
                print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
                print("Sending response: %f ms" %end)
                print("Full message processing time: %f ms" %(end-start))

                return ConnexionResponse(
                    status_code=codes[0],
                    content_type="application/json",
                    headers={"Location": groupDocId},
                    body=response_data)
            
            print("Error in database")
            return ConnexionResponse(
                status_code=codes[1],
                content_type="application/json",
                headers={"Location": groupDocId},
                body=response_data)
        else:
            print("The groupDocId (%s) is not valid."%groupDocId)
            response_data = {
                "reason":"Subscription ID is not valid"
            }
            denied = time.time() *1000
            print("Sending response denied: %f ms" %denied)
            print("Full message processing time: %f ms" %(denied-start))
            return ConnexionResponse(
                status_code=codes[1],
                content_type='application/json',
                headers={"Location": groupDocId},
                body={})

def UpdateIndValGroupDoc(groupDocId, body):
    global cursor, db, group_database
    codes = [201, 400, 401, 404, 411, 429, 500, 503]
    start = time.time() * 1000
    subtype = "group-management"


    try:
        auth_token = request.headers['authorization'].split(" ")[1]
        #location = kwargs.get("request").headers['Location']
        #body = kwargs.get("body")
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}
    
    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        headers = {"Authorization":auth_token}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )
    
    response_data = {
                # "Location":"",
                # "valGroupId": "",
                # "grpDesc": "grpDesc",
                # "members": [],
                # "valGrpConf": "",
                # "valServiceIds": [],
                # "valSvcInf": "string",
                # "suppFeat": "FFFF",
                # "resUri": "https://"+IPAddr+":"+str(AppPort)+"/ss-gm/v1/group-documents/",
                # "locInfo":"",
                # "addLocInfo":"",
                # "extGrpId":"",
                # "com5GLanType":"",
                }


    if ("valGrpConf" in body):
        response_data['valGroupId'] = body['valGroupId']
    if ("valGrpConf" in body):
        response_data['valGrpConf'] = body['valGrpConf']
    if ("valServiceIds" in body):
        response_data['valServiceIds'] = body['valServiceIds']
    if ("members" in body):
        response_data['members'] = body['members']
    if ("suppFeat" in body):
        response_data['suppFeat'] = body['suppFeat']
    if ("grpDesc" in body):
        response_data['grpDesc'] = body['grpDesc']
    if ("locInfo" in body):
        response_data['locInfo'] = body['locInfo']
    if ("addLocInfo" in body):
        response_data['addLocInfo'] = body['addLocInfo']
    if ("extGrpId" in body):
        response_data['extGrpId'] = body['extGrpId']
    if ("com5GLanType" in body):
        response_data['com5GLanType'] = body['com5GLanType']
    if ("valSvcInf" in body):
        response_data['valSvcInf'] = body['valSvcInf']
    if ("resUri" in body):
        response_data['resUri'] = "https://"+IPAddr+":"+str(AppPort)+"/ss-gm/v1/group-documents/"
    

    sql = "SELECT * FROM "+TABLE_GROUPMANAGEMENT +" WHERE address = %s AND subType = %s;"
    val = (groupDocId, subtype)
    cursor.execute(sql,  val)
    search = cursor.fetchall()
    
    if (search and (len(groupDocId)>=MINIMUM_VALGROUP and len(groupDocId) <= MAXIMUM_VALGROUP)):
        accepted = time.time() *1000 
        sql = "UPDATE "+ TABLE_GROUPMANAGEMENT +" SET groupDocsRequest = %s WHERE address = %s AND subType = %s"
        val = (json.dumps(response_data), groupDocId, subtype)

        
        if (len(json.dumps(response_data)) > (SUB_REQ_MAX_LENGHT-2)):
            print("Response too long: %d"%len(json.dumps(response_data)))
            response_data = {"reason":"From request the generated response is too long"}
            return ConnexionResponse(
                status_code=codes[1],
                content_type='application/json',
                #headers={"Location": multiSubId},
                body=response_data)
        else:
            print("UPDATE ENTRY.")
            cursor.execute(sql, val)
            db.commit()
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print(tables)


        #TODO change vlan if needed
        vlan = 0
        while ((vlan in vlan_group_connection) or (vlan == 0) or (vlan == 100)):
            vlan = random.randrange(start=2,stop=4094)
        vlan_group_connection[groupDocId] = vlan
        
        change_vlan = {
            "min_con" : "group0",
            "vlan": vlan
        }
        print(change_vlan)
        socket_send(change_vlan)
        

        group_database[groupDocId]['groupDocsRequest'] = response_data
        group_database[groupDocId]['timestamp'] = datetime.datetime.now()
        end = time.time() * 1000
        print("Received request: %f ms" %start)
        print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
        print("Sending response: %f ms" %end)
        print("Full message processing time: %f ms" %(end-start))


        if 'locInfo' in body.keys():
            gps = None
            dist = None
            ##Set current location, calculate distance and set delay
            i = random.randint(1,len(enodeB_database)-1) #Randomly set new location
            home_gps_loc = {"lat": enodeB_database[0]['lat'], "lon": enodeB_database[0]['lon']}


            ##Set current location, calculate distance and set delay
            if ('cellid' in body['locInfo'].keys()):
                valuser_current_loc_database[groupDocId] = {"accuracy":"cellid", 
                                                                    "locInfo" : {
                                                                        "cellid": body['locInfo']['cellid'],
                                                                    },
                                                                    "timestamp":datetime.datetime.now(),
                                                                }
                gps = cellid_to_gps({"cellid": valuser_current_loc_database[groupDocId]['cellid']})
                dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
            elif ('ENODEB' in body['locInfo'].keys()):
                valuser_current_loc_database[groupDocId] = {"accuracy":"ENODEB",
                                                                    "locInfo": {
                                                                        "enodeBId": body['locInfo']['enodeBId']
                                                                        },
                                                                    "timestamp":datetime.datetime.now(),
                                                                    }
                gps = enodeb_to_gps({'enodeBId': valuser_current_loc_database[groupDocId]['locInfo']['enodeBId']})
                dist = dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
            elif ('GEO_AREA' in body['locInfo'].keys()):
                valuser_current_loc_database[groupDocId] = {"accuracy":"GEO_AREA", 
                                                                    "locInfo": {
                                                                        "geographicArea": {
                                                                            "point":{
                                                                                "lat": body['locInfo']['geographicArea']['point']['lat'], 
                                                                                "lon": body['locInfo']['geographicArea']['point']['lon']
                                                                                },
                                                                            "shape" : "POINT",
                                                                            }
                                                                        },
                                                                    "timestamp":datetime.datetime.now(),
                                                                }
                gps = valuser_current_loc_database[groupDocId]['locInfo']['geographicArea']['point']
                dist = calculate_gps_dist_for_small_range(valuser_current_loc_database[groupDocId]['locInfo']['geographicArea']['point'], home_gps_loc)
            else:
                valuser_current_loc_database[groupDocId] = {"accuracy":"GEO_AREA", 
                                                                    "locInfo": {
                                                                        "geographicArea": {
                                                                            "point":{
                                                                                "lat": enodeB_database[i]['lat'], 
                                                                                "lon": enodeB_database[i]['lon']
                                                                                },
                                                                            "shape" : "POINT",
                                                                            }
                                                                        },
                                                                    "timestamp":datetime.datetime.now(),
                                                                }
                gps = valuser_current_loc_database[groupDocId]['locInfo']['geographicArea']['point']
                dist = calculate_gps_dist_for_small_range(valuser_current_loc_database[groupDocId]['locInfo']['geographicArea']['point'], home_gps_loc)
            #Since only valid ids and locations can be set here, this part is not needed
            # if gps == None or dist == None:
            #     print("The Location is unknown.")
            #     response_data = {
            #         "reason":"Location is not valid or unknown"
            #     }
            #     denied = time.time() *1000
            #     print("Sending response denied: %f ms" %denied)
            #     print("Full message processing time: %f ms" %(denied-start))
            #     return ConnexionResponse(
            #         status_code=codes[1],
            #         content_type='application/json',
            #         headers={"Location": configurationId},
            #         body=response_data) 


        return ConnexionResponse(
                status_code=codes[0],
                content_type='application/json',
                headers={"Location":groupDocId},
                body=response_data)
    else:
            print("The groupDocID (%s) is not valid."%groupDocId)
            response_data = {
                "reason":"Location is not valid"
            }
            denied = time.time() *1000
            print("Sending response denied: %f ms" %denied)
            print("Full message processing time: %f ms" %(denied-start))
            return ConnexionResponse(
                status_code=codes[1],
                content_type='application/json',
                headers={"Location": groupDocId},
                body=response_data)  


def ModifyIndValGroupDoc(groupDocId, body):
    global cursor, db, group_database
    codes = [201, 400, 401, 404, 411, 429, 500, 503]
    start = time.time() * 1000
    subtype = "group-management"


    try:
        auth_token = request.headers['authorization'].split(" ")[1]
        #location = kwargs.get("request").headers['Location']
        #body = kwargs.get("body")
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}
    
    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        headers = {"Authorization":auth_token}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )


    
    sql = "SELECT * FROM "+ TABLE_GROUPMANAGEMENT +" WHERE address = %s AND subType = %s"
    val = (groupDocId, subtype)
    cursor.execute(sql,  val)
    search = cursor.fetchall()
    if (search):
        #print(search[0])
        if (search[0][0] != groupDocId):
            print("Wrong entry, address doesn't match groupDocId(%s)"%groupDocId)
        elif (search[0][3] != subtype):
            print("Wrong subscription type... (not \"%s\")"%subtype)
        else:
            accepted = time.time() * 1000
            response_data = search[0][2]
            response_data = json.loads(response_data)


            if ("valGrpConf" in body):
                response_data['valGrpConf'] = body['valGrpConf']
            if ("valServiceIds" in body):
                response_data['valServiceIds'] = body['valServiceIds']
            if ("members" in body):
                response_data['members'] = body['members']
            if ("grpDesc" in body):
                response_data['grpDesc'] = body['grpDesc']
            if ("locInfo" in body):
                response_data['locInfo'] = body['locInfo']
            if ("addLocInfo" in body):
                response_data['addLocInfo'] = body['addLocInfo']
            if ("extGrpId" in body):
                response_data['extGrpId'] = body['extGrpId']
            if ("com5GLanType" in body):
                response_data['com5GLanType'] = body['com5GLanType']
            if ("valSvcInf" in body):
                response_data['valSvcInf'] = body['valSvcInf']
 
            
            sql = "SELECT * FROM "+ TABLE_GROUPMANAGEMENT +" WHERE address = %s AND subType = %s"
            val = ( groupDocId, subtype)
            cursor.execute(sql,  val)
            search = cursor.fetchall()
            db.commit()
            

            print("\n-----MODIFIED-----------")
            print(response_data)
            print("----------------\n")

            #print(search[0][0]==groupDocId)
            headers = {"Location": groupDocId}
            content_type = {"Content-Type": "application/json"}

            
            sql = "UPDATE "+ TABLE_GROUPMANAGEMENT +" SET groupDocsRequest = %s WHERE address = %s AND subType = %s"
            val = (json.dumps(response_data), groupDocId, subtype)

            
            if (len(json.dumps(response_data)) > (VALGORUP_MAX_LENGTH-2)):
                print("Response too long: %d"%len(json.dumps(response_data)))
                response_data = {"reason":"From request the generated response is too long"}
                return ConnexionResponse(
                    status_code=codes[1],
                    content_type='application/json',
                    #headers={"Location": groupDocId},
                    body=response_data)
            else:
                print("PATCH ENTRY.")
                cursor.execute(sql, val)
                db.commit()
                print("UPDATE: ",cursor.rowcount, "record(s) affected") 
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()
                print(tables)


            #TODO change vlan if needed
            vlan = 0
            while ((vlan in vlan_group_connection) or (vlan == 0) or (vlan == 100)):
                vlan = random.randrange(start=2,stop=4094)
            vlan_group_connection[groupDocId] = vlan
            
            change_vlan = {
                "min_con" : "group0",
                "vlan": vlan
            }
            print(change_vlan)
            socket_send(change_vlan)

            group_database[groupDocId] = response_data
            group_database[groupDocId]['timestamp'] = datetime.datetime.now()
            end = time.time() * 1000
            print("Received request: %f ms" %start)
            print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
            print("Sending response: %f ms" %end)
            print("Full message processing time: %f ms" %(end-start))


            if 'locInfo' in body.keys():
                gps = None
                dist = None
                ##Set current location, calculate distance and set delay
                i = random.randint(1,len(enodeB_database)-1) #Randomly set new location
                home_gps_loc = {"lat": enodeB_database[0]['lat'], "lon": enodeB_database[0]['lon']}


                ##Set current location, calculate distance and set delay
                if ('cellid' in body['locInfo'].keys()):
                    valuser_current_loc_database[groupDocId] = {"accuracy":"cellid", 
                                                                        "locInfo" : {
                                                                            "cellid": body['locInfo']['cellid'],
                                                                        },
                                                                        "timestamp":datetime.datetime.now(),
                                                                    }
                    gps = cellid_to_gps({"cellid": valuser_current_loc_database[groupDocId]['cellid']})
                    dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
                elif ('ENODEB' in body['locInfo'].keys()):
                    valuser_current_loc_database[groupDocId] = {"accuracy":"ENODEB",
                                                                        "locInfo": {
                                                                            "enodeBId": body['locInfo']['enodeBId']
                                                                            },
                                                                        "timestamp":datetime.datetime.now(),
                                                                        }
                    gps = enodeb_to_gps({'enodeBId': valuser_current_loc_database[groupDocId]['locInfo']['enodeBId']})
                    dist = dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
                elif ('GEO_AREA' in body['locInfo'].keys()):
                    valuser_current_loc_database[groupDocId] = {"accuracy":"GEO_AREA", 
                                                                        "locInfo": {
                                                                            "geographicArea": {
                                                                                "point":{
                                                                                    "lat": body['locInfo']['geographicArea']['point']['lat'], 
                                                                                    "lon": body['locInfo']['geographicArea']['point']['lon']
                                                                                    },
                                                                                "shape" : "POINT",
                                                                                }
                                                                            },
                                                                        "timestamp":datetime.datetime.now(),     
                                                                    }
                    gps = valuser_current_loc_database[groupDocId]['locInfo']['geographicArea']['point']
                    dist = calculate_gps_dist_for_small_range(valuser_current_loc_database[groupDocId]['locInfo']['geographicArea']['point'], home_gps_loc)
                    # dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
                else:
                    valuser_current_loc_database[groupDocId] = {"accuracy":"GEO_AREA", 
                                                                        "locInfo": {
                                                                            "geographicArea": {
                                                                                "point":{
                                                                                    "lat": enodeB_database[i]['lat'], 
                                                                                    "lon": enodeB_database[i]['lon']
                                                                                    },
                                                                                "shape" : "POINT",
                                                                                }
                                                                            },
                                                                        "timestamp":datetime.datetime.now(),
                                                                    }
                    gps = valuser_current_loc_database[groupDocId]['locInfo']['geographicArea']['point']
                    dist = calculate_gps_dist_for_small_range(valuser_current_loc_database[groupDocId]['locInfo']['geographicArea']['point'], home_gps_loc)
                #Since only valid ids and locations can be set here, this part is not needed
                # if gps == None or dist == None:
                #     print("The Location is unknown.")
                #     response_data = {
                #         "reason":"Location is not valid or unknown"
                #     }
                #     denied = time.time() *1000
                #     print("Sending response denied: %f ms" %denied)
                #     print("Full message processing time: %f ms" %(denied-start))
                #     return ConnexionResponse(
                #         status_code=codes[1],
                #         content_type='application/json',
                #         headers={"Location": configurationId},
                #         body=response_data) 



            return ConnexionResponse(
                    status_code=codes[0],
                    content_type='application/json',
                    headers={"Location":groupDocId},
                    body=body)
    else:
            print("The groupDocID (%s) is not valid."%groupDocId)
            response_data = {
                "reason":"Location is not valid"
            }
            denied = time.time() *1000
            print("Sending response denied: %f ms" %denied)
            print("Full message processing time: %f ms" %(denied-start))
            return ConnexionResponse(
                status_code=codes[1],
                content_type='application/json',
                headers={"Location": groupDocId},
                body=response_data)  

def DeleteIndValGroupDoc(groupDocId):
    global cursor, db, group_database
    start = time.time() * 1000
    codes = [200, 400, 401, 404, 411, 429, 500, 503]
    subType = "group-management"

    try:
        auth_token = request.headers['Authorization'].split(" ")[1]
        #location = kwargs.get("request").headers['Location']
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}

    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        headers = {"Authorization":auth_token, "Location": groupDocId}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )

    sql = "DELETE FROM "+ TABLE_GROUPMANAGEMENT +" WHERE address = %s AND subType = %s"
    val = (groupDocId, subType)
    cursor.execute(sql, val)
    db.commit()
    print(cursor.rowcount, "record(s) deleted") # To test, that only 1 line is entry is deleted
    if (cursor.rowcount > 0):
        vlan_group_connection.pop(groupDocId)
        response_data = {}
        if (groupDocId in group_database):
            group_database.pop(groupDocId)
        return ConnexionResponse(
            status_code=codes[0],
            content_type='application/json',
            headers={"Location": groupDocId},
            body=response_data)
    else:
        print("The GroupDocId (%s) is not valid."%groupDocId)
        response_data = {
            "reason":"Subscription ID is not valid"
        }
        denied = time.time() *1000
        print("Sending response denied: %f ms" %denied)
        print("Full message processing time: %f ms" %(denied-start))
        return ConnexionResponse(
            status_code=codes[1],
            content_type='application/json',
            headers={"Location": groupDocId},
            body=response_data)





#Multi-subscription block (POST,GET,DELETE)
def CreateMulticastSubscription(body):
    global cursor, db, subs_database, enodeB_database
    start = time.time() * 1000
    codes = [201, 400, 401, 404, 411, 429, 500, 503]
    subtype = "multicast-subscription"
    
    try:
        auth_token = request.headers['authorization'].split(" ")[1]
        #location = kwargs.get("request").headers['Location']
        #body = kwargs.get("body")
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}

    try: 
        location = request.headers['location']
        if (location == "" or location == None):
            location = None
        else:
            print("Location given (Update request maybe): %s"%location)
    except:
        location = None
    
    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        if (location is not None):
            headers = {"Authorization":auth_token, "Location": location}
        else:
            headers = {"Authorization":auth_token}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )
    
    accessToken: str
    print("Body: \n")
    print(body)
    print("\n")
    print(type(body))

    if ((location != None) and (location != "")):
        #if (len(location)>= MINIMUM_SUB_ID and len(location) < MAXIMUM_SUB_ID+1):
            #location is within expected range, but check if it is previously generated value
            multiSubId = location
            if ((len(location)>=MINIMUM_SUB_ID and len(location) <= MAXIMUM_SUB_ID)):
                sql = "SELECT * FROM "+ TABLENAME +" WHERE address = %s AND subType = %s;"
                val = (multiSubId, subtype)
                access_db = time.time() * 1000
                if (multiSubId in subs_database):
                    search = subs_database[multiSubId]
                else:
                    cursor.execute(sql, val)
                    search = cursor.fetchall()
                    print(sql)
                    print(val)


                print(search)
                print("\n---------\n")
                reached_db = time.time() * 1000
                # sql = "SHOW TABLES"
                # cursor.execute(sql)
                # print(cursor.fetchall())
                if((search)):
                    print("VALID uniSubId and search found entry....")
                    print("Access db: %f ms\n" % (access_db - start))
                    print("DB resp in: %f ms\n"% (reached_db - access_db))
                    accepted = time.time() * 1000
                    #multiSubId = location
                    sql = "UPDATE "+ TABLENAME +" SET subscriptionRequest = %s WHERE address = %s AND subType = %s"
                    val = (json.dumps(body), multiSubId, subtype)
                    print(sql % val)
                    cursor.execute(sql, val)
                    db.commit()
                    print(cursor.rowcount, "record(s) affected")
                    # cursor.execute("SHOW TABLES;")
                    # tables = cursor.fetchall()
                    # print("TABLES: ")
                    # print(tables[0])
                    response_data = {
                            "Location": multiSubId,
                            "valGroupId": body["valGroupId"],
                            "anncMode":body["anncMode"],
                            "duration": body["duration"],
                            "multiQosReq":body["multiQosReq"],
                            "locArea":body["locArea"],
                            "tmgi":body["tmgi"],
                            "upIpv4Addr":body["upIpv4Addr"],
                            "upIpv6Addr":body["upIpv6Addr"],
                            "upPortNum":body["upPortNum"],
                            "radioFreqs":body["radioFreqs"],
                            "localMbmsInfo":{
                                    "mbmsEnbIpv4MulAddr":"198.51.100.1",
                                    "mbmsEnbIpv6MulAddr":"2001:db8:abcd:12::0/64",
                                    "mbmsGwIpv4SsmAddr":"198.51.100.61",
                                    "mbmsGwIpv6SsmAddr":"2001:db8:abcd:13::0/64",
                                    "cteid":"string",
                                    "bmscIpv4Addr":"198.51.110.1",
                                    "bmscIpv6Addr":"2001:db8:abcd:10::0/64",
                                    "bmscPort":5550,
                            },
                            "localMbmsActInd":True,
                            "notifUri":{
                                    'websocketUri': 'https://'+IPAddr+':'+str(AppPort)+'/notifUri', #'https://10.1.4.40:7777/notifUri'
                                    'requestWebsocketUri': False,
                            },
                            "reqTestNotif":True,
                            "wsNotifCfg": {
                                "websocketUri": "https://"+IPAddr+":"+str(AppPort)+"/notifUri",
                                "requestWebsocketUri": True
                            },
                            "suppFeat": "FFFFF"
                    }

                    bod = json.loads(body["multiQosReq"])
                    ulBW, utype = bw_round_2_dec(bod["ulBW"])
                    dlBW, dtype = bw_round_2_dec(bod["dlBW"])
                    # print("%s\n%s" %(bod["ulBW"],bod["dlBW"]))
                    bw, bw_ext = bw_adder(ulBW, utype, dlBW, dtype)
                    set_bw = {
                        "min_con" : "bandwidth",
                        "bw":  bw * 1.1,
                        "bw_type": bw_ext,
                        "flowID": bod['flowID'],
                    }
                    print("%s %s"%(set_bw["bw"], set_bw["bw_type"]))
                    res = socket_send(set_bw)

    
                    #Was Location specified?
                    if ('locArea' in body.keys()):
                        print(type(body['locArea']))
                        print(type(body))
                        try:
                            bod = json.loads(body['locArea'])
                        except:
                            bod = body['locArea']
                        print(bod)
                        ##Set current location, calculate distance and set delay, if there is location parameter
                        if ('geographicArea' in bod.keys()):
                            print(bod['geographicArea'][0])
                            print(type(bod['geographicArea'][0]))
                            
                            gps = {"lat": bod['geographicArea'][0]['point']['lat'],
                                    "lon": bod['geographicArea'][0]['point']['lon']}
                            valuser_current_loc_database[multiSubId] = {"accuracy": "GEO_AREA",
                                                                            "locInfo": {
                                                                                'point': {
                                                                                    "lat": bod['geographicArea'][0]['point']['lat'],
                                                                                    "lon": bod['geographicArea'][0]['point']['lon']
                                                                                },
                                                                                "shape" : bod['geographicArea'][0]['shape'],
                                                                                    # "innerRadius": body['geographicArea'][0]['innerRadius'] #327674,
                                                                                    # "uncertaintyRadius": body['geographicArea'][0]['uncertaintyRadius'] #254,
                                                                                    # "offsetAngle": body['geographicArea'][0]['offsetAngle'] #180,
                                                                                    # "includedAngle": body['geographicArea'][0]['includedAngle'] #180,
                                                                                    # "confidence": body['geographicArea'][0]['confidence'] #80,
                                                                                },
                                                                            "timestamp":datetime.datetime.now()
                                                                        }
                            if 'innerRadius' in bod['geographicArea'][0].keys():
                                valuser_current_loc_database[multiSubId]['locInfo']['point']['innerRadius'] = bod['geographicArea'][0]['innerRadius']
                            if 'uncertaintyRadius' in bod['geographicArea'][0].keys():
                                valuser_current_loc_database[multiSubId]['locInfo']['point']['uncertaintyRadius'] = bod['geographicArea'][0]['uncertaintyRadius']
                            if 'offsetAngle' in bod['geographicArea'][0].keys():
                                valuser_current_loc_database[multiSubId]['locInfo']['point']['offsetAngle'] = bod['geographicArea'][0]['offsetAngle']
                            if 'confidence' in bod['geographicArea'][0].keys():
                                valuser_current_loc_database[multiSubId]['locInfo']['point']['confidence'] = bod['geographicArea'][0]['confidence']
                        elif ('cellid' in body['locArea'].keys()):    
                            for x in enodeB_database:
                                for y in bod['LocArea']['cellId']:
                                    if x['cellid'] == y:
                                        gps = cellid_to_gps({"cellid": y})
                                        valuser_current_loc_database[multiSubId] = {"accuracy":"cellid", 
                                                                                        'locInfo': {
                                                                                            "cellid": y
                                                                                        },
                                                                                        "timestamp":datetime.datetime.now(),
                                                                                        }
                                        break
                        elif ('enodeBId' in body['locArea'].keys()):
                            for x in enodeB_database:
                                for y in bod['locArea']['enodeBId']:
                                    if x['enodeBId'] == y:
                                        gps = enodeb_to_gps({"enodeBId": y})
                                        valuser_current_loc_database[multiSubId] = {"accuracy":"ENODEB",
                                                                                    "locInfo": {
                                                                                        "enodeBId": y
                                                                                    },
                                                                                    "timestamp":datetime.datetime.now(),
                                                                                    }
                                        break
                        
                        
                        dist = calculate_gps_dist_for_small_range(gps, {"lat": enodeB_database[0]['lat'], "lon": enodeB_database[0]['lon']})
                        delay = distance_delay(dist, "kilometer")
                        res = socket_send({
                            "min_con": "delay",
                            "delay": delay,
                            "delay_ext": "ms"
                        })
                        if (res < 200):
                            if (res == -2):
                                print("Error while trying to set delay: Client socket failed to create connection to server")
                            elif (res == -1):
                                print("Error while trying to set delay: Unsupported request")
                            elif (res == -300):
                                print("Error while trying to set delay: Wrong type")

                    # subs_database[multiSubId['multiSubReq']].update(response_data)
                    subs_database[multiSubId] = {
                        "uniSubReq": response_data,
                        "subType": subtype,
                        "timestamp":datetime.datetime.now(),
                    }
        
                    end = time.time() * 1000
                    print("Received request: %f ms" %start)
                    print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
                    print("Sending response: %f ms" %end)
                    print("Full message processing time: %f ms" %(end-start))
                    return ConnexionResponse(
                        status_code=codes[0],
                        content_type='application/json',
                        headers={"Location": multiSubId},
                        body=response_data
                    )
            

            
            else:
                print("The multiSubId (%s) is not valid."%location)
                response_data = {
                    "reason":"Location is not valid"
                }
                denied = time.time() *1000
                print("Sending response denied: %f ms" %denied)
                print("Full message processing time: %f ms" %(denied-start))
                return ConnexionResponse(
                    status_code=codes[1],
                    content_type='application/json',
                    headers={"Location": location},
                    body=response_data)  
    
    elif (location == None or location == ""):
        # multiSubId = "1113344kjghd"
        N = random.randint(MINIMUM_SUB_ID, MAXIMUM_SUB_ID)
        multiSubId = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
        # Make sure multiSubId generated is not used
        while(cursor.execute("SELECT * FROM "+ TABLENAME +" WHERE address = %s",(multiSubId,)) is not None):
            print("Subscription ID is in use. Creating new ID...")
            multiSubId = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

        print(json.dumps(body['multiQosReq']))

        #accessToken = body['Authorization']
        #if accessToken == 'Bearer ' + TOKEN:
        
        if 1:
            accepted = time.time() * 1000
            response_data = {
                                "Location": multiSubId,
                                "valGroupId": body["valGroupId"],
                                "anncMode":body["anncMode"],
                                "duration": body["duration"],
                                "multiQosReq":body['multiQosReq'],
                                "locArea":body["locArea"],
                                "tmgi":body["tmgi"],
                                "upIpv4Addr":body["upIpv4Addr"],
                                "upIpv6Addr":body["upIpv6Addr"],
                                "upPortNum":body["upPortNum"],
                                "radioFreqs":body["radioFreqs"],
                                "localMbmsInfo": body["localMbmsInfo"],
                                #{
                                #         "mbmsEnbIpv4MulAddr":"198.51.100.1",
                                #         "mbmsEnbIpv6MulAddr":"2001:db8:abcd:12::0/64",
                                #         "mbmsGwIpv4SsmAddr":"198.51.100.61",
                                #         "mbmsGwIpv6SsmAddr":"2001:db8:abcd:13::0/64",
                                #         "cteid":"string",
                                #         "bmscIpv4Addr":"198.51.110.1",
                                #         "bmscIpv6Addr":"2001:db8:abcd:10::0/64",
                                #         "bmscPort":5550,
                                # },
                                "localMbmsActInd":True,
                                "notifUri":{
                                        'websocketUri': 'https://'+IPAddr+':'+str(AppPort)+'/notifUri', #'https://10.1.4.40:7777/notifUri'
                                        'requestWebsocketUri': False,
                                },
                                "reqTestNotif":True,
                                "wsNotifCfg": {
                                    "websocketUri": "https://"+IPAddr+":"+str(AppPort)+"/notifUri",
                                    "requestWebsocketUri": True
                                },
                                "suppFeat": "FFFFF"
                            }
            print("\n----------------")
            print(response_data)
            print("----------------\n")

            #headers = {"Location": multiSubId}
            #content_type = {"Content-Type": "application/json"}

            sql = "INSERT INTO "+ TABLENAME +" (address, subscriptionRequest, subType) VALUES (%s, %s, %s)"
            val = (multiSubId, json.dumps(response_data), subtype)

            
            if (len(json.dumps(response_data)) > (SUB_REQ_MAX_LENGHT-2)):
                print("Response too long: %d"%len(json.dumps(response_data)))
                response_data = {"reason":"From request the generated response is too long"}
                return ConnexionResponse(
                status_code=codes[1],
                content_type='application/json',
                #headers={"Location": multiSubId},
                body=response_data)
            else:
                print("CREATE FIRST ENTRY.")
                cursor.execute(sql, val)
                db.commit()
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()
                print(tables)



            

            subs_database[multiSubId] = {
                "multiSubReq":response_data,
                "subType":subtype,
                "timestamp":datetime.datetime.now()
            }
            end = time.time() * 1000
            print("Received request: %f ms" %start)
            print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
            print("Sending response: %f ms" %end)
            print("Full message processing time: %f ms" %(end-start))

            

            bod = json.loads(body["multiQosReq"])
            ulBW, utype = bw_round_2_dec(bod["ulBW"])
            dlBW, dtype = bw_round_2_dec(bod["dlBW"])
            # print("%s\n%s" %(bod["ulBW"],bod["dlBW"]))
            bw, bw_ext = bw_adder(ulBW, utype, dlBW, dtype)
            set_bw = {
                "min_con" : "bandwidth",
                "bw":  bw * 1.1,
                "bw_type": bw_ext,
                "flowID": bod['flowID'],
            }
            print("%s %s"%(set_bw["bw"], set_bw["bw_type"]))
            res = socket_send(set_bw)

            if (res < 200):
                if (res == -2):
                    print("Error while trying to set bandwidth: Client socket failed to create connection to server")
                elif (res == -1):
                    print("Error while trying to set bandwidth: Unsupported request")
                elif (res == -300):
                    print("Error while trying to set bandwidth: Wrong type")
                
            

            #Was Location specified?
            if ('locArea' in body.keys()):
                print(type(body['locArea']))
                print(type(body))
                try:
                    bod = json.loads(body['locArea'])
                except:
                    bod = body['locArea']
                print(bod)


                ##Set current location, calculate distance and set delay, if there is location parameter
                if ('geographicArea' in bod.keys()):
                    print(bod['geographicArea'][0])
                    print(type(bod['geographicArea'][0]))
                    
                    gps = {"lat": bod['geographicArea'][0]['point']['lat'],
                            "lon": bod['geographicArea'][0]['point']['lon']}
                    valuser_current_loc_database[multiSubId] = {"accuracy": "GEO_AREA",
                                                                    "locInfo": {
                                                                        'point': {
                                                                            "lat": bod['geographicArea'][0]['point']['lat'],
                                                                            "lon": bod['geographicArea'][0]['point']['lon']
                                                                        },
                                                                        "shape" : bod['geographicArea'][0]['shape'],
                                                                        # "innerRadius": body['geographicArea'][0]['innerRadius'] #327674,
                                                                        # "uncertaintyRadius": body['geographicArea'][0]['uncertaintyRadius'] #254,
                                                                        # "offsetAngle": body['geographicArea'][0]['offsetAngle'] #180,
                                                                        # "includedAngle": body['geographicArea'][0]['includedAngle'] #180,
                                                                        # "confidence": body['geographicArea'][0]['confidence'] #80,
                                                                        },
                                                                    "timestamp":datetime.datetime.now()
                                                                }
                    if 'innerRadius' in bod['geographicArea'][0].keys():
                        valuser_current_loc_database[multiSubId]['locInfo']['point']['innerRadius'] = bod['geographicArea'][0]['innerRadius']
                    if 'uncertaintyRadius' in bod['geographicArea'][0].keys():
                        valuser_current_loc_database[multiSubId]['locInfo']['point']['uncertaintyRadius'] = bod['geographicArea'][0]['uncertaintyRadius']
                    if 'offsetAngle' in bod['geographicArea'][0].keys():
                        valuser_current_loc_database[multiSubId]['locInfo']['point']['offsetAngle'] = bod['geographicArea'][0]['offsetAngle']
                    if 'confidence' in bod['geographicArea'][0].keys():
                        valuser_current_loc_database[multiSubId]['locInfo']['point']['confidence'] = bod['geographicArea'][0]['confidence']
                elif ('cellid' in body['locArea'].keys()):    
                    for x in enodeB_database:
                        for y in bod['LocArea']['cellId']:
                            if x['cellid'] == y:
                                gps = cellid_to_gps({"cellid": y})
                                valuser_current_loc_database[multiSubId] = {"accuracy":"cellid", 
                                                                                'locInfo': {
                                                                                    "cellid": y
                                                                                },
                                                                                "timestamp":datetime.datetime.now(),
                                                                                }
                                break
                elif ('enodeBId' in body['locArea'].keys()):
                    for x in enodeB_database:
                        for y in bod['locArea']['enodeBId']:
                            if x['enodeBId'] == y:
                                gps = enodeb_to_gps({"enodeBId": y})
                                valuser_current_loc_database[multiSubId] = {"accuracy":"ENODEB",
                                                                            "locInfo": {
                                                                                "enodeBId": y
                                                                            },
                                                                            "timestamp":datetime.datetime.now(),
                                                                            }
                                break
                
                
                dist = calculate_gps_dist_for_small_range(gps, {"lat": enodeB_database[0]['lat'], "lon": enodeB_database[0]['lon']})
                delay = distance_delay(dist, "kilometer")
                res = socket_send({
                    "min_con": "delay",
                    "delay": delay,
                    "delay_ext": "ms"
                })
                if (res < 200):
                    if (res == -2):
                        print("Error while trying to set delay: Client socket failed to create connection to server")
                    elif (res == -1):
                        print("Error while trying to set delay: Unsupported request")
                    elif (res == -300):
                        print("Error while trying to set delay: Wrong type")


            # ##Set current location, calculate distance and set delay
            # gps = None
            # for x in enodeB_database:
            #     if x['cellid'] == body['locArea']['cellId']:
            #         gps = cellid_to_gps({"cellid": body['locArea']['cellId']})
            #         break
            # if (gps == None):
            #     helper_shape = body['locArea']['geographicArea'][0]['shape'].lower()

            #     ## None point shapes can have radius and confidence levels, it will be ignored -- for testing
                
            #     gps = {"lat": body[ 'locArea' ][ 'geographicArea' ][0][ helper_shape ][ 'lat' ], 
            #            "lon": body[ 'locArea' ][ 'geographicArea' ][0][ helper_shape ][ 'lon' ] }

            # dist = calculate_gps_dist_for_small_range(gps, {"lat": enodeB_database[0]['lat'], "lon": enodeB_database[0]['lon']})
            # delay = distance_delay(dist, "kilometer")
            # socket_send({
            #     "min_con": "delay",
            #     "delay": delay,
            #     "delay_ext": "ms"
            # })


            return ConnexionResponse(
                status_code=codes[0],
                content_type='application/json',
                headers={"Location": multiSubId},
                body=response_data)

        else:
            print(TOKEN)
            print(accessToken)
            return {}, codes[1], {"Content-Type": "application/json"}
        
    else:
        print("Location out of range! Too long or short Location given, possible guessing attack: %s \n"%location)
        response_data = {"reason" : "Wrong Location header"}
        return ConnexionResponse(
                status_code=codes[4],
                content_type='application/json',
                headers={"Location": location},
                body=response_data
        )

def GetMulticastSubscription(multiSubId):
    global cursor, subs_database
    start = time.time() * 1000
    codes = [200, 400, 401, 404, 411, 429, 500, 503]
    subtype = "multicast-subscription"

    try:
        auth_token = request.headers['Authorization'].split(" ")[1]
        #location = kwargs.get("request").headers['Location']
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}

    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        if (multiSubId is not None):
            headers = {"Authorization":auth_token, "Location": multiSubId}
        else:
            headers = {"Authorization":auth_token}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )
    
    #requested data in local variable
    if ( (subs_database[multiSubId]['multiSubReq'] is not None) and subs_database[multiSubId]['subType'] == subtype ):
        accepted = time.time() * 1000
        response_data = subs_database[multiSubId]['multiSubReq']
        print("\n----------------")
        print(response_data)
        print("----------------\n")

        headers = {"Location": multiSubId}
        content_type = {"Content-Type": "application/json"}

        end = time.time() * 1000
        print("Received request: %f ms" %start)
        print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
        print("Sending response: %f ms" %end)
        print("Full message processing time: %f ms" %(end-start))
        return ConnexionResponse(
                status_code=codes[0],
                content_type='application/json',
                headers={"Location": multiSubId},
                body=response_data)

    #requested data not in local variable, but can be in database
    else:
        sql = "SELECT * FROM "+ TABLENAME +" WHERE address = %s AND subType = %s"
        val = (multiSubId, subtype)
        cursor.execute(sql, val)
        search = cursor.fetchall()
        if (search):
            if (search[0][0] != multiSubId):
                print("Wrong entry, address doesn't match MultiSubId(%s)"%multiSubId)
            if (search[0][2] != subtype):
                print("Wrong subscription type... (not \"%s\")"%subtype)
            accepted = time.time() * 1000
            response_data = search[0][1]
            print("\n----------------")
            print(response_data)
            print("----------------\n")

            headers = {"Location": multiSubId}
            content_type = {"Content-Type": "application/json"}

            end = time.time() * 1000
            print("Received request: %f ms" %start)
            print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
            print("Sending response: %f ms" %end)
            print("Full message processing time: %f ms" %(end-start))

            return ConnexionResponse(
                status_code=codes[0],
                content_type='application/json',
                headers={"Location": multiSubId},
                body=response_data)
        else:
            print("The multiSubId (%s) is not valid."%multiSubId)
            response_data = {
                "reason":"Subscription ID is not valid"
            }
            denied = time.time() *1000
            print("Sending response denied: %f ms" %denied)
            print("Full message processing time: %f ms" %(denied-start))
            return ConnexionResponse(
                status_code=codes[1],
                content_type='application/json',
                headers={"Location": multiSubId},
                body=response_data)

def DeleteMulticastSubscription(multiSubId):
    global cursor, db, subs_database
    start = time.time() * 1000
    codes = [200, 400, 401, 404, 411, 429, 500, 503]
    subType = "multicast-subscription"

    try:
        auth_token = request.headers['Authorization'].split(" ")[1]
        #location = kwargs.get("request").headers['Location']
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}

    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        if (multiSubId is not None):
            headers = {"Authorization":auth_token, "Location": multiSubId}
        else:
            headers = {"Authorization":auth_token}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )

    sql = "DELETE FROM "+TABLENAME+" WHERE address = %s AND subType = %s"
    val = (multiSubId, subType)
    cursor.execute(sql,  val)
    db.commit()
    print(cursor.rowcount, "record(s) deleted") # To test, that only 1 line is entry is deleted
    if (cursor.rowcount > 0):
        response_data = {}
        
        ##Delete from local registered subs
        if (multiSubId in subs_database):
            subs_database.pop(multiSubId)
        ##Delete from local valuser loc if exists
        if (multiSubId in valuser_current_loc_database):
            valuser_current_loc_database.pop(multiSubId)


        return ConnexionResponse(
            status_code=codes[0],
            content_type='application/json',
            headers={"Location": multiSubId},
            body=response_data)
    else:
        print("The multiSubId (%s) is not valid."%multiSubId)
        response_data = {
            "reason":"Subscription ID is not valid"
        }
        denied = time.time() *1000
        print("Sending response denied: %f ms" %denied)
        print("Full message processing time: %f ms" %(denied-start))
        return ConnexionResponse(
            status_code=codes[1],
            content_type='application/json',
            headers={"Location": multiSubId},
            body=response_data)



#Unicast-subscription block (POST,GET,DELETE)
def CreateUnicastSubscription(body):
    global cursor, db, subs_database, enodeB_database
    start = time.time() * 1000
    location = None
    codes = [201, 400, 401, 404, 411, 429, 500, 503]
    subtype = "unicast-subscription"

    try:
        auth_token = request.headers['authorization'].split(" ")[1]
        #location = kwargs.get("request").headers['Location']
        #body = kwargs.get("body")
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}

    try: 
        location = request.headers['location']
        if (location == "" or location == None):
            location = None
        else:
            print("Location given (Update request maybe): %s"%location)
    except:
        location = None
    
    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        if (location is not None):
            headers = {"Authorization":auth_token, "Location": location}
        else:
            headers = {"Authorization":auth_token}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )
    
    accessToken: str
    print("Body: \n")
    print(body)
    print("\n")
    print(type(body))

    if ((location != None) and (location != "")):
        #if (len(location)>= MINIMUM_SUB_ID and len(location) < MAXIMUM_SUB_ID+1):
            #location is within expected range, but check if it is previously generated value

            uniSubId = location
            if (len(location)>= MINIMUM_SUB_ID and len(location) <= MAXIMUM_SUB_ID):
                sql = "SELECT * FROM "+ TABLENAME +" WHERE address = %s AND subType = %s;"
                val = (uniSubId, subtype)
                access_db = time.time() * 1000
                if (uniSubId in subs_database):
                    search = subs_database[uniSubId]
                else:
                    cursor.execute(sql, val)
                    search = cursor.fetchall()
                    print(sql)
                    print(val)
                
                print(search)
                print("\n---------\n")
                reached_db = time.time() * 1000
                # sql = "SHOW TABLES"
                # cursor.execute(sql)
                # print(cursor.fetchall())
                if(search):
                    print("VALID uniSubId and search found entry....")
                    print("Access db: %f ms\n" % (access_db - start))
                    print("DB resp in: %f ms\n"% (reached_db - access_db))
                    
                    accepted = time.time() * 1000
                    #uniSubId = location
                    sql = "UPDATE "+ TABLENAME +" SET subscriptionRequest = %s WHERE address = %s AND subType = %s"
                    val = (json.dumps(body), uniSubId, subtype)
                    print(sql % val)
                    cursor.execute(sql, val)
                    db.commit()
                    print(cursor.rowcount, "record(s) affected")
                    tmp = time.time()*1000
                    print("Records affected: %f ms\n"%(tmp-reached_db))
                    
                    response_data = {
                                        "duration": body['duration'], #Valid until duration (date-time): Default value is message sending date + 7 days
                                        "Location": uniSubId,
                                        "valGroupId": 'valGroupId1',
                                        "grpDesc": json.loads(body['uniQosReq'])["flowID"],
                                        "uniQosReq": body['uniQosReq'],
                                        "valTgtUe": body["valTgtUe"],
                                        "valGrpConf": "string",
                                        "valServiceIds": [
                                            "valServiceId1",
                                            "valServiceId2"
                                        ],
                                        'notifUri': {
                                                'websocketUri': 'https://'+IPAddr+':'+str(AppPort)+'/notifUri', #'https://10.1.4.40:7777/notifUri'
                                                'requestWebsocketUri': False,
                                        },
                                        "wsNotifCfg" : {
                                            "websocketUri": "https://"+IPAddr+":"+str(AppPort)+"/wsNotifUri", #'https://10.1.4.40:7777/wsNotifCfg'
                                            "requestWebsocketUri": False,
                                        },
                                        "reqTestNotif": True,
                                        "valSvcInf": "string",
                                        "suppFeat": "FFFF",
                                        "resUri": "https://"+IPAddr+":"+str(AppPort)+"/ss-gm/v1/group-documents/" + str(uniSubId)
                    }

                    ##Set requested bandwidth for links
                    bod = json.loads(body["uniQosReq"])
                    ulBW, utype = bw_round_2_dec(bod["ulBW"])
                    dlBW, dtype = bw_round_2_dec(bod["dlBW"])
                    #print("%s\n%s" %(bod["ulBW"],bod["dlBW"]))
                    #bw, bw_ext = bw_adder(ulBW, utype, dlBW, dtype)
                    set_bw = {
                        "min_con" : "bandwidth",
                        "bw":  ( float(ulBW)  + float(dlBW) )* 1.1,
                        "bw_type": dtype,
                        "flowID": bod['flowID'],
                    }
                    print("%s %s"%(set_bw["bw"], set_bw["bw_type"]))
                    
                    if set_bw['bw'] == 0.0:
                        set_bw['bw'] = 1.0
                    socked_sent = time.time()*1000
                    print("Sent bw update: %f ms\n"%(socked_sent-tmp))
                    res = socket_send(set_bw)


                    if (res < 200):
                        if (res == -2):
                            print("Error while trying to set bandwidth: \nClient socket failed to create connection to server")
                        elif (res == -1):
                            print("Error while trying to set bandwidth: \nUnsupported request")
                        elif (res == -300):
                            print("Error while trying to set bandwidth: \nWrong type")
                        else:
                            print(res)

                        return ConnexionResponse(
                            status_code=codes[6],
                            content_type='application/json',
                            headers={"Location": uniSubId},
                            body=response_data
                        )
                    
                    # subs_database[uniSubId]["uniSubReq"].update(response_data)
                    subs_database[uniSubId] = {
                        "uniSubReq": response_data,
                        "subType": subtype,
                        "timestamp":datetime.datetime.now()
                    }

                    end = time.time() * 1000
                    print("Received request: %f ms" %start)
                    print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
                    print("Sending response: %f ms" %end)
                    print("Full message processing time: %f ms" %(end-start))
                    return ConnexionResponse(
                        status_code=codes[0],
                        content_type='application/json',
                        headers={"Location": uniSubId},
                        body=response_data
                    )
            
            else:
                print("The uniSubId (%s) is not valid."%location)
                response_data = {
                    "reason":"Location is not valid"
                }
                denied = time.time() *1000
                print("Sending response denied: %f ms" %denied)
                print("Full message processing time: %f ms" %(denied-start))
                return ConnexionResponse(
                    status_code=codes[1],
                    content_type='application/json',
                    headers={"Location": location},
                    body=response_data)  
    
    elif (location == None or location == ""):
        # uniSubId = "1113344kjghd"
        N = random.randint(MINIMUM_SUB_ID, MAXIMUM_SUB_ID)
        uniSubId = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
        # Make sure uniSubId generated is not used
        while(cursor.execute("SELECT * FROM "+ TABLENAME +" WHERE address = %s", (uniSubId,)) is not None):
            print("Subscription ID is in use. Creating new ID...")
            uniSubId = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
        tmp = time.time()*1000
        print(json.dumps(body['uniQosReq']))

        #if accessToken == 'Bearer ' + TOKEN:
        if 1:
            accepted = time.time() * 1000
            response_data = {
                                "duration": body['duration'], #Valid until duration (date-time): Default value is message sending date + 7 days
                                "Location": uniSubId,
                                "valGroupId": 'valGroupId1',
                                "grpDesc": json.loads(body['uniQosReq'])["flowID"],
                                "uniQosReq": body['uniQosReq'],
                                "valTgtUe": body["valTgtUe"],
                                "valGrpConf": "string",
                                "valServiceIds": [
                                    "valServiceId1",
                                    "valServiceId2"
                                ],
                                'notifUri': {
                                        'websocketUri': 'https://'+IPAddr+':'+str(AppPort)+'/notifUri', #'https://10.1.4.40:7777/notifUri'
                                        'requestWebsocketUri': False,
                                },
                                "wsNotifCfg" : {
                                    "websocketUri": "https://"+IPAddr+":"+str(AppPort)+"/wsNotifUri", #'https://10.1.4.40:7777/wsNotifCfg'
                                    "requestWebsocketUri": False,
                                },
                                "reqTestNotif": True,
                                "valSvcInf": "string",
                                "suppFeat": "FFFF",
                                "resUri": "https://"+IPAddr+":"+str(AppPort)+"/ss-gm/v1/group-documents/" + str(uniSubId)
                            }
            print("\n----------------")
            print(response_data)
            print("----------------\n")

            #headers = {"Location": uniSubId}
            #content_type = {"Content-Type": "application/json"}

            sql = "INSERT INTO "+ TABLENAME +" (address, subscriptionRequest, subType) VALUES (%s, %s, %s)"
            val = (uniSubId, json.dumps(response_data), subtype)
            
            if (len(json.dumps(response_data)) > (SUB_REQ_MAX_LENGHT-2)):
                print("Response too long: %d"%len(json.dumps(response_data)))
                response_data = {"reason":"From request the generated response is too long"}
                return ConnexionResponse(
                status_code=codes[1],
                content_type='application/json',
                #headers={"Location": uniSubId},
                body=response_data)
            else:
                print("CREATE FIRST ENTRY.")
                cursor.execute(sql, val)
                db.commit()
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()
                print(tables)

            #save to local variable for faster get requests
            subs_database[uniSubId] = {
                "uniSubReq": response_data,
                "subType": subtype,
                "timestamp":datetime.datetime.now()
            }
            
            ##Set requested bandwidth for 
            # print("\n\n")
            ##Set requested bandwidth for links
            bod = json.loads(body["uniQosReq"])
            ulBW, utype = bw_round_2_dec(bod["ulBW"])
            dlBW, dtype = bw_round_2_dec(bod["dlBW"])
            #print("%s\n%s" %(bod["ulBW"],bod["dlBW"]))
            #bw, bw_ext = bw_adder(ulBW, utype, dlBW, dtype)
            set_bw = {
                "min_con" : "bandwidth",
                "bw":  ( float(ulBW)  + float(dlBW) )* 1.1,
                "bw_type": dtype,
                "flowID": bod['flowID'],
            }
            print("%s %s"%(set_bw["bw"], set_bw["bw_type"]))
            
            if set_bw['bw'] == 0.0:
                set_bw['bw'] = 1.0
            socked_sent = time.time()*1000
            print("Sent bw update: %f ms\n"%(socked_sent-tmp))
            res = socket_send(set_bw)

            if (res < 200):
                if (res == -2):
                    print("Error while trying to set bandwidth: \nClient socket failed to create connection to server")
                elif (res == -1):
                    print("Error while trying to set bandwidth: \nUnsupported request")
                elif (res == -300):
                    print("Error while trying to set bandwidth: \nWrong type")


            end = time.time() * 1000
            print("Received request: %f ms" %start)
            print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
            print("Sending response: %f ms" %end)
            print("Full message processing time: %f ms" %(end-start))
            return ConnexionResponse(
                status_code=codes[0],
                content_type='application/json',
                headers={"Location": uniSubId},
                body=response_data)

        else:
            print(TOKEN)
            print(accessToken)
            return {}, codes[1], {"Content-Type": "application/json"}
        
    else:
        print("Location out of range! Too long or short Location given, possible guessing attack: %s \n"%location)
        response_data = {"reason" : "Wrong Location header"}
        return ConnexionResponse(
                status_code=codes[4],
                content_type='application/json',
                headers={"Location": location},
                body=response_data
        )

def GetUnicastSubscription(uniSubId):
    global cursor, subs_database
    start = time.time() * 1000
    codes = [200, 400, 401, 404, 411, 429, 500, 503]
    subtype = "unicast-subscription"

    try:
        auth_token = request.headers['Authorization'].split(" ")[1]
        #location = kwargs.get("request").headers['Location']
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}
    
    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        headers = {"Authorization":auth_token, "Location": uniSubId}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )



    if ( (subs_database[uniSubId]['uniSubReq'] is not None) and (subs_database[uniSubId]['subType'] == subtype) ):
        accepted = time.time() * 1000
        response_data = subs_database[uniSubId]['uniSubReq']
        print("\n----------------")
        print(response_data)
        print("----------------\n")

        end = time.time() * 1000
        print("Received request: %f ms" %start)
        print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
        print("Sending response: %f ms" %end)
        print("Full message processing time: %f ms" %(end-start))

        return ConnexionResponse(
            status_code=codes[0],
            content_type='application/json',
            headers={"Location": uniSubId},
            body=response_data)
    else:
        sql = "SELECT * FROM "+ TABLENAME +" WHERE address = %s AND subType = %s"
        val = (uniSubId, subtype)
        cursor.execute(sql, val)
        search = cursor.fetchall()
        print(search)
        # print(type(search))
        # print(type(search[0]))

        if (search):
            if (search[0][0] != uniSubId):
                print("Wrong entry, address doesn't match uniSubId(%s)"%uniSubId)
            if (search[0][2] != subtype):
                print("Wrong subscription type... (not \"%s\")"%subtype)
            accepted = time.time() * 1000
            response_data = search[0][1]
            print("\n----------------")
            print(response_data)
            print("----------------\n")

            headers = {"Location": uniSubId}
            content_type = {"Content-Type": "application/json"}

            end = time.time() * 1000
            print("Received request: %f ms" %start)
            print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
            print("Sending response: %f ms" %end)
            print("Full message processing time: %f ms" %(end-start))

            return ConnexionResponse(
                status_code=codes[0],
                content_type='application/json',
                headers={"Location": uniSubId},
                body=response_data)
        else:
            print("LAST RESORT")
            print("The uniSubId (%s) is not valid."%uniSubId)
            response_data = {
                "reason":"Subscription ID is not valid"
            }
            denied = time.time() *1000
            print("Sending response denied: %f ms" %denied)
            print("Full message processing time: %f ms" %(denied-start))
            return ConnexionResponse(
                status_code=codes[1],
                content_type='application/json',
                headers={"Location": uniSubId},
                body=response_data)
        
def DeleteUnicastSubscription(uniSubId):
    global cursor, db, subs_database
    start = time.time() * 1000
    codes = [200, 400, 401, 404, 411, 429, 500, 503]
    subtype = "unicast-subscription"

    try:
        auth_token = request.headers['Authorization'].split(" ")[1]
        #location = kwargs.get("request").headers['Location']
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}

    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        headers = {"Authorization":auth_token, "Location": uniSubId}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )

    sql = "DELETE FROM "+ TABLENAME +" WHERE address = %s AND subType = %s"
    val = (uniSubId, subtype)
    print(sql % val)
    cursor.execute(sql, val)
    db.commit()
    print(cursor.rowcount, "record(s) deleted") # To test, that only 1 line is entry is deleted
    if (cursor.rowcount > 0):
        response_data = {}
        subs_database.pop(uniSubId)
        return ConnexionResponse(
            status_code=codes[0],
            content_type='application/json',
            headers={"Location": uniSubId},
            body=response_data)
    else:
        print("The uniSubId (%s) is not valid."%uniSubId)
        response_data = {
            "reason":"Subscription ID is not valid"
        }
        denied = time.time() *1000
        print("Sending response denied: %f ms" %denied)
        print("Full message processing time: %f ms" %(denied-start))
        return ConnexionResponse(
            status_code=codes[1],
            content_type='application/json',
            headers={"Location": uniSubId},
            body=response_data)



#TSC stream it is not needed they are empty. This is to avoid error/warning for no function found for their operation id
def GetTscStreamAvailability():
    return 200

def GetTscStream():
    return 200

def GetTscStreamData():
    return 200

def PutTscStream():
    return 200

def DeleteTscStream():
    return 200
###########################################################x




#LocationReporting
def CreateLocReportingConfig(body):
    global cursor, db, loc_rep_database,enodeB_database
    codes = [201, 400, 401, 404, 411, 429, 500, 503]
    start = time.time() * 1000
    subtype = "location-reporting"

    #print(request)
    try:
        auth_token = request.headers['authorization'].split(" ")[1]
        #location = kwargs.get("request").headers['Location']
        #body = kwargs.get("body")
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}
    
    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        headers = {"Authorization":auth_token}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )
    

    accepted = time.time()

    response_data = {
        "valServerId" : "",
        "valTgtUe" : {
            "valUserId": "",
            "valUeId": "",
        },
    }

    if ("valServerId" in body):
        response_data['valServerId'] = body['valServerId']
    if ("valTgtUe" in body):
        response_data['valTgtUe'] = body['valTgtUe']
    if ("immRep" in body):
        response_data['immRep'] = body['immRep']
    if ("monDur" in body):
        response_data['monDur'] = body['monDur']
    if ("repPeriod" in body):
        response_data['repPeriod'] = body['repPeriod']
    if ("accuracy" in body):
        response_data['accuracy'] = body['accuracy']
    if ("suppFeat" in body):
        response_data['suppFeat'] = body['suppFeat']

    print("\n----------------------")
    print(response_data)
    print("----------------------\n")


    
    if (len(json.dumps(response_data)) > (LOCATION_MAX_LENGTH-2)):
        print("Response too long: %d"%len(json.dumps(response_data)))
        response_data = {"reason":"From request the generated response is too long"}
        return ConnexionResponse(
        status_code=codes[1],
        content_type='application/json',
        #headers={"Location": multiSubId},
        body=response_data)
    else:
        N = random.randint(MAXIMUM_LOCATION_ID,MAXIMUM_LOCATION_ID)
        configurationId = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
        # Make sure groupDocId generated is not used
        sql = "SELECT * FROM "+TABLE_LOCATION+" WHERE address = %s"
        while(cursor.execute(sql, (configurationId,)) is not None):
            print("Subscription ID is in use. Creating new ID...")
            configurationId = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

        response_data['resUri'] = "https://"+IPAddr+":"+str(AppPort)+"/ss-lr/v1/group-documents/"+configurationId
        print(response_data['resUri'])

        loc_rep_database[configurationId]  = {
            "locReq": response_data,
            "subType": subtype,
            "timestamp":datetime.datetime.now()
        }       

        
        gps = None# if level == "B/s" or level == "b/s":
    #     speed = round(speed/1000/1000, 2)
    # elif level == "KB/s" or level == "kb/s" or level == "kB/s":
    #     speed = round(speed/1000, 2)
    # else:
    #     speed = round(speed, 2)
        dist = None
        ##Set current location, calculate distance and set delay
        #i = random.randint(1,len(enodeB_database)-1) #Randomly set new location
        home_gps_loc = {"lat": enodeB_database[0]['lat'], "lon": enodeB_database[0]['lon']}

        ##Set current location, calculate distance and set delay
        if (body['accuracy'] == 'cellid'):
            valuser_current_loc_database[configurationId] = {"accuracy":"cellid", 
                                                                "locInfo" : {
                                                                    "cellid":enodeB_database[1]['cellid'],
                                                                },
                                                                "datetime":datetime.datetime.now(),
                                                            }
            gps = cellid_to_gps({"cellid": valuser_current_loc_database[configurationId]['cellid']})
            dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
        elif (body['accuracy'] == 'ENODEB'):
            valuser_current_loc_database[configurationId] = {"accuracy":"ENODEB",
                                                                "locInfo": {
                                                                    "enodeBId": enodeB_database[1]['enodeBId']
                                                                    },
                                                                "datetime":datetime.datetime.now(),
                                                                }
            gps = enodeb_to_gps({'enodeBId': valuser_current_loc_database[configurationId]['locInfo']['enodeBId']})
            dist = dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
        elif (body['accuracy'] == 'GEO_AREA'):
            valuser_current_loc_database[configurationId] = {"accuracy":"GEO_AREA", 
                                                                "locInfo": {
                                                                    "geographicArea": {
                                                                        "point":{
                                                                            "lat": enodeB_database[1]['lat'], 
                                                                            "lon": enodeB_database[1]['lon']
                                                                            },
                                                                        "shape" : "POINT",
                                                                        }
                                                                    },
                                                                "datetime":datetime.datetime.now(),     
                                                            }
            gps = valuser_current_loc_database[configurationId]['locInfo']['geographicArea']['point']
            dist = calculate_gps_dist_for_small_range(valuser_current_loc_database[configurationId]['locInfo']['geographicArea']['point'], home_gps_loc)
        else:
            valuser_current_loc_database[configurationId] = {"accuracy":"GEO_AREA", 
                                                                "locInfo": {
                                                                    "geographicArea": {
                                                                        "point":{
                                                                            "lat": enodeB_database[1]['lat'], 
                                                                            "lon": enodeB_database[1]['lon']
                                                                            },
                                                                        "shape" : "POINT",
                                                                        }
                                                                    },
                                                                    "datetime":datetime.datetime.now(),
                                                            }
            gps = valuser_current_loc_database[configurationId]['locInfo']['geographicArea']['point']
            dist = calculate_gps_dist_for_small_range(valuser_current_loc_database[configurationId]['locInfo']['geographicArea']['point'], home_gps_loc)
        #Since only valid ids and locations can be set here, this part is not needed
        # if gps == None or dist == None:
        #     print("The Location is unknown.")
        #     response_data = {
        #         "reason":"Location is not valid or unknown"
        #     }
        #     denied = time.time() *1000
        #     print("Sending response denied: %f ms" %denied)
        #     print("Full message processing time: %f ms" %(denied-start))
        #     return ConnexionResponse(
        #         status_code=codes[1],
        #         content_type='application/json',
        #         headers={"Location": configurationId},
        #         body=response_data) 
        
        # if (body['accuracy'] == 'ENODEB'):
        #     valuser_current_loc_database[configurationId] = {"accuracy":"ENODEB", 
        #                                                      "cellid":enodeB_database[1]['cellid']}
        #     gps = cellid_to_gps({"cellid": valuser_current_loc_database[configurationId]['cellid']})
        #     dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
        # elif (body['accuracy'] == 'GEO_AREA'):
        #     valuser_current_loc_database[configurationId] = {"accuracy":"GEO_AREA", 
        #                                                      "geo_loc": {
        #                                                          "point":{
        #                                                                 "lat":enodeB_database[1]['lat'], 
        #                                                                 "lon": enodeB_database[1]['lon']
        #                                                                 },
        #                                                             "shape" : "POINT",}}
        #     dist = calculate_gps_dist_for_small_range(valuser_current_loc_database[configurationId]['locInfo']['geo_loc']['point'], home_gps_loc)
        # else:
        #     valuser_current_loc_database[configurationId] = {"accuracy":"GEO_AREA", 
        #                                                      "geo_loc": {
        #                                                          "point":{
        #                                                                 "lat":enodeB_database[1]['lat'], 
        #                                                                 "lon": enodeB_database[1]['lon']
        #                                                                 },
        #                                                             "shape" : "POINT",}}
        #     dist = calculate_gps_dist_for_small_range(valuser_current_loc_database[configurationId]['locInfo']['geo_loc']['point'], home_gps_loc)
        
        delay = distance_delay(dist, 'miles')
        res = socket_send({
            "min_con": "delay",
            "delay": delay,
            "delay_ext": "ms"
        })
        if (res < 200):
            if (res == -2):
                print("Error while trying to set delay: Client socket failed to create connection to server")
            elif (res == -1):
                print("Error while trying to set delay: Unsupported request")
            elif (res == -300):
                print("Error while trying to set delay: Wrong type")




        sql = "INSERT INTO "+TABLE_LOCATION+" (address, locationReportingRequest, subType) VALUES (%s, %s, %s)"
        val = ( configurationId, json.dumps(response_data), subtype)
        response_data = json.dumps(response_data)
        
        print("CREATE FIRST ENTRY.")
        cursor.execute(sql, val)
        db.commit()

        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print(tables)

        end = time.time() * 1000
        print("Received request: %f ms" %start)
        print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
        print("Sending response: %f ms" %end)
        print("Full message processing time: %f ms" %(end-start))


        return ConnexionResponse(
                status_code=codes[0],
                content_type='application/json',
                headers={"Location":configurationId},
                body=response_data)

def RetrieveLocReportingConfig(configurationId):
    global cursor, loc_rep_database
    start = time.time() * 1000
    codes = [200, 400, 401, 404, 411, 429, 500, 503]
    subtype = "location-reporting"

    try:
        auth_token = request.headers['Authorization'].split(" ")[1]
        #location = kwargs.get("request").headers['Location']
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}

    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        headers = {"Authorization":auth_token, "Location": configurationId}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )

    if (configurationId in loc_rep_database):
        response_data =  loc_rep_database[configurationId]['locReq']
        headers = {"Authorization":auth_token, "Location": configurationId}
        return ConnexionResponse(
                status_code=codes[0],
                content_type='application/json',
                headers=headers,
                body=response_data
        )

    sql = "SELECT * FROM "+TABLE_LOCATION+" WHERE address = %s AND subType = %s"
    val = (configurationId, subtype)
    cursor.execute(sql,  val)
    search = cursor.fetchall()
    if (search):
        if (search[0][0] != configurationId):
            print("Wrong entry, address doesn't match configurationId(%s)"%configurationId)
        if (search[0][2] != subtype):
            print("Wrong subscription type... (not \"%s\")"%subtype)
        accepted = time.time() * 1000
        response_data = search[0][1]
        print("\n----------------")
        print(response_data)
        print("----------------\n")

        headers = {"Location": configurationId}
        content_type = "application/json"

        end = time.time() * 1000
        print("Received request: %f ms" %start)
        print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
        print("Sending response: %f ms" %end)
        print("Full message processing time: %f ms" %(end-start))

        return ConnexionResponse(
            status_code=codes[0],
            content_type=content_type,
            headers={"Location": configurationId},
            body=response_data)
    else:
        print("The configurationId (%s) is not valid."%configurationId)
        response_data = {
            "reason":"Subscription ID is not valid"
        }
        denied = time.time() *1000
        print("Sending response denied: %f ms" %denied)
        print("Full message processing time: %f ms" %(denied-start))
        return ConnexionResponse(
            status_code=codes[1],
            content_type='application/json',
            headers={"Location": configurationId},
            body=response_data)

def UpdateLocReportingConfig(configurationId,body):
    global cursor, db, loc_rep_database, enodeB_database
    codes = [200, 400, 401, 404, 411, 429, 500, 503]
    valGroupId_loc = "96be8d4d422dd4f90eefd4ace1e4b8"
    start = time.time() * 1000
    subtype = "location-reporting"


    try:
        auth_token = request.headers['authorization'].split(" ")[1]
        #location = kwargs.get("request").headers['Location']
        #body = kwargs.get("body")
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}
    
    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        headers = {"Authorization":auth_token}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )
    
    response_data = {
        "valServerId" : "",
        "valTgtUe" : {
            "valUserId": "",
            "valUeId": "",
        },
    }


    if ("valServerId" in body):
        response_data['valServerId'] = body['valServerId']
    if ("valTgtUe" in body):
        response_data['valTgtUe'] = body['valTgtUe']
    if ("immRep" in body):
        response_data['immRep'] = body['immRep']
    if ("monDur" in body):
        response_data['monDur'] = body['monDur']
    if ("repPeriod" in body):
        response_data['repPeriod'] = body['repPeriod']
    if ("accuracy" in body):
        response_data['accuracy'] = body['accuracy']
    if ("suppFeat" in body):
        response_data['suppFeat'] = body['suppFeat']

    print("\n----------------------")
    print(response_data)
    print("----------------------\n")
    
    
    
    sql = "SELECT * FROM "+ TABLE_LOCATION +" WHERE address = %s AND subType = %s;"
    val = (configurationId, subtype)
    cursor.execute(sql,  val)
    search = cursor.fetchall()
    print(search)
    
    if (search and (len(configurationId)>=MINIMUM_LOCATION_ID and len(configurationId) <= MAXIMUM_LOCATION_ID)):
        accepted = time.time() *1000 
        sql = "UPDATE "+ TABLE_LOCATION +" SET locationReportingRequest = %s WHERE address = %s AND subType = %s"
        val = (json.dumps(response_data), configurationId,  subtype)

        
        if (len(json.dumps(response_data)) > (LOCATION_MAX_LENGTH-2)):
            print("Response too long: %d"%len(json.dumps(response_data)))
            response_data = {"reason":"From request the generated response is too long"}
            return ConnexionResponse(
            status_code=codes[1],
            content_type='application/json',
            body=response_data)
        else:
            print("UPDATE ENTRY.")
            cursor.execute(sql, val)
            db.commit()
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print(tables)


        gps = None
        dist = None
        ##Set current location, calculate distance and set delay
        i = random.randint(1,len(enodeB_database)-1) #Randomly set new location
        home_gps_loc = {"lat": enodeB_database[0]['lat'], "lon": enodeB_database[0]['lon']}


        ##Set current location, calculate distance and set delay
        if (body['accuracy'] == 'cellid'):
            valuser_current_loc_database[configurationId] = {"accuracy":"cellid", 
                                                                "locInfo" : {
                                                                    "cellid":enodeB_database[i]['cellid'],
                                                                },
                                                                "timestamp":datetime.datetime.now(),
                                                            }
            gps = cellid_to_gps({"cellid": valuser_current_loc_database[configurationId]['cellid']})
            dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
        elif (body['accuracy'] == 'ENODEB'):
            valuser_current_loc_database[configurationId] = {"accuracy":"ENODEB",
                                                                "locInfo": {
                                                                    "enodeBId": enodeB_database[i]['enodeBId']
                                                                    },
                                                                "timestamp":datetime.datetime.now(),
                                                                }
            gps = enodeb_to_gps({'enodeBId': valuser_current_loc_database[configurationId]['locInfo']['enodeBId']})
            dist = dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
        elif (body['accuracy'] == 'GEO_AREA'):
            valuser_current_loc_database[configurationId] = {"accuracy":"GEO_AREA", 
                                                                "locInfo": {
                                                                    "geographicArea": {
                                                                        "point":{
                                                                            "lat":enodeB_database[i]['lat'], 
                                                                            "lon": enodeB_database[i]['lon']
                                                                            },
                                                                        "shape" : "POINT",
                                                                        }
                                                                    },     
                                                                "timestamp":datetime.datetime.now(),
                                                            }
            gps = valuser_current_loc_database[configurationId]['locInfo']['geographicArea']['point']
            dist = calculate_gps_dist_for_small_range(valuser_current_loc_database[configurationId]['locInfo']['geographicArea']['point'], home_gps_loc)
        else:
            valuser_current_loc_database[configurationId] = {"accuracy":"GEO_AREA", 
                                                                "locInfo": {
                                                                    "geographicArea": {
                                                                        "point":{
                                                                            "lat":enodeB_database[i]['lat'], 
                                                                            "lon": enodeB_database[i]['lon']
                                                                            },
                                                                        "shape" : "POINT",
                                                                        }
                                                                    },
                                                                "timestamp":datetime.datetime.now(),
                                                            }
            gps = valuser_current_loc_database[configurationId]['locInfo']['geographicArea']['point']
            dist = calculate_gps_dist_for_small_range(valuser_current_loc_database[configurationId]['locInfo']['geographicArea']['point'], home_gps_loc)
        #Since only valid ids and locations can be set here, this part is not needed
        # if gps == None or dist == None:
        #     print("The Location is unknown.")
        #     response_data = {
        #         "reason":"Location is not valid or unknown"
        #     }
        #     denied = time.time() *1000
        #     print("Sending response denied: %f ms" %denied)
        #     print("Full message processing time: %f ms" %(denied-start))
        #     return ConnexionResponse(
        #         status_code=codes[1],
        #         content_type='application/json',
        #         headers={"Location": configurationId},
        #         body=response_data) 


        # if (body['accuracy'] == 'ENODEB'):
        #     valuser_current_loc_database[configurationId] = {"accuracy":"ENODEB", 
        #                                                      "cellid":enodeB_database[i]['cellid']}
        #     gps = cellid_to_gps({"cellid": valuser_current_loc_database[configurationId]['cellid']})
        #     dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
        # elif (body['accuracy'] == 'GEO_AREA'):
        #     valuser_current_loc_database[configurationId] = {"accuracy":"GEO_AREA", 
        #                                                      "geo_loc": {
        #                                                          "point":{
        #                                                                 "lat":enodeB_database[i]['lat'], 
        #                                                                 "lon": enodeB_database[i]['lon']
        #                                                                 },
        #                                                             "shape" : "POINT",}}
        #     dist = calculate_gps_dist_for_small_range(valuser_current_loc_database[configurationId]['locInfo']['geo_loc']['point'], home_gps_loc)
        # else:
        #     valuser_current_loc_database[configurationId] = {"accuracy":"GEO_AREA", 
        #                                                      "geo_loc": {
        #                                                          "point":{
        #                                                                 "lat":enodeB_database[i]['lat'], 
        #                                                                 "lon": enodeB_database[i]['lon']
        #                                                                 },
        #                                                             "shape" : "POINT",}}
        #     dist = calculate_gps_dist_for_small_range(valuser_current_loc_database[configurationId]['locInfo']['geo_loc']['point'], home_gps_loc)
        
        delay = distance_delay(dist, "kilometer")
        res = socket_send({
            "min_con": "delay",
            "delay": delay,
            "delay_ext": "ms"
        })
        if (res < 200):
            if (res == -2):
                print("Error while trying to set delay: Client socket failed to create connection to server")
            elif (res == -1):
                print("Error while trying to set delay: Unsupported request")
            elif (res == -300):
                print("Error while trying to set delay: Wrong type")

        loc_rep_database[configurationId]['locReq'].update(response_data)
        loc_rep_database[configurationId]["timestamp"] = datetime.datetime.now()
        

        end = time.time() * 1000
        print("Received request: %f ms" %start)
        print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
        print("Sending response: %f ms" %end)
        print("Full message processing time: %f ms" %(end-start))


        return ConnexionResponse(
                status_code=codes[0],
                content_type='application/json',
                headers={"Location":configurationId},
                body=body)
    else:
            print("The configurationId (%s) is not valid."%configurationId)
            response_data = {
                "reason":"Location is not valid"
            }
            denied = time.time() *1000
            print("Sending response denied: %f ms" %denied)
            print("Full message processing time: %f ms" %(denied-start))
            return ConnexionResponse(
                status_code=codes[1],
                content_type='application/json',
                headers={"Location": configurationId},
                body=response_data) 

def ModifyLocReportingConfig(configurationId,body):
    global cursor, db, loc_rep_database, enodeB_database
    codes = [200, 400, 401, 404, 411, 429, 500, 503]
    valGroupId_loc = "96be8d4d422dd4f90eefd4ace1e4b8"
    start = time.time() * 1000
    subtype = "location-reporting"


    try:
        auth_token = request.headers['authorization'].split(" ")[1]
        #location = kwargs.get("request").headers['Location']
        #body = kwargs.get("body")
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}
    
    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        headers = {"Authorization":auth_token}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )


    
    sql = "SELECT * FROM "+ TABLE_LOCATION +" WHERE address = %s AND subType = %s"
    val = (configurationId, subtype)
    cursor.execute(sql,  val)
    search = cursor.fetchall()
    if (search):
        #print(search[0])
        if (search[0][0] != configurationId):
            print("Wrong entry, address doesn't match groupDocId(%s)"%configurationId)
        elif (search[0][2] != subtype):
            print("Wrong subscription type... (not \"%s\")"%subtype)
        else:
            accepted = time.time() * 1000
            response_data = search[0][1]
            response_data = json.loads(response_data)



            if ("valTgtUe" in body):
                response_data['valTgtUe'] = body['valTgtUe']
            if ("monDur" in body):
                response_data['monDur'] = body['monDur']
            if ("repPeriod" in body):
                response_data['repPeriod'] = body['repPeriod']
            if ("accuracy" in body):
                response_data['accuracy'] = body['accuracy']
            

            print("\n-----MODIFIED-----------")
            print(response_data)
            print("----------------\n")

            #print(search[0][0]==groupDocId)
            headers = {"Location": configurationId}
            content_type = {"Content-Type": "application/json"}

            
            sql = "UPDATE "+ TABLE_LOCATION +" SET locationReportingRequest = %s WHERE address = %s AND subType = %s"
            val = (json.dumps(response_data), configurationId, subtype)

            
            if (len(json.dumps(response_data)) > (VALGORUP_MAX_LENGTH-2)):
                print("Response too long: %d"%len(json.dumps(response_data)))
                response_data = {"reason":"From request the generated response is too long"}
                return ConnexionResponse(
                status_code=codes[1],
                content_type='application/json',
                #headers={"Location": groupDocId},
                body=response_data)
            else:
                print("PATCH ENTRY.")
                cursor.execute(sql, val)
                db.commit()
                print("UPDATE: ",cursor.rowcount, "record(s) affected") 
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()
                print(tables)


            end = time.time() * 1000
            print("Received request: %f ms" %start)
            print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
            print("Sending response: %f ms" %end)
            print("Full message processing time: %f ms" %(end-start))


            gps = None
            dist = None
            ##Set current location, calculate distance and set delay
            i = random.randint(1,len(enodeB_database)-1) #Randomly set new location
            home_gps_loc = {"lat": enodeB_database[0]['lat'], "lon": enodeB_database[0]['lon']}


            ##Set current location, calculate distance and set delay
            if (body['accuracy'] == 'cellid'):
                valuser_current_loc_database[configurationId] = {"accuracy":"cellid", 
                                                                    "locInfo" : {
                                                                        "cellid":enodeB_database[i]['cellid'],
                                                                    },
                                                                    "timestamp":datetime.datetime.now(),
                                                                }
                gps = cellid_to_gps({"cellid": valuser_current_loc_database[configurationId]['cellid']})
                dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
            elif (body['accuracy'] == 'ENODEB'):
                valuser_current_loc_database[configurationId] = {"accuracy":"ENODEB",
                                                                    "locInfo": {
                                                                        "enodeBId": enodeB_database[i]['enodeBId']
                                                                        },
                                                                    "timestamp":datetime.datetime.now(),
                                                                    }
                gps = enodeb_to_gps({'enodeBId': valuser_current_loc_database[configurationId]['locInfo']['enodeBId']})
                dist = dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
            elif (body['accuracy'] == 'GEO_AREA'):
                valuser_current_loc_database[configurationId] = {"accuracy":"GEO_AREA", 
                                                                    "locInfo": {
                                                                        "geographicArea": {
                                                                            "point":{
                                                                                "lat":enodeB_database[i]['lat'], 
                                                                                "lon": enodeB_database[i]['lon']
                                                                                },
                                                                            "shape" : "POINT",
                                                                            }
                                                                        },
                                                                    "timestamp":datetime.datetime.now(),
                                                                }
                gps = valuser_current_loc_database[configurationId]['locInfo']['geographicArea']['point']
                dist = calculate_gps_dist_for_small_range(valuser_current_loc_database[configurationId]['locInfo']['geographicArea']['point'], home_gps_loc)
            else:
                valuser_current_loc_database[configurationId] = {"accuracy":"GEO_AREA", 
                                                                    "locInfo": {
                                                                        "geographicArea": {
                                                                            "point":{
                                                                                "lat":enodeB_database[i]['lat'], 
                                                                                "lon": enodeB_database[i]['lon']
                                                                                },
                                                                            "shape" : "POINT",
                                                                            }
                                                                        },
                                                                    "timestamp":datetime.datetime.now(),
                                                                }
                gps = valuser_current_loc_database[configurationId]['locInfo']['geographicArea']['point']
                dist = calculate_gps_dist_for_small_range(valuser_current_loc_database[configurationId]['locInfo']['geographicArea']['point'], home_gps_loc)
            #Since only valid ids and locations can be set here, this part is not needed
            # if gps == None or dist == None:
            #     print("The Location is unknown.")
            #     response_data = {
            #         "reason":"Location is not valid or unknown"
            #     }
            #     denied = time.time() *1000
            #     print("Sending response denied: %f ms" %denied)
            #     print("Full message processing time: %f ms" %(denied-start))
            #     return ConnexionResponse(
            #         status_code=codes[1],
            #         content_type='application/json',
            #         headers={"Location": configurationId},
            #         body=response_data) 

            
            delay = distance_delay(dist, 'kilometer')
            res = socket_send({
                "min_con": "delay",
                "delay": delay,
                "delay_ext": "ms"
            })
            if (res < 200):
                if (res == -2):
                    print("Error while trying to set delay: Client socket failed to create connection to server")
                elif (res == -1):
                    print("Error while trying to set delay: Unsupported request")
                elif (res == -300):
                    print("Error while trying to set delay: Wrong type")

            loc_rep_database[configurationId]['locReq'].update(response_data)
            loc_rep_database[configurationId]["timestamp"]= datetime.datetime.now()

            return ConnexionResponse(
                    status_code=codes[0],
                    content_type='application/json',
                    headers={"Location":configurationId},
                    body=body)
    else:
            print("The groupDocID (%s) is not valid."%configurationId)
            response_data = {
                "reason":"Location is not valid"
            }
            denied = time.time() *1000
            print("Sending response denied: %f ms" %denied)
            print("Full message processing time: %f ms" %(denied-start))
            return ConnexionResponse(
                status_code=codes[1],
                content_type='application/json',
                headers={"Location": configurationId},
                body=response_data) 

def DeleteLocReportingConfig(configurationId):
    global cursor, db, loc_rep_database
    start = time.time() * 1000
    codes = [200, 400, 401, 404, 411, 429, 500, 503]
    subType = "location-reporting"

    try:
        auth_token = request.headers['Authorization'].split(" ")[1]
        #location = kwargs.get("request").headers['Location']
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}

    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        headers = {"Authorization":auth_token, "Location": configurationId}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )

    sql = "DELETE FROM "+ TABLE_LOCATION +" WHERE address = %s AND subType = %s"
    val = (configurationId, subType)
    cursor.execute(sql,  val)
    db.commit()
    print(cursor.rowcount, "record(s) deleted") # To test, that only 1 line is entry is deleted
    if (cursor.rowcount > 0):
        response_data = {}


        ##Check if it is in the local variables
        if (loc_rep_database[configurationId]):
            loc_rep_database.pop(configurationId)
        ##Delete asigned location - not necessary, just reduce size of variable
        if (valuser_current_loc_database[configurationId]):
            valuser_current_loc_database.pop(configurationId)
        
        return ConnexionResponse(
            status_code=codes[0],
            content_type='application/json',
            headers={"Location": configurationId},
            body=response_data)
    else:
        print("The configurationId (%s) is not valid."%configurationId)
        response_data = {
            "reason":"Subscription ID is not valid"
        }
        denied = time.time() *1000
        print("Sending response denied: %f ms" %denied)
        print("Full message processing time: %f ms" %(denied-start))
        return ConnexionResponse(
            status_code=codes[1],
            content_type='application/json',
            headers={"Location": configurationId},
            body=response_data)



#LocationAreaInfoRetrieval
def RetrieveUeLocInfo(location_info, range):
    global cursor, db, enodeB_database, subs_database, group_database, vlan_group_connection, loc_rep_database
    codes = [201, 400, 401, 404, 411, 429, 500, 503]
    start = time.time() * 1000
    subtype = "location-Area-Info-Ret"

    #print(request)
    try:
        auth_token = request.headers['authorization'].split(" ")[1]
        #location = kwargs.get("request").headers['Location']
        #body = kwargs.get("body")
        print("Auth token: "+auth_token+"\n")
    except:
        print("Auth token or request body missing...\n")
        return {}, codes[1], {"Content-Type": "application/json"}
    
    if (auth_token != TOKEN):
        print("Unauthorized token")
        response_data = {"reason":"Not authorized"}
        headers = {"Authorization":auth_token}
        return ConnexionResponse(
                status_code=codes[2],
                content_type='application/json',
                headers=headers,
                body=response_data
        )
    
    # print(location_info)
    location_info = json.loads(location_info)
    # print(location_info)
    print(range)

    req_data = {
        "location-info":request.query["location-info"],
        "range": request.query["range"] #float(50.12) #The range information over which the UE(s) information is required, expressed in meters.
    }
    # print(req_data)

    accepted = time.time()
    # response_data = []
    # example_resp = [{
    #         "valTgtUe": {
    #             "valUserId":"string",
    #             "valUeId":"string",
    #         },
    #         "locInfo": {
    #             # "ageOfLocation":time.time()*1000,
    #             "cellId": "1240838",
    #             # "enodeBId": "4847",
    #             # "routingAreaId":"",
    #             # "trackingAreaId":"",
    #             # "plmnId":"",
    #             # "twanId":"",
    #             # "geographicArea":"",
    #             # "civicAddress":"",
    #             # "positionMethod":"",
    #             # "qosFulfilInd":"",
    #             # "ueVelocity":"",
    #             # "ldrType":"",
    #             # "achievedQos":""
    #         },
    #         "timeStamp":time.time()*1000,
    #         "valSvcId":"string" # Identity of the VAL service
    #     }]

    # response_data['locInfo'] = req_data['location-info']
    response_data = []

    ##TODO
    ### Get all valUsers in the area
    ## Similar to locationReport (it registers the data regularly reported by user)
    ## Get location and 

    for id in valuser_current_loc_database.keys():
        # for record in valuser_current_loc_database[id]:
            try:
                check_area = json.loads(request.query_params['location-info'])
            except:
                check_area = request.query_params['location-info']

            # if check_area['positionMethod'] == "enodeBId":
            if check_area['positionMethod'] == "ECID":
                home_gps_loc = enodeb_to_gps(check_area["enodeBId"])
                
            # elif check_area['positionMethod'] == "routingAreaId":
            elif check_area['positionMethod'] == "NETWORK_SPECIFIC" and 'routingAreaId' in check_area.keys():
                home_gps_loc = {"lat": enodeB_database[2]['lat'], "lon": enodeB_database[2]['lon']}

            # elif check_area['positionMethod'] == "trackingAreaId":
            elif check_area['positionMethod'] == "NETWORK_SPECIFIC" and 'trackingAreaId' in check_area.keys():
                home_gps_loc = {"lat": enodeB_database[2]['lat'], "lon": enodeB_database[2]['lon']}

            # elif check_area['positionMethod'] == "plmnId":
            elif check_area['positionMethod'] == "NR_ECID":
                home_gps_loc = {"lat": enodeB_database[2]['lat'], "lon": enodeB_database[2]['lon']}

            # elif check_area['positionMethod'] == "twanId":
            elif check_area['positionMethod'] == "WLAN":
                home_gps_loc = {"lat": enodeB_database[2]['lat'], "lon": enodeB_database[2]['lon']}

            # elif check_area['positionMethod'] == "geographicArea":
            elif check_area['positionMethod'] == "OTDOA":
                home_gps_loc = check_area['geographicArea']

            # elif check_area['positionMethod'] == "civicAddress":
            elif check_area['positionMethod'] == "CIVIC_LOOKUP":
                home_gps_loc = {"lat": enodeB_database[2]['lat'], "lon": enodeB_database[2]['lon']}
            
            else:
                home_gps_loc = {"lat": enodeB_database[2]['lat'], "lon": enodeB_database[2]['lon']}
            
            


            #Loc into saved locations and calculate distance from the LocationAreaInfoRetrieval center
            if (valuser_current_loc_database[id]['accuracy'] == 'cellid'):
                if valuser_current_loc_database[id]['cellid'].isdigit():
                    cellid = valuser_current_loc_database[id]['cellid']
                else:
                    mcc, mnc, region, cellid = valuser_current_loc_database[id]['cellid'].strip().split('-')
                #Here the mcc, mnc, region and cellid could be used to access a global location's gps coordinate 
                #delay calculation could be updated to check whether the distance is on a larger scale, like continental level
                gps = cellid_to_gps({"cellid": cellid})
                dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
            if (valuser_current_loc_database[id]['accuracy'] == 'enodeB'):
                gps = enodeb_to_gps({"enodeB": valuser_current_loc_database[id]['enodeBId']})
                dist = calculate_gps_dist_for_small_range(gps, home_gps_loc)
            elif (valuser_current_loc_database[id]['accuracy'] == 'GEO_AREA'):
                dist = calculate_gps_dist_for_small_range(valuser_current_loc_database[id]['locInfo']['geographicArea']['point'], home_gps_loc)

            else:
                dist = calculate_gps_dist_for_small_range(valuser_current_loc_database[id]['locInfo']['geographicArea']['point'], home_gps_loc)

            #Convert dist to meters if necessary, but everything should be in meters
            #calculate_gps_dist_for_small_range() is good for calculating short distance in meters
            #range is in meters
            resp = None
            
            
            
            #Check whether dist <= range is true: get nessary data #Response Must contain 'valTgtUe' and 'locInfo' minimum
            if dist <= request.query_params['range']:

                if id in subs_database.keys():
                    if 'uniQosReq' in subs_database[id]:
                        resp['valTgtUe'] = subs_database[id]['uniQosReq']['valTgtUe']

                        for key in loc_rep_database.keys():
                            if resp['valTgtUe'] in loc_rep_database[key]['locReq']['valTgtUe']:
                                resp['locInfo'] = valuser_current_loc_database[key]['loc_info']

                        if resp['locInfo'] == None or resp['locInfo'] == "":
                            resp['locInfo'] = valuser_current_loc_database[id]['locInfo']

                        if 'ageOfLocation' in subs_database[id]['uniQosReq']:
                            resp['timeStamp'] = subs_database[id]['uniQosReq']['timeStamp']

                        resp['valSvcId'] = subs_database[id]['uniQosReq']['valServiceIds']


                    if 'multiQosReq' in subs_database[id]:
                        for key in group_database.keys():
                            if subs_database[id]['multiQosReq']['valGroupId'] in group_database[key]['groupDocsRequest']:
                                #Must contain
                                resp['valTgtUe'] = group_database[key]['groupDocsRequest']['members']
                               
                                #Optional
                                if 'ageOfLocation' in subs_database[id]['multiQosReq'].keys():
                                    resp['timeStamp'] = subs_database[id]['multiQosReq']['duration']
                                #Optional
                                resp['valSvcId'] = group_database[key]['groupDocsRequest']['valServiceIds']

                                #Must contain
                                if 'locInfo' in subs_database[id]['multiQosReq'].keys():
                                    resp['locInfo'] = subs_database[id]['multiQosReq']['locInfo']
                                else:
                                    if 'locInfo' in group_database[key]['groupDocsRequest'].keys():
                                        resp['locInfo'] = group_database[key]['groupDocsRequest']['locInfo']
                                    else:
                                        resp["locInfo"] = valuser_current_loc_database[id]['locInfo']
                                break
                            
                if id in group_database.keys():
                    resp['valTgtUe'] = group_database[id]['groupDocsRequest']['members']
                    
                    if 'ageOfLocation' in group_database[id]['groupDocsRequest']['locInfo'].keys():
                        resp['timeStamp'] = group_database[id]['groupDocsRequest']['locInfo']['ageOfLocationInfo']
                    
                    if 'valServiceIds' in group_database[id]['groupDocsRequest'].keys():
                        resp['valSvcId'] = group_database[id]['groupDocsRequest']['valServiceIds']
                    
                    resp['locInfo'] = group_database[id]['groupDocsRequest']['locInfo']

                if id in loc_rep_database.keys():
                    resp['valTgtUe'] = loc_rep_database[id]['locReq']['valTgtUe']
                   
                    if 'duration' in loc_rep_database[id]['locReq'].keys():
                        resp['timeStamp'] = loc_rep_database[id]['locReq']['duration']
                    
                    if 'valServiceIds' in loc_rep_database[id]['locReq'].keys():
                        resp['valSvcId'] = loc_rep_database[id]['locReq']['valServiceIds']
                    
                    resp['locInfo'] = valuser_current_loc_database[id]['locInfo']

                if resp != None:
                    response_data.append(resp)
        


    end = time.time() * 1000
    print("Received request: %f ms" %start)
    print("Accepted request (setting bandwidth and forming response): %f ms" %accepted)
    print("Sending response: %f ms" %end)
    print("Full message processing time: %f ms" %(end-start))
    return ConnexionResponse(
            status_code=codes[0],
            content_type="application/json",
            body=response_data)


##Create the server
app = AsyncApp(__name__, specification_dir="connexion-example-master/")

##Add the required APIs
app.add_api("yaml/TS29549_SS_GroupManagement.yaml")
app.add_api("yaml/TS29549_SS_LocationReporting.yaml")
app.add_api("yaml/TS29549_SS_NetworkResourceAdaptation.yaml")
app.add_api("yaml/TS29549_SS_LocationAreaInfoRetrieval.yaml")


print("Waiting for first Network Resource Adaption request...")
try:
    if __name__ == '__main__':
        #Start server
        # app.run(f"{Path(__file__).stem}:app", port=AppPort)
        app.run(f"{Path(__file__).stem}:app", host=hostname , port=AppPort)

#User initiated shutdown with keyboard interrupt
except KeyboardInterrupt:
    print("CTRL-C: Exiting")
    # Close the client socket
    if (client_socket is not None) :
        print("Closing socket")
        client_socket.close()
    #Close db connection and cursor
    if db.is_connected():
        db.close()
        cursor.close()
        print("Database connection closed")



# Close the client socket
#client_socket.close()
#print("CTRL-C: Exiting")