import socket
import os
from connexion import AsyncApp, ConnexionMiddleware, request, App, request
from connexion.resolver import RelativeResolver
from connexion.context import context 
from pathlib import Path
from secrets import choice
import string
import random
# from connexion.options import SwaggerUIOptions
# # swagger_ui_options = SwaggerUIOptions(
# #     swagger_ui=True,
# #     swagger_ui_path="ui",
# # )

import time
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

DATABASE_NAME = "NetworkResourceDB"
TABLENAME = "subscriptions"
TABLE_GROUPMANAGEMENT = "GroupManagement"
TABLE_LOCATION = "LocationManagement"


#########################################################
#DATABASE CONNECTION: CREATE Database, Tables if necessary
db = None
cursor = None
try :
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="admin",
        password="Admin1Pass",
        database=DATABASE_NAME,
        auth_plugin='mysql_native_password'
    )
    cursor = db.cursor(buffered=True)
except:
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="admin",
        password="Admin1Pass",
        auth_plugin='mysql_native_password'
    )
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

if (not tables):
    cursor.execute("CREATE TABLE %s (address VARCHAR(%d), subscriptionRequest VARCHAR(%d), subType VARCHAR(60))" % (TABLENAME, MAXIMUM_SUB_ID,SUB_REQ_MAX_LENGHT))
    cursor.execute("CREATE TABLE %s (address VARCHAR(%d), valGroupId VARCHAR(60), groupDocsRequest VARCHAR(%d), subType VARCHAR(60))" % (TABLE_GROUPMANAGEMENT, MAXIMUM_VALGROUP,VALGORUP_MAX_LENGTH))
    cursor.execute("CREATE TABLE %s (address VARCHAR(%d), locationReportingRequest VARCHAR(%d), subType VARCHAR(60))" % (TABLE_LOCATION, MAXIMUM_LOCATION_ID, LOCATION_MAX_LENGTH))
else:
    #Check if some of the tables are missing
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



#########################################################
#Get IP address:port and define socket path, accepted TOKEN 
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
AppPort = 7777

# Define the path for the Unix socket
socket_path = '/tmp/mininet_control.s'
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImZvbyIsInBhc3N3b3JkIjoiYmFyIiwiaWF0IjoxNjY4MDg0NDI1fQ.lT4ABOQSHyJdIiF9rso06qcwrBkIxRFyolIgdBAI4l0"
PASSWD = {"admin": "secret", "foo": "bar"}
#########################################################




# This is not the socket server/mininet controller --> no need to remove UNIX socket path
# if os.path.exists(socket_path):       #Just in case later on someone wants change it
#      os.remove(socket_path)
client_socket = None
delay_bw = None
# Create a Unix socket
try:    
    client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) #socket.SOCK_STREAM
    client_socket.connect(socket_path)
    # Send a message to the server
    message = 'Hello from the client!'
    client_socket.sendall(message.encode())
    # # Receive a response from the server
    # response = client.recv(1024)
    # print(f'Received response: {response.decode()}')
except:
    print("Problem with connecting to the server")
    #client_socket = None


def printing_example(string):

    if type(string) is str:
        print(string)
    else:
        print("Not string input. Type: "+str(type(string)))
        print(type(string))
    pass

def socket_send(delay: int):
    global client_socket
    #print ("DELAY: "+str(delay))
    if (client_socket is not None):
        try:
            # Read data from the client
            msg = "L1 {}".format(delay)
            #client_socket.sendall(msg.encode())
            print("L1 %d" %delay)
        except Exception as e:
            print(f"Socket Error: {e}")
        # finally:
        #     try:
        #         client_socket.listen(1)
        #         datagram = client_socket.recv(1024)
        #         if datagram:
        #             print(datagram.strip().split())
        #     except Exception as error:
        #         print(f"Error during reading socket: {error}")
    else:
        print("client_socket failed to create connection")


#GroupManagement block
def CreateValGroupDoc(body):
    global cursor, db
    codes = [201, 400, 401, 404, 411, 429, 500, 503]
    valGroupId_loc = "96be8d4d422dd4f90eefd4ace1e4b8"
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
                "Location":"",
                "valGroupId": "",
                "grpDesc": "grpDesc",
                "members": [],
                "valGrpConf": "",
                "valServiceIds": [],
                "valSvcInf": "string",
                "suppFeat": "FFFF",
                "resUri": "https://"+IPAddr+":"+str(AppPort)+"/ss-gm/v1/group-documents/",
                "locInfo":"",
                "addLocInfo":"",
                "extGrpId":"",
                "com5GLanType":"",
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
        while(cursor.execute("SELECT * FROM %s WHERE address = '%s'"%(TABLE_GROUPMANAGEMENT,groupDocId)) is not None):
            print("Subscription ID is in use. Creating new ID...")
            groupDocId = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
        
        response_data['resUri'] = "https://"+IPAddr+":"+str(AppPort)+"/ss-gm/v1/group-documents/"+groupDocId
        response_data['Location'] = groupDocId

        sql = "INSERT INTO "+TABLE_GROUPMANAGEMENT+" (address, valGroupId, groupDocsRequest, subType) VALUES (%s, %s, %s, %s)"
        val = (groupDocId, response_data['valGroupId'], json.dumps(response_data), subtype)
        
        print("CREATE FIRST ENTRY.")
        cursor.execute(sql, val)
        db.commit()
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        response_data['Location'] = groupDocId
        print(tables)


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
    global cursor, db
    codes = [201, 400, 401, 404, 411, 429, 500, 503]
    valGroupId_loc = "96be8d4d422dd4f90eefd4ace1e4b8"
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
    resp = [{}]

    # sql = "SELECT * FROM %s WHERE address = '%s' AND subType = '%s' AND valGroupId = '%s'"
    # val = (TABLE_GROUPMANAGEMENT, val_service_id, subtype, val_group_id)
    sql = "SELECT * FROM %s WHERE subType = '%s' AND valGroupId = '%s'"
    val = (TABLE_GROUPMANAGEMENT, subtype, val_group_id)
    cursor.execute(sql % val)
    search = cursor.fetchall()
    i = 0
    if (search):
        accepted = time.time() * 1000
        for x in search:
            print(x)
            if (x[0] != val_service_id):
                a = 1
                #print("Wrong entry, address doesn't match val_service_id(%s)"%val_service_id)
            elif (x[3] != subtype):
                b = 1
                print("Wrong subscription type... (not '%s')"%subtype)
            elif (x[1] != val_group_id):
                print("Wrong entry, valGroupId doesn't match val_group_id(%s)"%val_group_id)
            elif (x[0] == val_service_id and x[1] == val_group_id):
                resp[i] = x[2]
                groupDocId = x[0]
                i+=1
        
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
            content_type="application/json",
            body=resp)
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
            body=resp)

def RetrieveIndValGroupDoc(groupDocId):
    global cursor
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

    sql = "SELECT * FROM %s WHERE address = '%s' AND subType = '%s'"
    val = (TABLE_GROUPMANAGEMENT, groupDocId, subtype)
    cursor.execute(sql % val)
    search = cursor.fetchall()
    if (search):
        #print(search[0])
        if (search[0][0] != groupDocId):
            print("Wrong entry, address doesn't match groupDocId(%s)"%groupDocId)
        elif (search[0][3] != subtype):
            print("Wrong subscription type... (not '%s')"%subtype)
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
    global cursor, db
    codes = [201, 400, 401, 404, 411, 429, 500, 503]
    valGroupId_loc = "96be8d4d422dd4f90eefd4ace1e4b8"
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
                    "Location":"",
                    "valGroupId": "",
                    "grpDesc": "",
                    "members": "",
                    "valGrpConf": "",
                    "valServiceIds": "",
                    "valSvcInf": "string",
                    "suppFeat": "FFFF",
                    "resUri": "https://"+IPAddr+":"+str(AppPort)+"/ss-gm/v1/group-documents/"
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
    
    
    
    sql = "SELECT * FROM %s WHERE address = '%s' AND subType = '%s';"
    val = (TABLE_GROUPMANAGEMENT, groupDocId, subtype)
    cursor.execute(sql % val)
    search = cursor.fetchall()
    
    if (search and (len(groupDocId)>=MINIMUM_VALGROUP and len(groupDocId) <= MAXIMUM_VALGROUP)):
        accepted = time.time() *1000 
        sql = "UPDATE %s SET groupDocsRequest = '%s' WHERE address = '%s' AND subType = '%s'"
        val = (TABLE_GROUPMANAGEMENT, json.dumps(response_data), groupDocId, subtype)

        
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
            cursor.execute(sql% val)
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

def ModifyIndValGroupDoc(groupDocId, body):
    global cursor, db
    codes = [201, 400, 401, 404, 411, 429, 500, 503]
    valGroupId_loc = "96be8d4d422dd4f90eefd4ace1e4b8"
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


    
    sql = "SELECT * FROM %s WHERE address = '%s' AND subType = '%s'"
    val = (TABLE_GROUPMANAGEMENT, groupDocId, subtype)
    cursor.execute(sql % val)
    search = cursor.fetchall()
    if (search):
        #print(search[0])
        if (search[0][0] != groupDocId):
            print("Wrong entry, address doesn't match groupDocId(%s)"%groupDocId)
        elif (search[0][3] != subtype):
            print("Wrong subscription type... (not '%s')"%subtype)
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


            sql = "SELECT * FROM %s WHERE address = '%s' AND subType = '%s'"
            val = (TABLE_GROUPMANAGEMENT, groupDocId, subtype)
            cursor.execute(sql % val)
            search = cursor.fetchall()
            db.commit()
            

            print("\n-----MODIFIED-----------")
            print(response_data)
            print("----------------\n")

            #print(search[0][0]==groupDocId)
            headers = {"Location": groupDocId}
            content_type = {"Content-Type": "application/json"}

            
            sql = "UPDATE %s SET groupDocsRequest = '%s' WHERE address = '%s' AND subType = '%s'"
            val = (TABLE_GROUPMANAGEMENT, json.dumps(response_data), groupDocId, subtype)

            
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
                cursor.execute(sql% val)
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
    global cursor, db
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

    sql = "DELETE FROM %s WHERE address = '%s' AND subType = '%s'"
    val = (TABLE_GROUPMANAGEMENT,groupDocId, subType)
    cursor.execute(sql % val)
    db.commit()
    print(cursor.rowcount, "record(s) deleted") # To test, that only 1 line is entry is deleted
    if (cursor.rowcount > 0):
        response_data = {}
        return ConnexionResponse(
            status_code=codes[0],
            content_type='application/json',
            headers={"Location": groupDocId},
            body=response_data)
    else:
        print("The multiSubId (%s) is not valid."%groupDocId)
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
    global delay_bw, cursor, db
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
    
    uplinkMaxBitRate: int 
    downlinkMaxBitRate: int
    accessToken: str
    print("Body: \n")
    print(body)
    print("\n")
    print(type(body))

    if ((location != None) and (location != "")):
        #if (len(location)>= MINIMUM_SUB_ID and len(location) < MAXIMUM_SUB_ID+1):
            #location is within expected range, but check if it is previously generated value
            multiSubId = location
            sql = "SELECT * FROM %s WHERE address = '%s' AND subType = '%s';"
            val = (TABLENAME, multiSubId, subtype)
            cursor.execute(sql % val)
            search = cursor.fetchall()
            print(sql)
            print(val)
            print(search)
            print("\n---------\n")
            # sql = "SHOW TABLES"
            # cursor.execute(sql)
            # print(cursor.fetchall())
            if((search) and (len(location)>=MINIMUM_SUB_ID and len(location) <= MAXIMUM_SUB_ID)):
                print("VALID multiSubId and search found entry....")
                accepted = time.time() * 1000
                #multiSubId = location
                sql = "UPDATE %s SET subscriptionRequest = '%s' WHERE address = '%s' AND subType = '%s'"
                val = (TABLENAME, json.dumps(body), multiSubId, subtype)
                print(sql%val)
                cursor.execute(sql % val)
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
        while(cursor.execute("SELECT * FROM %s WHERE address = '%s'"%(TABLENAME,multiSubId)) is not None):
            print("Subscription ID is in use. Creating new ID...")
            multiSubId = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

        print(json.dumps(body['multiQosReq']))
        multiQosReq = json.loads(body['multiQosReq'])
        uplinkMaxBitRate = int(multiQosReq['ulBW'])
        downlinkMaxBitRate = int(multiQosReq['dlBW'])
        #accessToken = body['Authorization']
        delay = int((uplinkMaxBitRate + downlinkMaxBitRate) / 0.95)
        print(str(delay)+" bit/s")
        

        #if accessToken == 'Bearer ' + TOKEN:
        if 1:
            socket_send(delay)
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

            sql = "INSERT INTO subscriptions (address, subscriptionRequest, subType) VALUES (%s, %s, %s)"
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
    global cursor
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

    sql = "SELECT * FROM %s WHERE address = '%s' AND subType = '%s'"
    val = (TABLENAME, multiSubId, subtype)
    cursor.execute(sql % val)
    search = cursor.fetchall()
    if (search):
        if (search[0][0] != multiSubId):
            print("Wrong entry, address doesn't match uniSubId(%s)"%multiSubId)
        if (search[0][2] != subtype):
            print("Wrong subscription type... (not '%s')"%subtype)
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
    global cursor, db
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

    sql = "DELETE FROM subscriptions WHERE address = '%s' AND subType = '%s'"
    val = (multiSubId, subType)
    cursor.execute(sql % val)
    db.commit()
    print(cursor.rowcount, "record(s) deleted") # To test, that only 1 line is entry is deleted
    if (cursor.rowcount > 0):
        response_data = {}
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
    global t, delay_bw, cursor, db
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
    
    uplinkMaxBitRate: int 
    downlinkMaxBitRate: int
    accessToken: str
    print("Body: \n")
    print(body)
    print("\n")
    print(type(body))

    if ((location != None) and (location != "")):
        #if (len(location)>= MINIMUM_SUB_ID and len(location) < MAXIMUM_SUB_ID+1):
            #location is within expected range, but check if it is previously generated value
            uniSubId = location
            sql = "SELECT * FROM %s WHERE address = '%s' AND subType = '%s';"
            val = (TABLENAME,uniSubId, subtype)
            cursor.execute(sql % val)
            search = cursor.fetchall()
            print(sql)
            print(val)
            print(search)
            print("\n---------\n")
            # sql = "SHOW TABLES"
            # cursor.execute(sql)
            # print(cursor.fetchall())
            if((search) and (len(location)>= MINIMUM_SUB_ID and len(location) <= MAXIMUM_SUB_ID)):
                print("VALID uniSubId and search found entry....")
                accepted = time.time() * 1000
                #uniSubId = location
                sql = "UPDATE %s SET subscriptionRequest = '%s' WHERE address = '%s' AND subType = '%s'"
                val = (TABLENAME, json.dumps(body), uniSubId, subtype)
                print(sql%val)
                cursor.execute(sql % val)
                db.commit()
                print(cursor.rowcount, "record(s) affected")
                # cursor.execute("SHOW TABLES;")
                # tables = cursor.fetchall()
                # print("TABLES: ")
                # print(tables[0])

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
        while(cursor.execute("SELECT * FROM %s WHERE address = '%s'"%(TABLENAME,uniSubId)) is not None):
            print("Subscription ID is in use. Creating new ID...")
            uniSubId = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

        print(json.dumps(body['uniQosReq']))
        uniQosReq = json.loads(body['uniQosReq'])
        uplinkMaxBitRate = int(uniQosReq['ulBW'])
        downlinkMaxBitRate = int(uniQosReq['dlBW'])
        #accessToken = body['Authorization']
        delay = int((uplinkMaxBitRate + downlinkMaxBitRate) / 0.95)
        print(str(delay)+" bit/s")
        

        #if accessToken == 'Bearer ' + TOKEN:
        if 1:
            socket_send(delay)
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

            sql = "INSERT INTO subscriptions (address, subscriptionRequest, subType) VALUES (%s, %s, %s)"
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
    global cursor
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

    sql = "SELECT * FROM %s WHERE address = '%s' AND subType = '%s'"
    val = (TABLENAME,uniSubId, subtype)
    cursor.execute(sql % val)
    search = cursor.fetchall()
    print(search)
    # print(type(search))
    # print(type(search[0]))

    if (search):
        if (search[0][0] != uniSubId):
            print("Wrong entry, address doesn't match uniSubId(%s)"%uniSubId)
        if (search[0][2] != subtype):
            print("Wrong subscription type... (not '%s')"%subtype)
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
    global cursor, db
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

    sql = "DELETE FROM %s WHERE address = '%s' AND subType = '%s'"
    val = (TABLENAME,uniSubId, subtype)
    print(sql%val)
    cursor.execute(sql % val)
    db.commit()
    print(cursor.rowcount, "record(s) deleted") # To test, that only 1 line is entry is deleted
    if (cursor.rowcount > 0):
        response_data = {}
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



#TSC stream it is not needed for now
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





#LocationReporting
def CreateLocReportingConfig(body):
    global cursor, db
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
        while(cursor.execute("SELECT * FROM %s WHERE address = '%s'"%(TABLE_LOCATION,configurationId)) is not None):
            print("Subscription ID is in use. Creating new ID...")
            configurationId = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

        response_data['resUri'] = "https://"+IPAddr+":"+str(AppPort)+"/ss-lr/v1/group-documents/"+configurationId
        print(response_data['resUri'])

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
    global cursor
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

    sql = "SELECT * FROM %s WHERE address = '%s' AND subType = '%s'"
    val = (TABLE_LOCATION, configurationId, subtype)
    cursor.execute(sql % val)
    search = cursor.fetchall()
    if (search):
        if (search[0][0] != configurationId):
            print("Wrong entry, address doesn't match configurationId(%s)"%configurationId)
        if (search[0][2] != subtype):
            print("Wrong subscription type... (not '%s')"%subtype)
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
    global cursor, db
    codes = [201, 400, 401, 404, 411, 429, 500, 503]
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
    
    
    
    sql = "SELECT * FROM %s WHERE address = '%s' AND subType = '%s';"
    val = (TABLE_LOCATION, configurationId, subtype)
    cursor.execute(sql % val)
    search = cursor.fetchall()
    print(search)
    
    if (search and (len(configurationId)>=MINIMUM_LOCATION_ID and len(configurationId) <= MAXIMUM_LOCATION_ID)):
        accepted = time.time() *1000 
        sql = "UPDATE %s SET locationReportingRequest = '%s' WHERE address = '%s' AND subType = '%s'"
        val = (TABLE_LOCATION, json.dumps(response_data), configurationId,  subtype)

        
        if (len(json.dumps(response_data)) > (LOCATION_MAX_LENGTH-2)):
            print("Response too long: %d"%len(json.dumps(response_data)))
            response_data = {"reason":"From request the generated response is too long"}
            return ConnexionResponse(
            status_code=codes[1],
            content_type='application/json',
            body=response_data)
        else:
            print("UPDATE ENTRY.")
            cursor.execute(sql% val)
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
    global cursor, db
    codes = [201, 400, 401, 404, 411, 429, 500, 503]
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


    
    sql = "SELECT * FROM %s WHERE address = '%s' AND subType = '%s'"
    val = (TABLE_LOCATION, configurationId, subtype)
    cursor.execute(sql % val)
    search = cursor.fetchall()
    if (search):
        #print(search[0])
        if (search[0][0] != configurationId):
            print("Wrong entry, address doesn't match groupDocId(%s)"%configurationId)
        elif (search[0][2] != subtype):
            print("Wrong subscription type... (not '%s')"%subtype)
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

            
            sql = "UPDATE %s SET locationReportingRequest = '%s' WHERE address = '%s' AND subType = '%s'"
            val = (TABLE_LOCATION, json.dumps(response_data), configurationId, subtype)

            
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
                cursor.execute(sql% val)
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
    global cursor, db
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

    sql = "DELETE FROM %s WHERE address = '%s' AND subType = '%s'"
    val = (TABLE_LOCATION, configurationId, subType)
    cursor.execute(sql % val)
    db.commit()
    print(cursor.rowcount, "record(s) deleted") # To test, that only 1 line is entry is deleted
    if (cursor.rowcount > 0):
        response_data = {}
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




##Create the server
app = AsyncApp(__name__, specification_dir="connexion-example-master/")

##Add the required APIs
#app.add_api("yaml/TS29549_SS_GroupManagement.yaml", resolver=RelativeResolver(''))
app.add_api("yaml/TS29549_SS_GroupManagement.yaml")
app.add_api("yaml/TS29549_SS_LocationReporting.yaml")
app.add_api("yaml/TS29549_SS_NetworkResourceAdaptation.yaml")


printing_example("Waiting for first Network Resource Adaption request...")



try:
    if __name__ == '__main__':
        #Start server
        app.run(f"{Path(__file__).stem}:app", port=AppPort)
except KeyboardInterrupt:
    #Ater KeyboardInterrupt
    print("CTRL-C: Exiting")
    #t.cancel()
    # Close the client socket
    if (client_socket is not None) :
        print("Closing socket")
        client_socket.close()
    #Close db connection and cursor
    if db.is_connected():
        db.close()
        cursor.close()
        print("MySQL connection is closed")

# Close the client socket
#client_socket.close()
#print("CTRL-C: Exiting")