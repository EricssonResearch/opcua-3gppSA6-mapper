from urllib import request, parse
import requests
from urllib import error
import string
import random
import json
import time
from datetime import timedelta, date, datetime, timezone

from NetworkExposureAPI import NetworkExposure_API


def flatten_dict(d, parent_key='location-info', sep='['):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)



class SEAL(NetworkExposure_API):

    def __init__(self):
        self.deviceID = "asdasd123"
        self.valGroupId = ""
        self.groupDocId = ""
        self.uniSubId = ""
        self.LocationReportingId = ""
        self.multiSubId = ""
        self.url_SEAL = 'http://10.1.2.50:7777/'
        # self.url_SEAL = 'http://127.0.0.1:7777/'
        self.auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImZvbyIsInBhc3N3b3JkIjoiYmFyIiwiaWF0IjoxNjY4MDg0NDI1fQ.lT4ABOQSHyJdIiF9rso06qcwrBkIxRFyolIgdBAI4l0"
        self.username = "foo"
        self.password = "bar"
        self.LocationArea = ""
        self.valServiceIds = []
        self.valServiceIds.append("VAL-service-1")
        

        # if there is a SEAL server that provides responses, then this can be set to 0
        self.local_test = 0
    
        self.QCI = None
        self.uplinkMaxBitRate = None
        self.downlinkMaxBitRate = None
        self.dstIp = None
        self.dstPort = None
        self.srcPort = None
        self.protocol = None
        self.direction = None

        r = None

        print("SEAL instance created" + str(self))

    def Login(self):
        url = self.url_SEAL + "login"
        print("url: " + url)

        post_data = {'username': self.username,
                    "password": self.password 
                    }

        post_data = json.dumps(post_data)
        print(post_data)
        post_data = post_data.encode()

        if self.local_test == 0:
            try:
                #req = request.Request(url, data = post_data, method="POST")
                req = request.Request(url, method="POST")
                req.add_header('Content-Type', 'application/json')
                r = request.urlopen(req, data=post_data).read().decode('utf-8')
            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
            else:
                # everything is fine
                # not used
                ret_code = 200  
        else:
            r = '''{"username":"foo","password":"bar","accessToken":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImZvbyIsInBhc3N3b3JkIjoiYmFyIiwiaWF0IjoxNjY4MDg0NDI1fQ.lT4ABOQSHyJdIiF9rso06qcwrBkIxRFyolIgdBAI4l0"}'''

        data = json.loads(r)
        self.auth_token = data['accessToken']
        print("auth_token : " + self.auth_token)
        return 200


    def CheckConnectionToNRM(self):
        url = self.url_SEAL
        print("url: " + url)
        post_data = {}


        if self.local_test == 0:
                try:
                    #req = request.Request(url, data = post_data, method="POST")
                    req = request.Request(url, method="POST")
                    req.add_header('Content-Type', 'application/json')
                    r = request.urlopen(req, data=post_data, timeout=6000).read().decode('utf-8')
                    return
                except error.URLError as e:
                    if hasattr(e, 'reason'):
                        print('We failed to reach a server.')
                        print('Reason: ', e.reason)

                        if (hasattr(e, 'reason')):
                        
                            while(hasattr(e, 'reason')):
                                time.sleep(5)
                                try:
                                    r = request.urlopen(req, data=post_data, timeout=10).read().decode('utf-8')
                                    print("Connection to NRM is OK")
                                    return
                                except error.URLError as es:
                                    e = es
                                    if hasattr(e, 'reason'):
                                        print('We failed to reach a server.')
                                        print('Reason: ', e.reason)
                                    elif hasattr(e, 'code'):
                                        print('The server couldn\'t fulfill the request.')
                                        print('Error code: ', e.code)
                                        return

                    elif hasattr(e, 'code'):
                        print('The server couldn\'t fulfill the request.')
                        print('Error code: ', e.code)
        

    


#Group Management
    def CreateDeviceGroup(self, grpDesc):
        local_test = 1
        url = self.url_SEAL + "ss-gm/v1/group-documents"
        print("url: " + url)

        post_data2 = {
            "valGroupId": 'OPC-UA-DOMAIN_ID-' + str(grpDesc),
            "grpDesc": 'OPC-UA-DOMAIN_ID-' + str(grpDesc),
            "members": [
                {
                "valUserId": str(self.deviceID),
                "valUeId": str(self.deviceID) + "@valdomain.com"
                },
            ],
            "valGrpConf": "communicationType: IPV4",
            "valServiceIds": [
                "VAL-service-1"
            ],
            "suppFeat": "1"
        }

        post_data = {
            "valGroupId": 'OPC-UA-DOMAIN_ID-' + str(grpDesc),
            "grpDesc": 'OPC-UA-DOMAIN_ID-' + str(grpDesc),
            "members": [
                {
                "valUserId": str(self.deviceID),
                "valUeId": str(self.deviceID) + "@valdomain.com"
                },
            ],
            "valGrpConf": "communicationType: IPV4",
            "valServiceIds": [
                "VAL-service-1"
            ],
            "valSvcInf":"string", #VAL service specific information.
            "locInfo":{
                "ageOfLocationInfo": 0,#Integer (int32): minimum 0
                "cellId": "Cella_ID_string_example",
                "enodeBId": "enodeB_Identifier_string",
                "routingAreaId": "string",
                "trackingAreaId": "string",
                "plmnId": "PLMN Identity",
                "twanId": "TWAN Identity",
                "geographicArea":#[ #minimum array length: 1
                        {   
                            "point":{ 
                                    "lon": 47.1625, 
                                    "lat": 19.5033,
                                    # "innerRadius":327674,
                                    # "uncertaintyRadius":254,
                                    # "offsetAngle":180,
                                    # "includedAngle":180,
                                    # "confidence":80,
                            },
                            "shape":"POINT",  
                            #"shape" : "POINT",
                            # - POINT
                            # - POINT_UNCERTAINTY_CIRCLE
                            # - POINT_UNCERTAINTY_ELLIPSE
                            # - POLYGON
                            # - POINT_ALTITUDE
                            # - POINT_ALTITUDE_UNCERTAINTY
                            # - ELLIPSOID_ARC
                            # - LOCAL_2D_POINT_UNCERTAINTY_ELLIPSE
                            # - LOCAL_3D_POINT_UNCERTAINTY_ELLIPSOID
                        },
                    #],
                "civicAddress":#[ #minimum array length: 1
                    { 
                            "country":"Hungary",
                            "A1":"A1",
                            "A2":"A2",
                            "A3":"A3",
                            "A4":"A4",
                            "A5":"A5",
                            "A6":"A6",
                            "PRD":"PRD",
                            "POD":"POD",
                            "STS":"STS",
                            "HNO":"HNO",
                            "HNS":"HNS",
                            "LMK":"LMK",
                            "LOC":"LOC",
                            "NAM":"NAM",
                            "PC":"PC",
                            "BLD":"BLD",
                            "UNIT":"UNIT",
                            "FLR":"FLR",
                            "ROOM":"ROOM",
                            "PLC":"PLC",
                            "PCN":"PCN",
                            "POBOX":"POBOX",
                            "ADDCODE":"ADDCODE",
                            "SEAT":"SEAT",
                            "RD":"RD",
                            "RDSEC":"RDSEC",
                            "RDBR":"RDBR",
                            "RDSUBBR":"RDSUBBR",
                            "PRM":"PRM",
                            "POM":"POM",
                            "usageRules":"Authorized only",
                            "method":"HTTP",
                            "providedBy":"OPC-UA-subscription-SEAL-User",
                    },
                #],
                "positionMethod": "CELLID",
                        # - CELLID
                        # - ECID
                        # - OTDOA
                        # - BAROMETRIC_PRESSURE
                        # - WLAN
                        # - BLUETOOTH
                        # - MBS
                        # - MOTION_SENSOR
                        # - DL_TDOA
                        # - DL_AOD
                        # - MULTI-RTT
                        # - NR_ECID
                        # - UL_TDOA
                        # - UL_AOA
                        # - NETWORK_SPECIFIC
                "qosFulFilInd": "REQUESTED_ACCURACY_FULFILLED",
                    # - REQUESTED_ACCURACY_FULFILLED
                    # - REQUESTED_ACCURACY_NOT_FULFILLED  
                "ueVelocity": { #HorizontalWithVerticalVelocityAndUncertainty
                    "hSpeed": 100,              #Horizontal speed: 0 - 2047 (float)                         HorizontalVelocity
                    "bearing": 30,              #Horizontal orientation: 0 - 360 (float)                    HorizontalVelocity
                    # "vSpeed": 0,                #Vertical speed: 0 - 255 (float)                            HorizontalWithVerticalVelocity
                    # "vDirection": "DOWNWARD",   #Dir of vertical speed: UPWARD / DOWNWARD                   HorizontalWithVerticalVelocity
                    # "hUncertainty": 0,          #Indicates value of speed uncertainty: 0 - 255 (float)      HorizontalWithVerticalVelocityAndUncertainty
                    # "vUncertainty": 0           #Same for vSpeed                                            HorizontalWithVerticalVelocityAndUncertainty
                },
                    # HorizontalVelocity
                    # HorizontalWithVerticalVelocity
                "ldrType": "BEING_INSIDE_AREA",
                    # - UE_AVAILABLE
                    # - PERIODIC
                    # - ENTERING_INTO_AREA
                    # - LEAVING_FROM_AREA
                    # - BEING_INSIDE_AREA
                    # - MOTION
                "achievedQos":{
                    "hAccuracy": 0.5, #min val 0 float
                    "vAccuracy": 0.5
                }
            },
            "addLocInfo":{
                "geographicAreas":  [], #Can be empty array
                "civicAddresses": [], #Can be empty array
                "nwAreaInfo": {
                    "ecqis": [#minimum array length: 1
                        {
                            "plmnId": {
                                "mcc": "216",   #Pattern: '^\d{3}$'
                                "mnc": "30",    #Pattern: '^\d{2,3}$'
                                # Mcc-Mnc example for Hungary
                                # 216-01  	Yettel Magyarország Zrt.  	            assigned  	HA-21052/2005  	    2006.01.10 
                                # 216-02  	HM EI Zrt.  	                        assigned  	AG/10631-3/2024  	2024.05.01 
                                # 216-03  	DIGI Távközlési és Szolgáltató Kft.  	assigned  	AG/26689-5/2016  	2016.10.26 
                                # 216-04  	Pro-M Zrt.  	                        assigned  	AG/19823-3/2023  	2023.09.19 
                                # 216-20  	Yettel Magyarország Zrt.  	            assigned  	AG/19312-4/2022  	2022.09.05 
                                # 216-25  	Yettel Magyarország Zrt.  	            assigned  	AG/23794-5/2024  	2024.10.28 
                                # 216-30  	Magyar Telekom Nyrt.  	                assigned  	HA-21053/2005  	    2006.01.04 
                                # 216-70  	Vodafone Magyarország Zrt.  	        assigned  	HA-21054/2005  	    2006.01.19 
                                # 216-71  	Vodafone Magyarország Zrt.  	        assigned  	AG/8926-2/2021  	2021.05.03 
                                # 216-99  	MÁV Zrt.  	                            assigned  	AG/30745-4/2014  	2015.01.15 
                            },
                            "eutraCellId": "A123456", #Pattern: '^[A-Fa-f0-9]{7}$'
                            "nid": "string", #Pattern: '^[A-Fa-f0-9]{11}$'
                        }
                    ],
                    "ncgis": [#minimum array length: 1
                        {
                            "plmnId":{
                                "mcc": "216",   #Pattern: '^\d{3}$'
                                "mnc": "30",    #Pattern: '^\d{2,3}$'
                            },
                            "nrCellId": "96e407bA2", #Pattern: '^[A-Fa-f0-9]{9}$'
                            "nid": "ABCFabcf019", #Pattern: '^[A-Fa-f0-9]{11}$'
                        }
                    ],
                    "gRanNodeIds": [#minimum array length: 1
                        {
                            "plmnId":{
                                "mcc": "216",   #Pattern: '^\d{3}$'
                                "mnc": "30",    #Pattern: '^\d{2,3}$'
                            },

                            ####################### From this only one is needed because of 'OneOf'
                            # "n3IwfId": "Af", #Pattern: '^[A-Fa-f0-9]+$'
                            "gNbId": {
                                "bitLength": 22, #Integer length of gNB ID: 22-32
                                "gNBValue":  "96e407b" #Pattern: '^[A-Fa-f0-9]{6,8}$' #NCI:158220411, NCI hex:96e407b
                            },
                            # "ngeNbId": "MacroNGeNB-AFFFF", #Pattern: '^(MacroNGeNB-[A-Fa-f0-9]{5}|LMacroNGeNB-[A-Fa-f0-9]{6}|SMacroNGeNB-[A-Fa-f0-9]{5})$'
                            # "wagfId": "Fa", #Pattern: '^[A-Fa-f0-9]+$'
                            # "tngfId": "aF", #Pattern: '^[A-Fa-f0-9]+$'
                            # "eNbId": "SMacroeNB-AF012", #Pattern: '^(MacroeNB-[A-Fa-f0-9]{5}|LMacroeNB-[A-Fa-f0-9]{6}|SMacroeNB-[A-Fa-f0-9]{5}|HomeeNB-[A-Fa-f0-9]{7})$'
                            #######################
                            "nid": "ABCFabcf019", #Pattern: '^[A-Fa-f0-9]{11}$'
                        }
                    ],
                    "tais": [#minimum array length: 1
                        {
                            "plmnId":{
                                "mcc": "216",   #Pattern: '^\d{3}$'
                                "mnc": "30",    #Pattern: '^\d{2,3}$'
                            },
                            "tac":"AF12", #Pattern: '(^[A-Fa-f0-9]{4}$)|(^[A-Fa-f0-9]{6}$)'
                            "nid": "ff00ABC123a", #Pattern: '^[A-Fa-f0-9]{11}$'
                        },
                    ]
                }
            },
            "extGrpId": "string", #str(self.deviceID) #String: local identifier followed by "@" and a domain identifier. Both the local identifier and the domain identifier shall be encoded as strings that do not contain any "@" characters. See Clauses 4.6.2 and 4.6.3 of 3GPP TS 23.682 for more information.
            "com5GLanType": "IPV4",
                # - IPV4
                # - IPV6
                # - IPV4V6
                # - UNSTRUCTURED
                # - ETHERNET
            "suppFeat": "FFFF", #Pattern: '^[A-Fa-f0-9]*$'
            "resUri": "string",
        }

        post_data['valServiceIds'] = self.valServiceIds
        post_data = json.dumps(post_data)
        print(post_data)
        post_data = post_data.encode()

        response = None
        response_data = None

        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)
                
                req = request.Request(url, method="POST")
                req.add_header('Content-Type', 'application/json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                response = request.urlopen(req, data=post_data)
                response_data = response.read().decode('utf-8')
                
                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("GroupManagement POST %f ms" %delay)

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
            else:
                # everything is fine
                # not used
                ret_code = 200  
        else:
            response_data = '''{
                    "valGroupId": "string",
                    "grpDesc": "string",
                    "members": [
                        {
                        "valUserId": "string",
                        "valUeId": "string"
                        },
                        {
                        "valUserId": "string",
                        "valUeId": "string"
                        }
                    ],
                    "valGrpConf": "string",
                    "valServiceIds": [
                        "string"
                    ],
                    "valSvcInf": "string",
                    "suppFeat": "string",
                    "resUri": "https://example.com/ss-gm/v1/group-documents/96be8d4d422dd4f90eefd4ace1e4b8"
                    }'''

        try:
            self.groupDocId = response.getheader('Location')
            self.valGroupId = response.valGroupId
            print("\n\nREAD-HEADER-('Location') groupDocId : " + str(self.groupDocId))
            # self.groupDocId = json.loads(response_data)["Location"]
            # print("READ-BODY-LOCATION groupDocId : " + str(self.groupDocId))
        except Exception as e:
            print(response_data)
            data = json.loads(response_data)
            self.groupDocId = data['Location']
        print("groupDocId : " + str(self.groupDocId))
        #breakpoint()
        return 200

    def RetriveDeviceGroups(self, grpDesc):
        val_group_id = self.groupDocId 
        val_service_id = self.valServiceIds[0]
        local_test = 1
        #url = self.url_SEAL + "ss-gm/v1/group-documents{}".format(str("?"+"val-group-id="+val_group_id+"&"+"val-service-id="+val_service_id))#+"?"+"val-group-id="+val_group_id+"&"+"val-service-id="+val_service_id
        url = self.url_SEAL + "ss-gm/v1/group-documents"+"?"+"val-group-id="+val_group_id+"&"+"val-service-id="+val_service_id
        print("url: " + url)

        post_data = {}

        response = None
        response_data = None

        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)
                
                req = request.Request(url, method="GET")
                req.add_header('Content-Type', 'application/json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                response = request.urlopen(req)
                response_data = response.read().decode('utf-8')
                
                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("GroupManagement-filter GET %f ms" %delay)

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
            else:
                # everything is fine
                # not used
                ret_code = 200  
        else:
            response_data = '''{
                    "valGroupId": "string",
                    "grpDesc": "string",
                    "members": [
                        {
                        "valUserId": "string",
                        "valUeId": "string"
                        },
                        {
                        "valUserId": "string",
                        "valUeId": "string"
                        }
                    ],
                    "valGrpConf": "string",
                    "valServiceIds": [
                        "string"
                    ],
                    "valSvcInf": "string",
                    "suppFeat": "string",
                    "resUri": "https://example.com/ss-gm/v1/group-documents/96be8d4d422dd4f90eefd4ace1e4b8"
                    }'''
        data = ""
        try:
            self.valgroupId = response.getheader('Location')
            if (self.valgroupId is None or self.valgroupId == ""):
                self.valgroupId = response.body["Location"]
            data = json.loads(response_data)
        except Exception as e:
            #print(response_data)
            data = json.loads(response_data)
            #self.groupDocId = data['resUri']
            
        print("valgroupId : " + str(self.valgroupId))
        print("DATA accessed : \n")
        print(data)
        #breakpoint()
        return 200

    def GetDeviceGroup(self):
        local_test = 1
        url = self.url_SEAL + "ss-gm/v1/group-documents/"+self.groupDocId
        print("url: " + url)

        post_data = {}

        response = None
        response_data = None

        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)
        
                req = request.Request(url, method="GET")
                req.add_header('Content-Type', 'application/json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                response = request.urlopen(req, data=post_data)
                response_data = response.read().decode('utf-8')
                
                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("GroupManagement GET %f ms" %delay)

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
            else:
                # everything is fine
                # not used
                ret_code = 200  
        else:
            response_data = '''{
                    "valGroupId": "string",
                    "grpDesc": "string",
                    "members": [
                        {
                        "valUserId": "string",
                        "valUeId": "string"
                        },
                        {
                        "valUserId": "string",
                        "valUeId": "string"
                        }
                    ],
                    "valGrpConf": "string",
                    "valServiceIds": [
                        "string"
                    ],
                    "valSvcInf": "string",
                    "suppFeat": "string",
                    "resUri": "https://example.com/ss-gm/v1/group-documents/96be8d4d422dd4f90eefd4ace1e4b8"
                    }'''

        try:
            self.groupDocId = response.getheader('Location') 
        except Exception as e:
            print(response_data)
            data = json.loads(response_data)
            self.groupDocId = data['resUri']
        
        print("groupDocId : " + str(self.groupDocId))
        print("DATA accessed : \n%s\n\n"%json.dumps(response_data))
        #breakpoint()
        return 200

    def ModifyDeviceGroup(self, grpDesc):
        local_test = 1
        url = self.url_SEAL + "ss-gm/v1/group-documents/"+self.groupDocId
        print("url: " + url)

        post_data = {
            #"valGroupId": 'OPC-UA-DOMAIN_ID-' + str(grpDesc),
            "grpDesc": 'OPC-UA-DOMAIN_ID-' + str(grpDesc),
            "members": [
                {
                "valUserId": str(self.deviceID),
                "valUeId": str(self.deviceID) + "@valdomain.com"
                },
            ],
            "valGrpConf": "communicationType: IPV4",
            "valServiceIds": [
                "VAL-service-1"
            ],
            "locInfo":{
                "ageOfLocationInfo": 0,#Integer (int32): minimum 0
                "cellId": "Cella_ID_string_example",
                "enodeBId": "enodeB_Identifier_string",
                "routingAreaId": "string",
                "trackingAreaId": "string",
                "plmnId": "PLMN Identity",
                "twanId": "TWAN Identity",
                "geographicArea":#[ #minimum array length: 1
                        {   
                            "point":{ 
                                    "lon": 47.1625, 
                                    "lat": 19.5033,
                            },
                            "shape":"POINT",  
                        },
                    #],
                "civicAddress":#[ #minimum array length: 1
                    { 
                            "country":"Hungary",
                            "A1":"A1",
                            "A2":"A2",
                            "A3":"A3",
                            "A4":"A4",
                            "A5":"A5",
                            "A6":"A6",
                            "PRD":"PRD",
                            "POD":"POD",
                            "STS":"STS",
                            "HNO":"HNO",
                            "HNS":"HNS",
                            "LMK":"LMK",
                            "LOC":"LOC",
                            "NAM":"NAM",
                            "PC":"PC",
                            "BLD":"BLD",
                            "UNIT":"UNIT",
                            "FLR":"FLR",
                            "ROOM":"ROOM",
                            "PLC":"PLC",
                            "PCN":"PCN",
                            "POBOX":"POBOX",
                            "ADDCODE":"ADDCODE",
                            "SEAT":"SEAT",
                            "RD":"RD",
                            "RDSEC":"RDSEC",
                            "RDBR":"RDBR",
                            "RDSUBBR":"RDSUBBR",
                            "PRM":"PRM",
                            "POM":"POM",
                            "usageRules":"Authorized only",
                            "method":"HTTP",
                            "providedBy":"OPC-UA-subscription-SEAL-User",
                    },
                #],
                "positionMethod": "CELLID",
                "qosFulFilInd": "REQUESTED_ACCURACY_FULFILLED",
                    # - REQUESTED_ACCURACY_FULFILLED
                    # - REQUESTED_ACCURACY_NOT_FULFILLED  
                "ueVelocity": { #HorizontalWithVerticalVelocityAndUncertainty
                    "hSpeed": 100,              #Horizontal speed: 0 - 2047 (float)                         HorizontalVelocity
                    "bearing": 30,              #Horizontal orientation: 0 - 360 (float)                    HorizontalVelocity
                },
                "ldrType": "BEING_INSIDE_AREA",
                "achievedQos":{
                    "hAccuracy": 0.5, #min val 0 float
                    "vAccuracy": 0.5
                }
            },
            "addLocInfo":{
                "geographicAreas":  [], #Can be empty array
                "civicAddresses": [], #Can be empty array
                "nwAreaInfo": {
                    "ecqis": [#minimum array length: 1
                        {
                            "plmnId": {
                                "mcc": "216",   #Pattern: '^\d{3}$'
                                "mnc": "30",    #Pattern: '^\d{2,3}$'
                            },
                            "eutraCellId": "A123456", #Pattern: '^[A-Fa-f0-9]{7}$'
                            "nid": "string", #Pattern: '^[A-Fa-f0-9]{11}$'
                        }
                    ],
                    "ncgis": [#minimum array length: 1
                        {
                            "plmnId":{
                                "mcc": "216",   #Pattern: '^\d{3}$'
                                "mnc": "30",    #Pattern: '^\d{2,3}$'
                            },
                            "nrCellId": "96e407bA2", #Pattern: '^[A-Fa-f0-9]{9}$'
                            "nid": "ABCFabcf019", #Pattern: '^[A-Fa-f0-9]{11}$'
                        }
                    ],
                    "gRanNodeIds": [#minimum array length: 1
                        {
                            "plmnId":{
                                "mcc": "216",   #Pattern: '^\d{3}$'
                                "mnc": "30",    #Pattern: '^\d{2,3}$'
                            },
                            ####################### From this only one is needed because of 'OneOf'
                            # "n3IwfId": "Af", #Pattern: '^[A-Fa-f0-9]+$'
                            # "gNbId": {
                            #     "bitLength": 22, #Integer length of gNB ID: 22-32
                            #     "gNBValue":  "96e407b" #Pattern: '^[A-Fa-f0-9]{6,8}$' #NCI:158220411, NCI hex:96e407b
                            # },
                            # "ngeNbId": "MacroNGeNB-AFFFF", #Pattern: '^(MacroNGeNB-[A-Fa-f0-9]{5}|LMacroNGeNB-[A-Fa-f0-9]{6}|SMacroNGeNB-[A-Fa-f0-9]{5})$'
                            # "wagfId": "Fa", #Pattern: '^[A-Fa-f0-9]+$'
                            # "tngfId": "aF", #Pattern: '^[A-Fa-f0-9]+$'
                            "eNbId": "SMacroeNB-AF012", #Pattern: '^(MacroeNB-[A-Fa-f0-9]{5}|LMacroeNB-[A-Fa-f0-9]{6}|SMacroeNB-[A-Fa-f0-9]{5}|HomeeNB-[A-Fa-f0-9]{7})$'
                            #######################
                            "nid": "ABCFabcf019", #Pattern: '^[A-Fa-f0-9]{11}$'
                        }
                    ],
                    "tais": [#minimum array length: 1
                        {
                            "plmnId":{
                                "mcc": "216",   #Pattern: '^\d{3}$'
                                "mnc": "30",    #Pattern: '^\d{2,3}$'
                            },
                            "tac":"AF12", #Pattern: '(^[A-Fa-f0-9]{4}$)|(^[A-Fa-f0-9]{6}$)'
                            "nid": "ff00ABC123a", #Pattern: '^[A-Fa-f0-9]{11}$'
                        },
                    ]
                }
            },
            "extGrpId": "string", #str(self.deviceID) #String: local identifier followed by "@" and a domain identifier. Both the local identifier and the domain identifier shall be encoded as strings that do not contain any "@" characters. See Clauses 4.6.2 and 4.6.3 of 3GPP TS 23.682 for more information.
            "com5GLanType": "IPV4",
        }

        post_data = json.dumps(post_data)
        print(post_data)
        post_data = post_data.encode()

        response = None
        response_data = None

        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)
                
                req = request.Request(url, method="PATCH")
                req.add_header('Content-Type', 'application/merge-patch+json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                response = request.urlopen(req, data=post_data)
                response_data = response.read().decode('utf-8')

                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("GroupManagement PATCH %f ms" %delay)

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
            else:
                # everything is fine
                # not used
                ret_code = 200  
        else:
            response_data = '''{
                    "valGroupId": "string",
                    "grpDesc": "string",
                    "members": [
                        {
                        "valUserId": "string",
                        "valUeId": "string"
                        },
                        {
                        "valUserId": "string",
                        "valUeId": "string"
                        }
                    ],
                    "valGrpConf": "string",
                    "valServiceIds": [
                        "string"
                    ],
                    "valSvcInf": "string",
                    "suppFeat": "string",
                    "resUri": "https://example.com/ss-gm/v1/group-documents/96be8d4d422dd4f90eefd4ace1e4b8"
                    }'''

        try:
            self.groupDocId = response.getheader('Location') 
        except Exception as e:
            print(response_data)
            data = json.loads(response_data)
            self.groupDocId = data['resUri']
        
        print("groupDocId : " + str(self.groupDocId))
        print("DATA accessed : \n%s\n\n"%json.dumps(response_data))
        #breakpoint()
        return 200

    def UpdateDeviceGroup(self, grpDesc):
        local_test = 1
        url = self.url_SEAL + "ss-gm/v1/group-documents/"+self.groupDocId
        print("url: " + url)

        post_data = {
            "valGroupId": 'OPC-UA-DOMAIN_ID-' + str(grpDesc),
            "grpDesc": 'OPC-UA-DOMAIN_ID-' + str(grpDesc),
            "members": [
                {
                "valUserId": str(self.deviceID),
                "valUeId": str(self.deviceID) + "@valdomain.com"
                },
            ],
            "valGrpConf": "communicationType: IPV4",
            "valServiceIds": [
                "VAL-service-1"
            ],
            "valSvcInf":"string", #VAL service specific information.
            "locInfo":{
                "ageOfLocationInfo": 0,#Integer (int32): minimum 0
                "cellId": "Cella_ID_string_example",
                "enodeBId": "enodeB_Identifier_string",
                "routingAreaId": "string",
                "trackingAreaId": "string",
                "plmnId": "PLMN Identity",
                "twanId": "TWAN Identity",
                "geographicArea":#[ #minimum array length: 1
                        {   
                            "point":{ 
                                    "lon": 47.1625, 
                                    "lat": 19.5033,
                                    # "innerRadius":327674,
                                    # "uncertaintyRadius":254,
                                    # "offsetAngle":180,
                                    # "includedAngle":180,
                                    # "confidence":80,
                            },
                            "shape":"POINT",  
                            #"shape" : "POINT",
                            # - POINT
                            # - POINT_UNCERTAINTY_CIRCLE
                            # - POINT_UNCERTAINTY_ELLIPSE
                            # - POLYGON
                            # - POINT_ALTITUDE
                            # - POINT_ALTITUDE_UNCERTAINTY
                            # - ELLIPSOID_ARC
                            # - LOCAL_2D_POINT_UNCERTAINTY_ELLIPSE
                            # - LOCAL_3D_POINT_UNCERTAINTY_ELLIPSOID
                        },
                    #],
                "civicAddress":#[ #minimum array length: 1
                    { 
                            "country":"Hungary",
                            "A1":"A1",
                            "A2":"A2",
                            "A3":"A3",
                            "A4":"A4",
                            "A5":"A5",
                            "A6":"A6",
                            "PRD":"PRD",
                            "POD":"POD",
                            "STS":"STS",
                            "HNO":"HNO",
                            "HNS":"HNS",
                            "LMK":"LMK",
                            "LOC":"LOC",
                            "NAM":"NAM",
                            "PC":"PC",
                            "BLD":"BLD",
                            "UNIT":"UNIT",
                            "FLR":"FLR",
                            "ROOM":"ROOM",
                            "PLC":"PLC",
                            "PCN":"PCN",
                            "POBOX":"POBOX",
                            "ADDCODE":"ADDCODE",
                            "SEAT":"SEAT",
                            "RD":"RD",
                            "RDSEC":"RDSEC",
                            "RDBR":"RDBR",
                            "RDSUBBR":"RDSUBBR",
                            "PRM":"PRM",
                            "POM":"POM",
                            "usageRules":"Authorized only",
                            "method":"HTTP",
                            "providedBy":"OPC-UA-subscription-SEAL-User",
                    },
                #],
                "positionMethod": "CELLID",
                                # - CELLID
                                # - ECID
                                # - OTDOA
                                # - BAROMETRIC_PRESSURE
                                # - WLAN
                                # - BLUETOOTH
                                # - MBS
                                # - MOTION_SENSOR
                                # - DL_TDOA
                                # - DL_AOD
                                # - MULTI-RTT
                                # - NR_ECID
                                # - UL_TDOA
                                # - UL_AOA
                                # - NETWORK_SPECIFIC
                "qosFulFilInd": "REQUESTED_ACCURACY_FULFILLED",
                                # - REQUESTED_ACCURACY_FULFILLED
                                # - REQUESTED_ACCURACY_NOT_FULFILLED  
                "ueVelocity": { #HorizontalWithVerticalVelocityAndUncertainty
                    "hSpeed": 100,              #Horizontal speed: 0 - 2047 (float)                         HorizontalVelocity
                    "bearing": 30,              #Horizontal orientation: 0 - 360 (float)                    HorizontalVelocity
                    # "vSpeed": 0,                #Vertical speed: 0 - 255 (float)                            HorizontalWithVerticalVelocity
                    # "vDirection": "DOWNWARD",   #Dir of vertical speed: UPWARD / DOWNWARD                   HorizontalWithVerticalVelocity
                    # "hUncertainty": 0,          #Indicates value of speed uncertainty: 0 - 255 (float)      HorizontalWithVerticalVelocityAndUncertainty
                    # "vUncertainty": 0           #Same for vSpeed                                            HorizontalWithVerticalVelocityAndUncertainty
                },
                    # HorizontalVelocity
                    # HorizontalWithVerticalVelocity
                "ldrType": "BEING_INSIDE_AREA",
                            # - UE_AVAILABLE
                            # - PERIODIC
                            # - ENTERING_INTO_AREA
                            # - LEAVING_FROM_AREA
                            # - BEING_INSIDE_AREA
                            # - MOTION
                "achievedQos":{
                    "hAccuracy": 0.5, #min val 0 float
                    "vAccuracy": 0.5
                }
            },
            "addLocInfo":{
                "geographicAreas":  [], #Can be empty array
                "civicAddresses": [], #Can be empty array
                "nwAreaInfo": {
                    "ecqis": [#minimum array length: 1
                        {
                            "plmnId": {
                                "mcc": "216",   #Pattern: '^\d{3}$'
                                "mnc": "30",    #Pattern: '^\d{2,3}$'
                                # Mcc-Mnc example for Hungary
                                # 216-01  	Yettel Magyarország Zrt.  	            assigned  	HA-21052/2005  	    2006.01.10 
                                # 216-02  	HM EI Zrt.  	                        assigned  	AG/10631-3/2024  	2024.05.01 
                                # 216-03  	DIGI Távközlési és Szolgáltató Kft.  	assigned  	AG/26689-5/2016  	2016.10.26 
                                # 216-04  	Pro-M Zrt.  	                        assigned  	AG/19823-3/2023  	2023.09.19 
                                # 216-20  	Yettel Magyarország Zrt.  	            assigned  	AG/19312-4/2022  	2022.09.05 
                                # 216-25  	Yettel Magyarország Zrt.  	            assigned  	AG/23794-5/2024  	2024.10.28 
                                # 216-30  	Magyar Telekom Nyrt.  	                assigned  	HA-21053/2005  	    2006.01.04 
                                # 216-70  	Vodafone Magyarország Zrt.  	        assigned  	HA-21054/2005  	    2006.01.19 
                                # 216-71  	Vodafone Magyarország Zrt.  	        assigned  	AG/8926-2/2021  	2021.05.03 
                                # 216-99  	MÁV Zrt.  	                            assigned  	AG/30745-4/2014  	2015.01.15 
                            },
                            "eutraCellId": "A123456", #Pattern: '^[A-Fa-f0-9]{7}$'
                            "nid": "string", #Pattern: '^[A-Fa-f0-9]{11}$'
                        }
                    ],
                    "ncgis": [#minimum array length: 1
                        {
                            "plmnId":{
                                "mcc": "216",   #Pattern: '^\d{3}$'
                                "mnc": "30",    #Pattern: '^\d{2,3}$'
                            },
                            "nrCellId": "96e407bA2", #Pattern: '^[A-Fa-f0-9]{9}$'
                            "nid": "ABCFabcf019", #Pattern: '^[A-Fa-f0-9]{11}$'
                        }
                    ],
                    "gRanNodeIds": [#minimum array length: 1
                        {
                            "plmnId":{
                                "mcc": "216",   #Pattern: '^\d{3}$'
                                "mnc": "30",    #Pattern: '^\d{2,3}$'
                            },

                            ####################### From this only one is needed because of 'OneOf'
                            # "n3IwfId": "Af", #Pattern: '^[A-Fa-f0-9]+$'
                            "gNbId": {
                                "bitLength": 22, #Integer length of gNB ID: 22-32
                                "gNBValue":  "96e407b" #Pattern: '^[A-Fa-f0-9]{6,8}$' #NCI:158220411, NCI hex:96e407b
                            },
                            # "ngeNbId": "MacroNGeNB-AFFFF", #Pattern: '^(MacroNGeNB-[A-Fa-f0-9]{5}|LMacroNGeNB-[A-Fa-f0-9]{6}|SMacroNGeNB-[A-Fa-f0-9]{5})$'
                            # "wagfId": "Fa", #Pattern: '^[A-Fa-f0-9]+$'
                            # "tngfId": "aF", #Pattern: '^[A-Fa-f0-9]+$'
                            # "eNbId": "SMacroeNB-AF012", #Pattern: '^(MacroeNB-[A-Fa-f0-9]{5}|LMacroeNB-[A-Fa-f0-9]{6}|SMacroeNB-[A-Fa-f0-9]{5}|HomeeNB-[A-Fa-f0-9]{7})$'
                            #######################
                            "nid": "ABCFabcf019", #Pattern: '^[A-Fa-f0-9]{11}$'
                        }
                    ],
                    "tais": [#minimum array length: 1
                        {
                            "plmnId":{
                                "mcc": "216",   #Pattern: '^\d{3}$'
                                "mnc": "30",    #Pattern: '^\d{2,3}$'
                            },
                            "tac":"AF12", #Pattern: '(^[A-Fa-f0-9]{4}$)|(^[A-Fa-f0-9]{6}$)'
                            "nid": "ff00ABC123a", #Pattern: '^[A-Fa-f0-9]{11}$'
                        },
                    ]
                }
            },
            "extGrpId": "string", #str(self.deviceID) #String: local identifier followed by "@" and a domain identifier. Both the local identifier and the domain identifier shall be encoded as strings that do not contain any "@" characters. See Clauses 4.6.2 and 4.6.3 of 3GPP TS 23.682 for more information.
            "com5GLanType": "IPV4",
                            # - IPV4
                            # - IPV6
                            # - IPV4V6
                            # - UNSTRUCTURED
                            # - ETHERNET
            "suppFeat": "FFFF", #Pattern: '^[A-Fa-f0-9]*$'
            "resUri": "string",
        }

        post_data = json.dumps(post_data)
        print(post_data)
        post_data = post_data.encode()

        response = None
        response_data = None

        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)
                
                req = request.Request(url, method="PUT")
                req.add_header('Content-Type', 'application/json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                response = request.urlopen(req,data=post_data)
                response_data = response.read().decode('utf-8')

                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("GroupManagement PUT %f ms" %delay)

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
            else:
                # everything is fine
                # not used
                ret_code = 200  
        else:
            response_data = '''{
                    "valGroupId": "string",
                    "grpDesc": "string",
                    "members": [
                        {
                        "valUserId": "string",
                        "valUeId": "string"
                        },
                        {
                        "valUserId": "string",
                        "valUeId": "string"
                        }
                    ],
                    "valGrpConf": "string",
                    "valServiceIds": [
                        "string"
                    ],
                    "valSvcInf": "string",
                    "suppFeat": "string",
                    "resUri": "https://example.com/ss-gm/v1/group-documents/96be8d4d422dd4f90eefd4ace1e4b8"
                    }'''

        try:
            self.groupDocId = response.getheader('Location') 
        except Exception as e:
            print(response_data)
            data = json.loads(response_data)
            self.groupDocId = data['resUri']
        
        print("groupDocId : " + str(self.groupDocId))
        print("DATA updated: \n%s\n\n"%json.dumps(response_data))
        #breakpoint()
        return 200

    def DeleteDeviceGroup(self):
        local_test = 1
        url = self.url_SEAL + "ss-gm/v1/group-documents/"+self.groupDocId
        print("url: " + url)


        post_data = {}
        response = None
        response_data = None

        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)

                req = request.Request(url, method="DELETE")
                req.add_header('Content-Type', 'application/json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                response = request.urlopen(req, data=post_data)
                response_data = response.read().decode('utf-8')
                
                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("GroupManagement DELETE %f ms" %delay)

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
            else:
                # everything is fine
                # not used
                ret_code = 200  
        else:
            response_data = '''{
                    "valGroupId": "string",
                    "grpDesc": "string",
                    "members": [
                        {
                        "valUserId": "string",
                        "valUeId": "string"
                        },
                        {
                        "valUserId": "string",
                        "valUeId": "string"
                        }
                    ],
                    "valGrpConf": "string",
                    "valServiceIds": [
                        "string"
                    ],
                    "valSvcInf": "string",
                    "suppFeat": "string",
                    "resUri": "https://example.com/ss-gm/v1/group-documents/96be8d4d422dd4f90eefd4ace1e4b8"
                    }'''

        try:
            self.groupDocId = response.getheader('Location') 
        except Exception as e:
            print(response_data)
            data = json.loads(response_data)
            self.groupDocId = data['resUri']
        
        print("groupDocId : " + str(self.groupDocId))
        print("DATA accessed (deleted if empty): \n%s\n\n"%json.dumps(response_data))
        #breakpoint()
        return 200




    def AddDeviceAsMemberToDeviceGroup(self, grpDesc):
        local_test = 1
        url = self.url_SEAL + "/" + self.groupDocId
        print("url: " + url)

        post_data = {
            "valGroupId": 'ROS2-DOMAIN_ID-' + str(grpDesc),
            "grpDesc": 'ROS2-DOMAIN_ID-' + str(grpDesc),
            "members": [
                {
                "valUserId": str(self.deviceID),
                "valUeId": str(self.deviceID) + "@valdomain.com"
                },
            ],
            "valGrpConf": "communicationType: IPV4",
            "valServiceIds": [
                "VAL-service-1"
            ],
            "suppFeat": "1"
        }

        post_data = json.dumps(post_data)
        print(post_data)
        post_data = post_data.encode()

        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)
                
                req = request.Request(url, method="PATCH")
                req.add_header('Content-Type', 'application/json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                r = request.urlopen(req, data=post_data)

                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("Group-Management-add-device PATCH %f ms" %delay)

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                    if (hasattr(e, 'reason')):
                            while(hasattr(e, 'reason')):
                                time.sleep(10)
                                try:
                                    r = request.urlopen(req, data=post_data)
                                    return
                                except error.URLError as es:
                                    e = es
                                    if hasattr(e, 'reason'):
                                        print('We failed to reach a server.')
                                        print('Reason: ', e.reason)
                                    elif hasattr(e, 'code'):
                                        print('The server couldn\'t fulfill the request.')
                                        print('Error code: ', e.code)
                                        return
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
            else:
                # everything is fine
                r = '{}'
                return 200;   
        else:
            r = '''{
                }'''
            return 200

        self.groupDocId = r.getheader('Location')
        print("groupDocId : " + str(self.groupDocId))
        #breakpoint()
        return 200
        



#Unicast-subscription management
    def NetworkResourceAdaptation(self, QCI, uplinkMaxBitRate, downlinkMaxBitRate, dstIp, dstPort, srcIp, srcPort, protocol, direction, loc = False):
        local_test = 1
        url = self.url_SEAL + "ss-nra/v1/unicast-subscriptions"
        print("url: " + url)

        #request is valid for 7 days
        end_date = date.today() + timedelta(days=7)

        uniQoSReq_data = {
                    "type": "IPV4", 
                    "qci": QCI, 
                    "ulBW": uplinkMaxBitRate, 
                    "dlBW": downlinkMaxBitRate, 
                    "flowID": {
                        "dstIp": dstIp, 
                        "dstPort": dstPort,
                        "srcIp": srcIp, 
                        "srcPort": srcPort, 
                        "protocol": protocol, 
                        }
        }

        post_data =  {
                    "valTgtUe": {
                        "valUserId": str(self.deviceID),
                        "valUeId": str(self.deviceID) + "@valdomain.com"
                    },
                    "uniQosReq": json.dumps(uniQoSReq_data),
                    "duration": end_date.strftime('%d/%m/%Y %H:%M:%S'),
                    "notifUri": "string",
                    "reqTestNotif": True,
                    "wsNotifCfg": {
                        "websocketUri": "string",
                        "requestWebsocketUri": True
                    },
                    "suppFeat": "FFFFF"
        }

        post_data = json.dumps(post_data)
        print(post_data)
        post_data = post_data.encode()

        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)
                req = request.Request(url, method="POST")
                req.add_header('Content-Type', 'application/json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                
                if (loc):
                    req.add_header('Location', self.uniSubId)

                r = request.urlopen(req, data=post_data)
                r_data = r.read().decode('utf-8')
                
                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("Unicast-Subscription POST %f ms" %delay)
                
            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                    if (hasattr(e, 'reason')):
                            while(hasattr(e, 'reason')):
                                time.sleep(10)
                                try:
                                    r = request.urlopen(req, data=post_data)
                                    return
                                except error.URLError as es:
                                    e = es
                                    if hasattr(e, 'reason'):
                                        print('We failed to reach a server.')
                                        print('Reason: ', e.reason)
                                    elif hasattr(e, 'code'):
                                        print('The server couldn\'t fulfill the request.')
                                        print('Error code: ', e.code)
                                        return

                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
                else:
                    # everything is fine
                    r = '{}'
                    return 200   
        else:
            r = '{}'
            return 200

        self.uniSubId = r.getheader('Location')

        print("uniSubId : " + str(self.uniSubId))
        #print("r_data: "+str(r_data))

    def NetworkResourceAdaptationGET(self):
        local_test = 1
        url = self.url_SEAL + "ss-nra/v1/unicast-subscriptions/" + self.uniSubId
        print("url: " + url)

        #request is valid for 7 days
        #end_date = date.today() + timedelta(days=7)

        post_data =  {}


        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)
                
                req = request.Request(url, method="GET")
                req.add_header('Content-Type', 'application/json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                r = request.urlopen(req, data=post_data).read().decode('utf-8')
                print(r)

                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("Unicast-Subscription GET %f ms" %delay)

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                    if (hasattr(e, 'reason')):
                            while(hasattr(e, 'reason')):
                                time.sleep(10)
                                try:
                                    r = request.urlopen(req, data=post_data)
                                    return
                                except error.URLError as es:
                                    e = es
                                    if hasattr(e, 'reason'):
                                        print('We failed to reach a server.')
                                        print('Reason: ', e.reason)
                                    elif hasattr(e, 'code'):
                                        print('The server couldn\'t fulfill the request.')
                                        print('Error code: ', e.code)
                                        return
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
                else:
                    # everything is fine
                    r = '{}'
                    return 200   
        else:
            r = '{}'
            return 200

    def NetworkResourceAdaptationDELETE(self):
        local_test = 1
        url = self.url_SEAL + "ss-nra/v1/unicast-subscriptions/" + self.uniSubId
        print("url: " + url)

        #request is valid for 7 days
        end_date = date.today() + timedelta(days=7)

        post_data =  {}


        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)

                req = request.Request(url, method="DELETE")
                req.add_header('Content-Type', 'application/json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                r = request.urlopen(req, data=post_data).read().decode('utf-8')
                print(r)
                self.uniSubId = None

                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("Unicast-Subscription DELETE %f ms" %delay)

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                    if (hasattr(e, 'reason')):
                            while(hasattr(e, 'reason')):
                                time.sleep(10)
                                try:
                                    r = request.urlopen(req, data=post_data)
                                    return
                                except error.URLError as es:
                                    e = es
                                    if hasattr(e, 'reason'):
                                        print('We failed to reach a server.')
                                        print('Reason: ', e.reason)
                                    elif hasattr(e, 'code'):
                                        print('The server couldn\'t fulfill the request.')
                                        print('Error code: ', e.code)
                                        return
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
                else:
                    # everything is fine
                    r = '{}'
                    return 200   
        else:
            r = '{}'
            return 200



#Multicast-subscription management
    def NetworkResourceAdaptationMulti(self, QCI, uplinkMaxBitRate, downlinkMaxBitRate, dstIp, dstPort, srcIp, srcPort, protocol, direction, loc = False):
        local_test = 1
        url = self.url_SEAL + "ss-nra/v1/multicast-subscriptions"
        print("url: " + url)

        #request is valid for 7 days
        end_date = date.today() + timedelta(days=7)

        multiQoSReq_data = {
                    "type": "IPV4", 
                    "qci": QCI, 
                    "ulBW": uplinkMaxBitRate, 
                    "dlBW": downlinkMaxBitRate, 
                    "flowID": {
                        "dstIp": dstIp, 
                        "dstPort": dstPort,
                        "srcIp": srcIp,
                        "srcPort": srcPort, 
                        "protocol": protocol, 
                        }
        }
        post_data = {
            "valGroupId": self.valGroupId,
            "anncMode":"NRM",
            "duration": end_date.strftime('%d/%m/%Y %H:%M:%S'),
            "multiQosReq":json.dumps(multiQoSReq_data),
            "locArea":{
                    "cellId":["91399"],
                    "enodeBId":["357"],
                    "geographicArea":[
                        {   
                                "point":{ "lon": 47.471039, "lat": 19.062555 },
                                "shape" : "POINT",
                            # "innerRadius":327674,
                            # "uncertaintyRadius":254,
                            # "offsetAngle":180,
                            # "includedAngle":180,
                            # "confidence":80,
                        },
                    ],
                    "mbmsServiceAreaId":["FFFFFF"], #Unique number between 000000 - FFFFFF to indetify MBMS bearer in PLMN
                    "civicAddres":[{
                            "country":"Hungary",
                            "A1":"A1",
                            "A2":"A2",
                            "A3":"A3",
                            "A4":"A4",
                            "A5":"A5",
                            "A6":"A6",
                            "PRD":"PRD",
                            "POD":"POD",
                            "STS":"STS",
                            "HNO":"HNO",
                            "HNS":"HNS",
                            "LMK":"LMK",
                            "LOC":"LOC",
                            "NAM":"NAM",
                            "PC":"PC",
                            "BLD":"BLD",
                            "UNIT":"UNIT",
                            "FLR":"FLR",
                            "ROOM":"ROOM",
                            "PLC":"PLC",
                            "PCN":"PCN",
                            "POBOX":"POBOX",
                            "ADDCODE":"ADDCODE",
                            "SEAT":"SEAT",
                            "RD":"RD",
                            "RDSEC":"RDSEC",
                            "RDBR":"RDBR",
                            "RDSUBBR":"RDSUBBR",
                            "PRM":"PRM",
                            "POM":"POM",
                            "usageRules":"Authorized only",
                            "method":"HTTPS",
                            "providedBy":"User",
                    }],
            },
            "tmgi":3000,
            "upIpv4Addr":dstIp,
            "upIpv6Addr":"2001:db8:85a3::8a2e:370:7338",
            "upPortNum":dstPort,
            "radioFreqs":[4294967295],
            "localMbmsInfo":{
                    "mbmsEnbIpv4MulAddr":"198.51.100.1",
                    "mbmsEnbIpv6MulAddr":"2001:db8:abcd:12::0/64",
                    "mbmsGwIpv4SsmAddr":"198.51.100.2",
                    "mbmsGwIpv6SsmAddr":"2001:db8:85a3::8a2e:370:7336",
                    "cteid":"string",
                    "bmscIpv4Addr":"10.1.1.2",
                    "bmscIpv6Addr":"2001:db8:85a3::8a2e:370:7337",
                    "bmscPort":7777,
            },
            "localMbmsActInd":True,
            "notifUri":"https://www.example.com",
            "reqTestNotif":True,
            "wsNotifCfg": {
                "websocketUri": "string",
                "requestWebsocketUri": True
            },
            "suppFeat": "FFFFF"
        }

        post_data = json.dumps(post_data)
        print(post_data)
        post_data = post_data.encode()

        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)
                
                req = request.Request(url, method="POST")
                req.add_header('Content-Type', 'application/json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                if (loc):
                    req.add_header('Location', self.multiSubId)
                r = request.urlopen(req, data=post_data)
                r_data = r.read().decode('utf-8')
                
                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("Multicast-Subscription POST %f ms" %delay)
                # print(r)
                # print("\n\n")
                # print(json.loads(r))
                # print("\n\n")
                # print(json.loads(r)['Location'])
                # self.multiSubId = json.loads(r)['Location']#r.getheader('Location')
                # print("multiSubId : " + str(self.multiSubId))

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                    if (hasattr(e, 'reason')):
                            while(hasattr(e, 'reason')):
                                time.sleep(10)
                                try:
                                    r = request.urlopen(req, data=post_data)
                                    return
                                except error.URLError as es:
                                    e = es
                                    if hasattr(e, 'reason'):
                                        print('We failed to reach a server.')
                                        print('Reason: ', e.reason)
                                    elif hasattr(e, 'code'):
                                        print('The server couldn\'t fulfill the request.')
                                        print('Error code: ', e.code)
                                        return
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
                else:
                    # everything is fine
                    r = '{}'
                    return 200   
        else:
            r = '{}'
            return 200

        self.multiSubId = r.getheader('Location') #json.loads(r_data)['Location']
        #print(r.getheader('Location'))
        print("uniSubId : " + str(self.multiSubId))

    def NetworkResourceAdaptationMultiGET(self):
        local_test = 1
        url = self.url_SEAL + "ss-nra/v1/multicast-subscriptions/" + self.multiSubId
        print("url: " + url)

        #request is valid for 7 days
        #end_date = date.today() + timedelta(days=7)

        post_data =  {}


        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)

                req = request.Request(url, method="GET")
                req.add_header('Content-Type', 'application/json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                r = request.urlopen(req, data=post_data).read().decode('utf-8')
                print(r)

                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("Multicast-Subscription GET %f ms" %delay)

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                    if (hasattr(e, 'reason')):
                            while(hasattr(e, 'reason')):
                                time.sleep(10)
                                try:
                                    r = request.urlopen(req, data=post_data)
                                    return
                                except error.URLError as es:
                                    e = es
                                    if hasattr(e, 'reason'):
                                        print('We failed to reach a server.')
                                        print('Reason: ', e.reason)
                                    elif hasattr(e, 'code'):
                                        print('The server couldn\'t fulfill the request.')
                                        print('Error code: ', e.code)
                                        return
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
                else:
                    # everything is fine
                    r = '{}'
                    return 200   
        else:
            r = '{}'
            return 200

    def NetworkResourceAdaptationMultiDELETE(self):
        local_test = 1
        url = self.url_SEAL + "ss-nra/v1/multicast-subscriptions/" + self.multiSubId
        print("url: " + url)

        #request is valid for 7 days
        end_date = date.today() + timedelta(days=7)

        post_data =  {}


        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)
                
                req = request.Request(url, method="DELETE")
                req.add_header('Content-Type', 'application/json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                r = request.urlopen(req, data=post_data).read().decode('utf-8')
                print(r)
                self.multiSubId = None

                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("Multicast-Subscription DELETE %f ms" %delay)

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                    if (hasattr(e, 'reason')):
                            i = 1
                            while(hasattr(e, 'reason') and i < 10):
                                time.sleep(10)
                                i += 1
                                try:
                                    r = request.urlopen(req, data=post_data)
                                    return
                                except error.URLError as es:
                                    e = es
                                    if hasattr(e, 'reason'):
                                        print('We failed to reach a server.')
                                        print('Reason: ', e.reason)
                                    elif hasattr(e, 'code'):
                                        print('The server couldn\'t fulfill the request.')
                                        print('Error code: ', e.code)
                                        return
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
                else:
                    # everything is fine
                    r = '{}'
                    return 200   
        else:
            r = '{}'
            return 200



#Location Management - LocationReporting
    def CreateLocReportingConfig(self):
        local_test = 1
        url = self.url_SEAL + "ss-lr/v1/trigger-configurations"
        print("url: " + url)
        

        post_data = {
            "valServerId": "val-Server-Id-1",
            "valTgtUe": {
                "valUserId": str(self.deviceID),
                "valUeId": str(self.deviceID) + "@valdomain.com"
            },
            "immRep": True,
            "monDur": datetime.now(timezone.utc).isoformat()+"Z", #"2024-12-5T09:12:28Z",
            "repPeriod": 1000,
            "accuracy": "GEO_AREA",
                # - CGI_ECGI
                # - ENODEB
                # - TA_RA
                # - PLMN
                # - TWAN_ID
                # - GEO_AREA
                # - CIVIC_ADDR
            "suppFeat": "FFFF"
        }



        post_data = json.dumps(post_data)
        print(post_data)
        post_data = post_data.encode()

        response = None
        response_data = None

        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)

                req = request.Request(url, method="POST")
                req.add_header('Content-Type', 'application/json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                response = request.urlopen(req, data=post_data)
                response_data = response.read().decode('utf-8')

                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("LocationReporting POST %f ms" %delay)

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                    if (hasattr(e, 'reason')):
                            while(hasattr(e, 'reason')):
                                time.sleep(10)
                                try:
                                    response = request.urlopen(req, data=post_data)
                                    response_data = response.read().decode('utf-8')
                                    return
                                except error.URLError as es:
                                    e = es
                                    if hasattr(e, 'reason'):
                                        print('We failed to reach a server.')
                                        print('Reason: ', e.reason)
                                    elif hasattr(e, 'code'):
                                        print('The server couldn\'t fulfill the request.')
                                        print('Error code: ', e.code)
                                        return
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
            else:
                # everything is fine
                # not used
                ret_code = 200  
        else:
            response_data = '''{
                        "valServerId": "val-Server-Id-1",
                        "valTgtUe": {
                            "valUserId": "deviceID",
                            "valUeId":   "deviceID@valdomain.com"
                        },
                        "immRep": "True",
                        "monDur": "2024-12-5T09:12:28Z",
                        "repPeriod": 1000,
                        "accuracy": "GEO_AREA",
                        "suppFeat": "FFFF"
                    }'''

        try:
            self.LocationReportingId = response.getheader('Location')
            print("\n\nREAD-HEADER-('Location') configurationId (LocationReportingId) : " + str(self.LocationReportingId))
            # self.groupDocId = json.loads(response_data)["Location"]
            # print("READ-BODY-LOCATION groupDocId : " + str(self.groupDocId))
        except Exception as e:
            print(response_data)
            data = json.loads(response_data)
            self.LocationReportingId = data['Location']
        print("configurationId : " + str(self.LocationReportingId))

    def RetrieveLocReportingConfig(self):
        local_test = 1
        url = self.url_SEAL + "ss-lr/v1/trigger-configurations/"+self.LocationReportingId
        print("url: " + url)

        post_data = {}

        response = None
        response_data = None

        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)
                
                req = request.Request(url, method="GET")
                req.add_header('Content-Type', 'application/json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                response = request.urlopen(req, data=post_data)
                response_data = response.read().decode('utf-8')

                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("LocationReporting GET %f ms" %delay)

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                    if (hasattr(e, 'reason')):
                            while(hasattr(e, 'reason')):
                                time.sleep(10)
                                try:
                                    response = request.urlopen(req, data=post_data)
                                    response_data = response.read().decode('utf-8')
                                    return
                                except error.URLError as es:
                                    e = es
                                    if hasattr(e, 'reason'):
                                        print('We failed to reach a server.')
                                        print('Reason: ', e.reason)
                                    elif hasattr(e, 'code'):
                                        print('The server couldn\'t fulfill the request.')
                                        print('Error code: ', e.code)
                                        return
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
            else:
                # everything is fine
                # not used
                ret_code = 200  
        else:
            response_data = '''{
                        "valServerId": "val-Server-Id-example",
                        "valTgtUe": {
                            "valUserId": "deviceID",
                            "valUeId":   "deviceID@valdomain.com"
                        },
                        "immRep": "True",
                        "monDur": "2024-12-5T09:12:28Z",
                        "repPeriod": 1000,
                        "accuracy": "GEO_AREA",
                        "suppFeat": "FFFF"
                    }'''

        try:
            self.LocationReportingId = response.getheader('Location') 
        except Exception as e:
            print(response_data)
            data = json.loads(response_data)
            self.LocationReportingId = data['resUri']
        
        print("groupDocId : " + str(self.LocationReportingId))
        print("DATA accessed : \n%s\n\n"%json.dumps(response_data))
        #breakpoint()
        return 200

    def UpdateLocReportingConfig(self):
        local_test = 1
        url = self.url_SEAL + "ss-lr/v1/trigger-configurations/"+self.LocationReportingId
        print("url: " + url)

        post_data = {
            "valServerId": "val-Server-Id-example",
            "valTgtUe": {
                "valUserId": str(self.deviceID+"2"),
                "valUeId": str(self.deviceID+"2") + "@valdomain.com"
            },
            "immRep": True,
            "monDur": datetime.now(timezone.utc).isoformat()+"Z", #"2024-12-5T09:12:28Z",
            "repPeriod": 1000,
            "accuracy": "ENODEB"
                        # - CGI_ECGI
                        # - ENODEB
                        # - TA_RA
                        # - PLMN
                        # - TWAN_ID
                        # - GEO_AREA
                        # - CIVIC_ADDR
            ,
        }
    

        post_data = json.dumps(post_data)
        print(post_data)
        post_data = post_data.encode()

        response = None
        response_data = None

        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)
                
                req = request.Request(url, method="PUT")
                req.add_header('Content-Type', 'application/json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                response = request.urlopen(req,data=post_data)
                response_data = response.read().decode('utf-8')

                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("LocationReporting PUT %f ms" %delay)

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                    if (hasattr(e, 'reason')):
                            while(hasattr(e, 'reason')):
                                time.sleep(10)
                                try:
                                    response = request.urlopen(req, data=post_data)
                                    response_data = response.read().decode('utf-8')
                                    return
                                except error.URLError as es:
                                    e = es
                                    if hasattr(e, 'reason'):
                                        print('We failed to reach a server.')
                                        print('Reason: ', e.reason)
                                    elif hasattr(e, 'code'):
                                        print('The server couldn\'t fulfill the request.')
                                        print('Error code: ', e.code)
                                        return
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
            else:
                # everything is fine
                # not used
                ret_code = 200  
        else:
            response_data = '''{
                    "valGroupId": "string",
                    "grpDesc": "string",
                    "members": [
                        {
                        "valUserId": "string",
                        "valUeId": "string"
                        },
                        {
                        "valUserId": "string",
                        "valUeId": "string"
                        }
                    ],
                    "valGrpConf": "string",
                    "valServiceIds": [
                        "string"
                    ],
                    "valSvcInf": "string",
                    "suppFeat": "string",
                    "resUri": "https://example.com/ss-gm/v1/group-documents/96be8d4d422dd4f90eefd4ace1e4b8"
                    }'''

        try:
            self.LocationReportingId = response.getheader('Location') 
        except Exception as e:
            print(response_data)
            data = json.loads(response_data)
            self.LocationReportingId = data['resUri']
        
        print("LocationReportingId : " + str(self.LocationReportingId))
        print("DATA updated: \n%s\n\n"%json.dumps(response_data))
        #breakpoint()
        return 200
    
    def ModifyLocReportingConfig(self):
        local_test = 1
        url = self.url_SEAL + "ss-lr/v1/trigger-configurations/"+self.LocationReportingId
        print("url: " + url)


        post_data = {
            "valTgtUe": {
                "valUserId": str(self.deviceID+".a"),
                "valUeId": str(self.deviceID+".a") + "@valdomain.com"
            },
            "monDur": datetime.now(timezone.utc).isoformat()+"Z", #"2024-12-5T09:12:28Z",
            "repPeriod": 1000,
            "accuracy": "TWAN_ID",
        }



        post_data = json.dumps(post_data)
        print(post_data)
        post_data = post_data.encode()

        response = None
        response_data = None

        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)
                
                req = request.Request(url, method="PATCH")
                req.add_header('Content-Type', 'application/merge-patch+json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                response = request.urlopen(req, data=post_data)
                response_data = response.read().decode('utf-8')

                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("LocationReporting PATCH %f ms" %delay)

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                    if (hasattr(e, 'reason')):
                            while(hasattr(e, 'reason')):
                                time.sleep(10)
                                try:
                                    response = request.urlopen(req, data=post_data)
                                    response_data = response.read().decode('utf-8')
                                    return
                                except error.URLError as es:
                                    e = es
                                    if hasattr(e, 'reason'):
                                        print('We failed to reach a server.')
                                        print('Reason: ', e.reason)
                                    elif hasattr(e, 'code'):
                                        print('The server couldn\'t fulfill the request.')
                                        print('Error code: ', e.code)
                                        return
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
            else:
                # everything is fine
                # not used
                ret_code = 200  
        else:
            response_data = '''{
                        "valServerId": "val-Server-Id-example",
                        "valTgtUe": {
                            "valUserId": "deviceID",
                            "valUeId":   "deviceID@valdomain.com"
                        },
                        "immRep": "True",
                        "monDur": "2024-12-5T09:12:28Z",
                        "repPeriod": 1000,
                        "accuracy": "GEO_AREA",
                        "suppFeat": "FFFF"
                    }'''

        try:
            self.LocationReportingId = response.getheader('Location')
            print("\n\nREAD-HEADER-('Location') configurationId (LocationReportingId) : " + str(self.LocationReportingId))
            # self.groupDocId = json.loads(response_data)["Location"]
            # print("READ-BODY-LOCATION groupDocId : " + str(self.groupDocId))
        except Exception as e:
            print(response_data)
            data = json.loads(response_data)
            self.LocationReportingId = data['Location']
        print("configurationId : " + str(self.LocationReportingId))
    
    def DeleteLocReportingConfig(self):
        local_test = 1
        url = self.url_SEAL + "ss-lr/v1/trigger-configurations/"+self.LocationReportingId
        print("url: " + url)


        post_data = {}
        response = None
        response_data = None

        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)

                req = request.Request(url, method="DELETE")
                req.add_header('Content-Type', 'application/json')
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                response = request.urlopen(req, data=post_data)
                response_data = response.read().decode('utf-8')

                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("LocationReporting DELETE %f ms" %delay)

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                    if (hasattr(e, 'reason')):
                            while(hasattr(e, 'reason')):
                                time.sleep(10)
                                try:
                                    response = request.urlopen(req, data=post_data)
                                    response_data = response.read().decode('utf-8')
                                    return
                                except error.URLError as es:
                                    e = es
                                    if hasattr(e, 'reason'):
                                        print('We failed to reach a server.')
                                        print('Reason: ', e.reason)
                                    elif hasattr(e, 'code'):
                                        print('The server couldn\'t fulfill the request.')
                                        print('Error code: ', e.code)
                                        return
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
            else:
                # everything is fine
                # not used
                ret_code = 200  
        else:
            response_data = '''{
                        "valServerId": "val-Server-Id-example",
                        "valTgtUe": {
                            "valUserId": "deviceID",
                            "valUeId":   "deviceID@valdomain.com"
                        },
                        "immRep": "True",
                        "monDur": "2024-12-5T09:12:28Z",
                        "repPeriod": 1000,
                        "accuracy": "GEO_AREA",
                        "suppFeat": "FFFF"
                    }'''

        try:
            self.LocationReportingId = response.getheader('Location') 
        except Exception as e:
            print(response_data)
            data = json.loads(response_data)
            self.LocationReportingId = data['resUri']
        
        print("groupDocId : " + str(self.LocationReportingId))
        print("DATA accessed (deleted if empty): \n%s\n\n"%json.dumps(response_data))
        #breakpoint()
        return 200
    



    def LocationAreaInfoRetrieval(self, loc_type = "enodeBId", loc = "4847"):
        local_test = 1

        url = self.url_SEAL + "ss-lair/v1/location-retrievals"
        print("url: " + url)
        post_data = {}
        query1 = { #LocationInfo 
            "ageOfLocationInfo": 0,
            "cellId": "1240838",#"216-30-12007-1240838",
            "enodeBId": "4837",
            "routingAreaId": "string",
            "trackingAreaId": "string",
            "plmnId": json.dumps({"mcc": "216",   "mnc": "30",}),
            "twanId": "TWAN Identity",
            "geographicArea":{   
                                "point":{ "lon": 47.471039, "lat": 19.062555 },
                                "shape" : "POINT",
                                # "innerRadius":327674,
                                # "uncertaintyRadius":254,
                                # "offsetAngle":180,
                                # "includedAngle":180,
                                # "confidence":80,
                            },
            "civicAddress":{ 
                                    "country":"Hungary",
                                    "A1":"A1",
                                    "A2":"A2",
                                    "A3":"A3",
                                    "A4":"A4",
                                    "A5":"A5",
                                    "A6":"A6",
                                    "PRD":"PRD",
                                    "POD":"POD",
                                    "STS":"STS",
                                    "HNO":"HNO",
                                    "HNS":"HNS",
                                    "LMK":"LMK",
                                    "LOC":"LOC",
                                    "NAM":"NAM",
                                    "PC":"PC",
                                    "BLD":"BLD",
                                    "UNIT":"UNIT",
                                    "FLR":"FLR",
                                    "ROOM":"ROOM",
                                    "PLC":"PLC",
                                    "PCN":"PCN",
                                    "POBOX":"POBOX",
                                    "ADDCODE":"ADDCODE",
                                    "SEAT":"SEAT",
                                    "RD":"RD",
                                    "RDSEC":"RDSEC",
                                    "RDBR":"RDBR",
                                    "RDSUBBR":"RDSUBBR",
                                    "PRM":"PRM",
                                    "POM":"POM",
                                    "usageRules":"Authorized only",
                                    "method":"HTTP",
                                    "providedBy":"OPC-UA-subscription-SEAL-User",
                            },
            "positionMethod":"ENODEB",
                            # - CELLID
                            # - ECID
                            # - OTDOA
                            # - BAROMETRIC_PRESSURE
                            # - WLAN
                            # - BLUETOOTH
                            # - MBS
                            # - MOTION_SENSOR
                            # - DL_TDOA
                            # - DL_AOD
                            # - MULTI-RTT
                            # - NR_ECID
                            # - UL_TDOA
                            # - UL_AOA
                            # - NETWORK_SPECIFIC
            "qosFulfilInd":"REQUESTED_ACCURACY_FULFILLED",
            "ueVelocity":{ #HorizontalWithVerticalVelocityAndUncertainty
                    "hSpeed": 100,              #Horizontal speed: 0 - 2047 (float)                         HorizontalVelocity
                    "bearing": 30,              #Horizontal orientation: 0 - 360 (float)                    HorizontalVelocity
                    },
            "ldrType":"BEING_INSIDE_AREA"
                        # - UE_AVAILABLE
                        # - PERIODIC
                        # - ENTERING_INTO_AREA
                        # - LEAVING_FROM_AREA
                        # - BEING_INSIDE_AREA
                        # - MOTION
            ,
            "achievedQos":{
                "hAccuracy": 0.0,
                "vAccuracy": 0.0
            }
        }
        if (loc_type == 'enodeBId'):
            query1['enodeBId'] == loc
            query1['positionMethod'] == "ECID" #CELLID, ECID, NR_ECID
        else:
            if (loc_type == 'routingAreaId'):
                query1['routingAreaId'] == loc
                query1['positionMethod'] == "NETWORK_SPECIFIC"

            elif (loc_type == 'trackingAreaId'):
                query1['trackingAreaId'] == loc
                query1['positionMethod'] == "NETWORK_SPECIFIC"

            elif (loc_type == 'plmnId'):
                query1['plmnId'] == loc
                query1['positionMethod'] == "NR_ECID"#"NETWORK_SPECIFIC"

            elif (loc_type == 'twanId'):
                query1['twanId'] == loc
                query1['positionMethod'] == "WLAN"

            elif (loc_type == 'geographicArea'):
                query1['geographicArea'] == loc
                query1['positionMethod'] == "OTDOA"

            elif (loc_type == 'civicAddress'):
                query1['civicAddress'] == loc
                query1['positionMethod'] == "CIVIC_LOOKUP" #NETWORK_SPECIFIC, MOTION_SENSOR, CIVIC_LOOKUP
            
            elif (loc_type == "cellid"):
                query1['cellid'] == loc #216-30-12007-1240836
                query1['positionMethod'] == "CELLID" #CELLID, ECID, NR_ECID

            elif loc == "4847" and (loc_type != "enodeBId" or loc_type != "ENODEB"):
                print("Location incorrect")
                raise ValueError
  
        # query1['qosFulfilInd'] == ""
                
        query2 = 150.02; #range

        params = flatten_dict(query1, parent_key="location-info")
        # # params = {f"location-info[{k}]=": v for k, v in query1.items()}
        params["range"] = query2
        # params = {"location-info": json.dumps(query1, separators=(",", ":")), "range": query2}

        # params = {
        #     "location-info[positionMethod]": "enodeBId",
        #     "location-info[enodeBId]": 4847,
        #     "range": query2
        # }

        # params = {"location-info": query1, "range": query2}

        # params = {"location-info": query1, "range": query2}

        # query_string = parse.quote(json.dumps(query1))
        # query_string = flatten_dict(query1)
        # # url = f"{url}?{query_string}"
        # # query_string = parse.urlencode(query1)
        # # print(url + "?location-info=" +query_string +"&range=%f"%query2)
        # # url = f"{url}?location-info={ query_string }&range={query2}"
        # # url= url + "?location-info=" +query_string +"&range=%f"%query2

        url = url +"?location-info=%s&range=%f"%(json.loads(query1),query2)

        response = None
        response_data = None
        
        
        print(url)

        if self.local_test == 0:
            try:
                start = time.time() * 1000
                print("Sending request: %f ms" %start)
                # response =requests.get(url, params=params, json=query1, headers={ 'Authorization': 'Bearer ' + self.auth_token}, timeout=10)
                req = request.Request(url, method="GET")
                req.add_header('Authorization', 'Bearer ' + self.auth_token)
                
                response = request.urlopen(req, data=post_data, timeout=10)
                response_data = response.read().decode('utf-8')

                end = time.time() * 1000
                print("Receiving request response: %f ms" %end)
                delay = end - start
                print("Roundtrip Delay: %f ms" %delay)
                print("Oneway Delay: ~%f ms (+half of message processing time of server)" %(delay/2))
                print("LocationAreaInfoRetrieval GET %f ms" %delay)

            except error.URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                    if (hasattr(e, 'reason')):
                            while(hasattr(e, 'reason')):
                                time.sleep(10)
                                try:
                                    # response = requests.get(url, params=params, headers={'Authorization': 'Bearer ' + self.auth_token}, timeout=10)
                                    response = request.urlopen(req, data=post_data)
                                    response_data = response.read().decode('utf-8')
                                    return
                                except error.URLError as es:
                                    e = es
                                    if hasattr(e, 'reason'):
                                        print('We failed to reach a server.')
                                        print('Reason: ', e.reason)
                                    elif hasattr(e, 'code'):
                                        print('The server couldn\'t fulfill the request.')
                                        print('Error code: ', e.code)
                                        return
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
            else:
                # everything is fine
                # not used
                ret_code = 200  
        else:
            # resp = '''{
            #             "valServerId": "val-Server-Id-1",
            #             "valTgtUe": {
            #                 "valUserId": "deviceID",
            #                 "valUeId":   "deviceID@valdomain.com"
            #             },
            #             "immRep": "True",
            #             "monDur": "2024-12-5T09:12:28Z",
            #             "repPeriod": 1000,
            #             "accuracy": "GEO_AREA",
            #             "suppFeat": "FFFF"
            #         }'''
            
            response_data = {
                    "valTgtUe": {
                        "valUserId":"deviceID",
                        "valUeId":"deviceID@valdomain.com",
                    },
                    "locInfo": {
                        "ageOfLocationInfo": 0,#Integer (int32): minimum 0
                        "cellId": "Cella_ID_string_example",
                        "enodeBId": "enodeB_Identifier_string",
                        "routingAreaId": "string",
                        "trackingAreaId": "string",
                        "plmnId": "PLMN Identity",
                        "twanId": "TWAN Identity",
                        "geographicArea":#[ #minimum array length: 1
                                {   
                                    "point":{ 
                                            "lon": 47.47131, 
                                            "lat": 19.062889,
                                            # "innerRadius":327674,
                                            # "uncertaintyRadius":254,
                                            # "offsetAngle":180,
                                            # "includedAngle":180,
                                            # "confidence":80,
                                    },
                                    "shape":"POINT",  
                                    #"shape" : "POINT",
                                    # - POINT
                                    # - POINT_UNCERTAINTY_CIRCLE
                                    # - POINT_UNCERTAINTY_ELLIPSE
                                    # - POLYGON
                                    # - POINT_ALTITUDE
                                    # - POINT_ALTITUDE_UNCERTAINTY
                                    # - ELLIPSOID_ARC
                                    # - LOCAL_2D_POINT_UNCERTAINTY_ELLIPSE
                                    # - LOCAL_3D_POINT_UNCERTAINTY_ELLIPSOID
                                },
                            #],
                        "civicAddress":#[ #minimum array length: 1
                            { 
                                    "country":"Hungary",
                                    "A1":"A1",
                                    "A2":"A2",
                                    "A3":"A3",
                                    "A4":"A4",
                                    "A5":"A5",
                                    "A6":"A6",
                                    "PRD":"PRD",
                                    "POD":"POD",
                                    "STS":"STS",
                                    "HNO":"HNO",
                                    "HNS":"HNS",
                                    "LMK":"LMK",
                                    "LOC":"LOC",
                                    "NAM":"NAM",
                                    "PC":"PC",
                                    "BLD":"BLD",
                                    "UNIT":"UNIT",
                                    "FLR":"FLR",
                                    "ROOM":"ROOM",
                                    "PLC":"PLC",
                                    "PCN":"PCN",
                                    "POBOX":"POBOX",
                                    "ADDCODE":"ADDCODE",
                                    "SEAT":"SEAT",
                                    "RD":"RD",
                                    "RDSEC":"RDSEC",
                                    "RDBR":"RDBR",
                                    "RDSUBBR":"RDSUBBR",
                                    "PRM":"PRM",
                                    "POM":"POM",
                                    "usageRules":"Authorized only",
                                    "method":"HTTP",
                                    "providedBy":"OPC-UA-subscription-SEAL-User",
                            },
                        #],
                        "positionMethod": "CELLID",
                                        # - CELLID
                                        # - ECID
                                        # - OTDOA
                                        # - BAROMETRIC_PRESSURE
                                        # - WLAN
                                        # - BLUETOOTH
                                        # - MBS
                                        # - MOTION_SENSOR
                                        # - DL_TDOA
                                        # - DL_AOD
                                        # - MULTI-RTT
                                        # - NR_ECID
                                        # - UL_TDOA
                                        # - UL_AOA
                                        # - NETWORK_SPECIFIC
                        "qosFulFilInd": "REQUESTED_ACCURACY_FULFILLED",
                                        # - REQUESTED_ACCURACY_FULFILLED
                                        # - REQUESTED_ACCURACY_NOT_FULFILLED  
                        "ueVelocity": { #HorizontalWithVerticalVelocityAndUncertainty
                            "hSpeed": 100,                #Horizontal speed: 0 - 2047 (float)                         HorizontalVelocity
                            "bearing": 30,                #Horizontal orientation: 0 - 360 (float)                    HorizontalVelocity
                            # "vSpeed": 0,                #Vertical speed: 0 - 255 (float)                            HorizontalWithVerticalVelocity
                            # "vDirection": "DOWNWARD",   #Dir of vertical speed: UPWARD / DOWNWARD                   HorizontalWithVerticalVelocity
                            # "hUncertainty": 0,          #Indicates value of speed uncertainty: 0 - 255 (float)      HorizontalWithVerticalVelocityAndUncertainty
                            # "vUncertainty": 0           #Same for vSpeed                                            HorizontalWithVerticalVelocityAndUncertainty
                        },
                            # HorizontalVelocity
                            # HorizontalWithVerticalVelocity
                        "ldrType": "BEING_INSIDE_AREA",
                                    # - UE_AVAILABLE
                                    # - PERIODIC
                                    # - ENTERING_INTO_AREA
                                    # - LEAVING_FROM_AREA
                                    # - BEING_INSIDE_AREA
                                    # - MOTION
                        "achievedQos":{
                            "hAccuracy": 0.5, #min val 0 float
                            "vAccuracy": 0.5
                        }
                    },
                    "timeStamp": "2024-12-5T09:12:28Z",
                    "valSvcId":"string"
                }

        try:
            self.LocationArea = response.getheader('Location') 
        except Exception as e:
            print(response_data)
            data = json.loads(response_data)
            self.LocationArea = data['resUri']
        
        print("LocationArea : " + str(self.LocationArea))
        print("DATA accessed : \n%s\n\n"%json.dumps(response_data))
        #breakpoint()
        return 200







