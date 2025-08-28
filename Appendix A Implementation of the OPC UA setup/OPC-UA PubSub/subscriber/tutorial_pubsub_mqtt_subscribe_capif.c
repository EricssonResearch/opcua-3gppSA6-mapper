/* This work is licensed under a Creative Commons CCZero 1.0 Universal License.
 * See http://creativecommons.org/publicdomain/zero/1.0/ for more information.
 *
 * Copyright (c) 2022 Fraunhofer IOSB (Author: Noel Graf)
 */

#include <open62541/plugin/log_stdout.h>
#include <open62541/server.h>
#include <open62541/plugin/securitypolicy_default.h>
#include <open62541/plugin/pubsub_mqtt.h>
//UNIX socket
#include <sys/socket.h>
#include <sys/un.h>
//JSON
#include "cJSON/cJSON.h"
#include "cJSON/cJSON.c"
#include <stdlib.h>
//#include <sys/time.h>

#define CONNECTION_NAME               "MQTT Subscriber Connection"
#define TRANSPORT_PROFILE_URI         "http://opcfoundation.org/UA-Profile/Transport/pubsub-mqtt"
#define MQTT_CLIENT_ID                "OPC_UA_Subscriber"
#define CONNECTIONOPTION_NAME         "mqttClientId"

#define SUBSCRIBER_TOPIC              "topic1"
#define SUBSCRIBER_TOPIC2              "topic2"

#define SUBSCRIBER_METADATAQUEUENAME  "MetaDataTopic"
#define SUBSCRIBER_METADATAUPDATETIME 0
//#define BROKER_ADDRESS_URL            "opc.mqtt://10.1.2.2:8883"
#define BROKER_ADDRESS_URL            "opc.mqtt://127.0.0.1:8883"
#define SUBSCRIBE_INTERVAL            600
#define SUBSCRIBE_INTERVAL2            500

// Uncomment the following line to enable MQTT login for the example
// #define EXAMPLE_USE_MQTT_LOGIN

#ifdef EXAMPLE_USE_MQTT_LOGIN
#define LOGIN_OPTION_COUNT           2
#define USERNAME_OPTION_NAME         "mqttUsername"
#define PASSWORD_OPTION_NAME         "mqttPassword"
#define MQTT_USERNAME                "open62541user"
#define MQTT_PASSWORD                "open62541"
#endif

// Uncomment the following line to enable MQTT via TLS for the example
//#define EXAMPLE_USE_MQTT_TLS

#ifdef EXAMPLE_USE_MQTT_TLS
#define TLS_OPTION_COUNT                2
#define USE_TLS_OPTION_NAME             "mqttUseTLS"
#define MQTT_CA_FILE_PATH_OPTION_NAME   "mqttCaFilePath"
#define CA_FILE_PATH                    "/path/to/server.cert"
#endif

#if defined(UA_ENABLE_PUBSUB_ENCRYPTION) && !defined(UA_ENABLE_JSON_ENCODING)
#define UA_AES128CTR_SIGNING_KEY_LENGTH 32
#define UA_AES128CTR_KEY_LENGTH 16
#define UA_AES128CTR_KEYNONCE_LENGTH 4

UA_Byte signingKey[UA_AES128CTR_SIGNING_KEY_LENGTH] = {0};
UA_Byte encryptingKey[UA_AES128CTR_KEY_LENGTH] = {0};
UA_Byte keyNonce[UA_AES128CTR_KEYNONCE_LENGTH] = {0};
#endif

#ifdef UA_ENABLE_JSON_ENCODING
static UA_Boolean useJson = true;
#else
static UA_Boolean useJson = false;
#endif

UA_NodeId connectionIdent;
UA_NodeId subscribedDataSetIdent;
UA_NodeId subscribedDataSetIdent2;
UA_NodeId readerGroupIdent;
UA_NodeId readerGroupIdent2;



UA_DataSetReaderConfig readerConfig;

static void fillTestDataSetMetaData(UA_DataSetMetaDataType *pMetaData, char*);

static UA_StatusCode
addPubSubConnection(UA_Server *server, char *addressUrl) {
    UA_StatusCode retval = UA_STATUSCODE_GOOD;
    /* Details about the connection configuration and handling are located
     * in the pubsub connection tutorial */
    UA_PubSubConnectionConfig connectionConfig;
    memset(&connectionConfig, 0, sizeof(connectionConfig));
    connectionConfig.name = UA_STRING(CONNECTION_NAME);
    connectionConfig.transportProfileUri = UA_STRING(TRANSPORT_PROFILE_URI);
    connectionConfig.enabled = UA_TRUE;

    /* configure address of the mqtt broker (local on default port) */
    UA_NetworkAddressUrlDataType networkAddressUrl = {UA_STRING_NULL , UA_STRING(addressUrl)};
    UA_Variant_setScalar(&connectionConfig.address, &networkAddressUrl,
                         &UA_TYPES[UA_TYPES_NETWORKADDRESSURLDATATYPE]);
    /* Changed to static publisherId from random generation to identify
     * the publisher on Subscriber side */
    connectionConfig.publisherIdType = UA_PUBLISHERIDTYPE_UINT16;
    connectionConfig.publisherId.uint16 = 2234;

    /* configure options, set mqtt client id */
    const int connectionOptionsCount = 2
#ifdef EXAMPLE_USE_MQTT_LOGIN
    + LOGIN_OPTION_COUNT
#endif
#ifdef EXAMPLE_USE_MQTT_TLS
    + TLS_OPTION_COUNT
#endif
    ;

    UA_KeyValuePair connectionOptions[connectionOptionsCount];

    size_t connectionOptionIndex = 0;
    connectionOptions[connectionOptionIndex].key = UA_QUALIFIEDNAME(0, CONNECTIONOPTION_NAME);
    UA_String mqttClientId = UA_STRING(MQTT_CLIENT_ID);
    UA_Variant_setScalar(&connectionOptions[connectionOptionIndex++].value, &mqttClientId, &UA_TYPES[UA_TYPES_STRING]);



#ifdef EXAMPLE_USE_MQTT_LOGIN
    connectionOptions[connectionOptionIndex].key = UA_QUALIFIEDNAME(0, USERNAME_OPTION_NAME);
    UA_String mqttUsername = UA_STRING(MQTT_USERNAME);
    UA_Variant_setScalar(&connectionOptions[connectionOptionIndex++].value, &mqttUsername, &UA_TYPES[UA_TYPES_STRING]);

    connectionOptions[connectionOptionIndex].key = UA_QUALIFIEDNAME(0, PASSWORD_OPTION_NAME);
    UA_String mqttPassword = UA_STRING(MQTT_PASSWORD);
    UA_Variant_setScalar(&connectionOptions[connectionOptionIndex++].value, &mqttPassword, &UA_TYPES[UA_TYPES_STRING]);
#endif

#ifdef EXAMPLE_USE_MQTT_TLS
    connectionOptions[connectionOptionIndex].key = UA_QUALIFIEDNAME(0, USE_TLS_OPTION_NAME);
    UA_Boolean mqttUseTLS = true;
    UA_Variant_setScalar(&connectionOptions[connectionOptionIndex++].value, &mqttUseTLS, &UA_TYPES[UA_TYPES_BOOLEAN]);

    connectionOptions[connectionOptionIndex].key = UA_QUALIFIEDNAME(0, MQTT_CA_FILE_PATH_OPTION_NAME);
    UA_String mqttCaFile = UA_STRING(CA_FILE_PATH);
    UA_Variant_setScalar(&connectionOptions[connectionOptionIndex++].value, &mqttCaFile, &UA_TYPES[UA_TYPES_STRING]);
#endif

    connectionConfig.connectionProperties.map = connectionOptions;
    connectionConfig.connectionProperties.mapSize = connectionOptionIndex;

    retval |= UA_Server_addPubSubConnection(server, &connectionConfig, &connectionIdent);

    return retval;
}

/**
 * **ReaderGroup**
 *
 * ReaderGroup is used to group a list of DataSetReaders. All ReaderGroups are
 * created within a PubSubConnection and automatically deleted if the connection
 * is removed. All network message related filters are only available in the DataSetReader. */
/* Add ReaderGroup to the created connection */
static UA_StatusCode
addReaderGroup(UA_Server *server, char* readername, UA_NodeId *readerGroupIdent, char* topic,  int interval, UA_BrokerTransportQualityOfService QoS) {
    if(server == NULL) {
        return UA_STATUSCODE_BADINTERNALERROR;
    }
    //printf("addReaderGroup begin: %d\n", readerGroupIdent->identifier);
    UA_StatusCode retval = UA_STATUSCODE_GOOD;
    UA_ReaderGroupConfig readerGroupConfig;
    memset (&readerGroupConfig, 0, sizeof(UA_ReaderGroupConfig));
    readerGroupConfig.name = UA_STRING(readername);
    readerGroupConfig.subscribingInterval = interval;
    if(useJson)
        readerGroupConfig.encodingMimeType = UA_PUBSUB_ENCODING_JSON;

    /* configure the mqtt publish topic */
    UA_BrokerWriterGroupTransportDataType brokerTransportSettings;
    memset(&brokerTransportSettings, 0, sizeof(UA_BrokerWriterGroupTransportDataType));
    /* Assign the Topic at which MQTT publish should happen */
    /*ToDo: Pass the topic as argument from the reader group */
    //brokerTransportSettings.queueName = UA_STRING(SUBSCRIBER_TOPIC);
    brokerTransportSettings.queueName = UA_STRING(topic);
    brokerTransportSettings.resourceUri = UA_STRING_NULL;
    brokerTransportSettings.authenticationProfileUri = UA_STRING_NULL;

    /* Choose the QOS Level for MQTT */
    //brokerTransportSettings.requestedDeliveryGuarantee = UA_BROKERTRANSPORTQUALITYOFSERVICE_BESTEFFORT;
    brokerTransportSettings.requestedDeliveryGuarantee = QoS;
    

    /* Encapsulate config in transportSettings */
    UA_ExtensionObject transportSettings;
    memset(&transportSettings, 0, sizeof(UA_ExtensionObject));
    transportSettings.encoding = UA_EXTENSIONOBJECT_DECODED;
    transportSettings.content.decoded.type = &UA_TYPES[UA_TYPES_BROKERDATASETREADERTRANSPORTDATATYPE];
    transportSettings.content.decoded.data = &brokerTransportSettings;

    readerGroupConfig.transportSettings = transportSettings;

#if defined(UA_ENABLE_PUBSUB_ENCRYPTION) && !defined(UA_ENABLE_JSON_ENCODING)
    /* Encryption settings */
    UA_ServerConfig *config = UA_Server_getConfig(server);
    readerGroupConfig.securityMode = UA_MESSAGESECURITYMODE_SIGNANDENCRYPT;
    readerGroupConfig.securityPolicy = &config->pubSubConfig.securityPolicies[0];
#endif
#include <stdlib.h>#include <stdlib.h>
    retval |= UA_Server_addReaderGroup(server, connectionIdent, &readerGroupConfig,
                                       readerGroupIdent);
    if (retval != UA_STATUSCODE_GOOD)
        printf("\n\n UA_Server_addReaderGroup: %d", retval);
    
#if defined(UA_ENABLE_PUBSUB_ENCRYPTION) && !defined(UA_ENABLE_JSON_ENCODING)
    /* Add the encryption key informaton */
    UA_ByteString sk = {UA_AES128CTR_SIGNING_KEY_LENGTH, signingKey};
    UA_ByteString ek = {UA_AES128CTR_KEY_LENGTH, encryptingKey};
    UA_ByteString kn = {UA_AES128CTR_KEYNONCE_LENGTH, keyNonce};

    // TODO security token not necessary for readergroup (extracted from security-header)
    retval |= UA_Server_setReaderGroupEncryptionKeys(server, *readerGroupIdent, 1, sk, ek, kn);
#endif
    retval |= UA_Server_setReaderGroupOperational(server, *readerGroupIdent);
    if (retval != UA_STATUSCODE_GOOD)
        printf("\n\n UA_Server_setReaderGroupOperational: %d", retval);
        
    //printf("addReaderGroup end: %d\n", readerGroupIdent->identifier);
    return retval;
}



/**
 * **ReaderGroup** **updating function**
 *
 * ReaderGroup is used to group a list of DataSetReaders. All ReaderGroups are
 * created within a PubSubConnection and automatically deleted if the connection
 * is removed. All network message related filters are only available in the DataSetReader. 
 * It is only possible to update the publishing/reading interval*/
// static UA_StatusCode
// updateReaderGroup(UA_Server *server, char* readername, UA_NodeId *readerGroupIdent, char* topic,  int interval, UA_BrokerTransportQualityOfService QoS) {
// UA_ReaderGroup_removeSubscribeCallback(UA_Server *server, UA_ReaderGroup *readerGroup);
// UA_ReaderGroup_addSubscribeCallback(UA_Server *server, UA_ReaderGroup *readerGroup);
// }





/**
 * **DataSetReader**
 *
 * DataSetReader can receive NetworkMessages with the DataSetMessage
 * of interest sent by the Publisher. DataSetReader provides
 * the configuration necessary to receive and process DataSetMessages
 * on the Subscriber side. DataSetReader must be linked with a
 * SubscribedDataSet and be contained within a ReaderGroup. */
/* Add DataSetReader to the ReaderGroup */
static UA_StatusCode
addDataSetReader(UA_Server *server, UA_NodeId readerGroupIdent, char* DataSetReaderName, char* DataSetName, UA_NodeId *subscribedDataSetIdent) {
    if(server == NULL) {
        return UA_STATUSCODE_BADINTERNALERROR;
    }

    UA_StatusCode retval = UA_STATUSCODE_GOOD;
    memset (&readerConfig, 0, sizeof(UA_DataSetReaderConfig));
    readerConfig.name = UA_STRING(DataSetReaderName);
    /* Parameters to filter which DataSetMessage has to be processed
     * by the DataSetReader */
    /* The following parameters are used to show that the data published by
     * tutorial_pubsub_mqtt_publish.c is being subscribed and is being updated in
     * the information model */
    UA_UInt16 publisherIdentifier = 2234;
    readerConfig.publisherId.type = &UA_TYPES[UA_TYPES_UINT16];
    readerConfig.publisherId.data = &publisherIdentifier;
    readerConfig.writerGroupId    = 100;
    readerConfig.dataSetWriterId  = 62541;
#ifdef UA_ENABLE_PUBSUB_MONITORING
    readerConfig.messageReceiveTimeout = 10;
#endif

    /* Setting up Meta data configuration in DataSetReader */
    fillTestDataSetMetaData(&readerConfig.dataSetMetaData, DataSetName);
    //printf("%s",readerConfig,"\n",DataSetName);
    retval |= UA_Server_addDataSetReader(server, readerGroupIdent, &readerConfig,
                                         subscribedDataSetIdent);
    
    if (retval != UA_STATUSCODE_GOOD)
        printf("\n\n UA_Server_addDataSetReader: %d", retval);
    
    return retval;
}

/**
 * **SubscribedDataSet**
 *
 * Set SubscribedDataSet type to TargetVariables data type.
 * Add subscribedvariables to the DataSetReader */
static UA_StatusCode
addSubscribedVariables (UA_Server *server, UA_NodeId dataSetReaderId, int nsi) {
    if(server == NULL)
        return UA_STATUSCODE_BADINTERNALERROR;

    UA_StatusCode retval = UA_STATUSCODE_GOOD;
    UA_NodeId folderId;
    UA_String folderName = readerConfig.dataSetMetaData.name;
    UA_ObjectAttributes oAttr = UA_ObjectAttributes_default;
    UA_QualifiedName folderBrowseName;
    if(folderName.length > 0) {
        oAttr.displayName.locale = UA_STRING ("en-US");
        oAttr.displayName.text = folderName;
        folderBrowseName.namespaceIndex = 1;
        folderBrowseName.name = folderName;
    }
    else {
        oAttr.displayName = UA_LOCALIZEDTEXT ("en-US", "Subscribed Variables");
        folderBrowseName = UA_QUALIFIEDNAME (1, "Subscribed Variables");
    }

    UA_Server_addObjectNode (server, UA_NODEID_NULL,
                             UA_NODEID_NUMERIC (0, UA_NS0ID_OBJECTSFOLDER),
                             UA_NODEID_NUMERIC (0, UA_NS0ID_ORGANIZES),
                             folderBrowseName, UA_NODEID_NUMERIC (0,
                             UA_NS0ID_BASEOBJECTTYPE), oAttr, NULL, &folderId);
    if (retval != UA_STATUSCODE_GOOD)
        printf("\n\n UA_Server_addObjectNode: %d", retval);

/**
 * **TargetVariables**
 *
 * The SubscribedDataSet option TargetVariables defines a list of Variable mappings between
 * received DataSet fields and target Variables in the Subscriber AddressSpace.
 * The values subscribed from the Publisher are updated in the value field of these variables */
    /* Create the TargetVariables with respect to DataSetMetaData fields */
    UA_FieldTargetVariable *targetVars = (UA_FieldTargetVariable *)
        UA_calloc(readerConfig.dataSetMetaData.fieldsSize, sizeof(UA_FieldTargetVariable));
    for(size_t i = 0; i < readerConfig.dataSetMetaData.fieldsSize; i++) {
        /* Variable to subscribe data */
        UA_VariableAttributes vAttr = UA_VariableAttributes_default;
        UA_LocalizedText_copy(&readerConfig.dataSetMetaData.fields[i].description,
                              &vAttr.description);
        vAttr.displayName.locale = UA_STRING("en-US");
        vAttr.displayName.text = readerConfig.dataSetMetaData.fields[i].name;
        vAttr.dataType = readerConfig.dataSetMetaData.fields[i].dataType;

        UA_NodeId newNode;
        retval |= UA_Server_addVariableNode(server, 
        				    UA_NODEID_NUMERIC(1, (UA_UInt32)i + nsi),
                                            folderId,
                                            UA_NODEID_NUMERIC(0, UA_NS0ID_HASCOMPONENT),
                                            UA_QUALIFIEDNAME(1, (char*)readerConfig.dataSetMetaData.fields[i].name.data),
                                            UA_NODEID_NUMERIC(0, UA_NS0ID_BASEDATAVARIABLETYPE),
                                            vAttr, NULL, &newNode);
        if (retval != UA_STATUSCODE_GOOD){
        	printf("\n\n UA_Server_addVariableNode: %d ", retval);
        	//printf("newNode: %s ", newNode);
}
	//printf("newNode: %d ", newNode);
        /* For creating Targetvariables */
        UA_FieldTargetDataType_init(&targetVars[i].targetVariable);
        targetVars[i].targetVariable.attributeId  = UA_ATTRIBUTEID_VALUE;
        targetVars[i].targetVariable.targetNodeId = newNode;
    }

    retval = UA_Server_DataSetReader_createTargetVariables(server, dataSetReaderId, readerConfig.dataSetMetaData.fieldsSize, targetVars);
    if (retval != UA_STATUSCODE_GOOD)
    {
        printf("\n\n UA_Server_DataSetReader_createTargetVariables: %d \n", retval);
        //printf("dataSetReaderId: %s \n", dataSetReaderId);
        }
    for(size_t i = 0; i < readerConfig.dataSetMetaData.fieldsSize; i++)
        UA_FieldTargetDataType_clear(&targetVars[i].targetVariable);

    UA_free(targetVars);
    UA_free(readerConfig.dataSetMetaData.fields);
    return retval;
}

/**
 * **DataSetMetaData**
 *
 * The DataSetMetaData describes the content of a DataSet. It provides the information necessary to decode
 * DataSetMessages on the Subscriber side. DataSetMessages received from the Publisher are decoded into
 * DataSet and each field is updated in the Subscriber based on datatype match of TargetVariable fields of Subscriber
 * and PublishedDataSetFields of Publisher */
/* Define MetaData for TargetVariables */
static void fillTestDataSetMetaData(UA_DataSetMetaDataType *pMetaData, char* DataSetName) {
    if(pMetaData == NULL) {
        return;
    }

    UA_DataSetMetaDataType_init (pMetaData);
    pMetaData->name = UA_STRING (DataSetName);

    /* Static definition of number of fields size to 4 to create four different
     * targetVariables of distinct datatype
     * Currently the publisher sends only DateTime data type */
    pMetaData->fieldsSize = 4;
    pMetaData->fields = (UA_FieldMetaData*)UA_Array_new (pMetaData->fieldsSize,
                                                         &UA_TYPES[UA_TYPES_FIELDMETADATA]);

    /* DateTime DataType */
    UA_FieldMetaData_init (&pMetaData->fields[0]);
    UA_NodeId_copy (&UA_TYPES[UA_TYPES_DATETIME].typeId,
                    &pMetaData->fields[0].dataType);
    pMetaData->fields[0].builtInType = UA_NS0ID_DATETIME;
    pMetaData->fields[0].name =  UA_STRING ("DateTime");
    pMetaData->fields[0].valueRank = -1; /* scalar */

    /* Int32 DataType */
    UA_FieldMetaData_init (&pMetaData->fields[1]);
    UA_NodeId_copy(&UA_TYPES[UA_TYPES_INT32].typeId,
                   &pMetaData->fields[1].dataType);
    pMetaData->fields[1].builtInType = UA_NS0ID_INT32;
    pMetaData->fields[1].name =  UA_STRING ("Int32");
    pMetaData->fields[1].valueRank = -1; /* scalar */

    /* Int64 DataType */
    UA_FieldMetaData_init (&pMetaData->fields[2]);
    UA_NodeId_copy(&UA_TYPES[UA_TYPES_INT64].typeId,
                   &pMetaData->fields[2].dataType);
    pMetaData->fields[2].builtInType = UA_NS0ID_INT64;
    pMetaData->fields[2].name =  UA_STRING ("Int64");
    pMetaData->fields[2].valueRank = -1; /* scalar */

    /* Boolean DataType */
    UA_FieldMetaData_init (&pMetaData->fields[3]);
    UA_NodeId_copy (&UA_TYPES[UA_TYPES_BOOLEAN].typeId,
                    &pMetaData->fields[3].dataType);
    pMetaData->fields[3].builtInType = UA_NS0ID_BOOLEAN;
    pMetaData->fields[3].name =  UA_STRING ("BoolToggle");
    pMetaData->fields[3].valueRank = -1; /* scalar */
}



// Signal handler to handle Ctrl+C and clean up resources
void handle_signal(int signo) {
    printf("Received signal %d. Cleaning up...\n", signo);
    // Cleanup code here
    exit(0);
}



static void usage(void) {
    printf("Usage: tutorial_pubsub_mqtt_subscribe [--url <opc.mqtt://hostname:port>] "
           "[--topic <1 or 2 mqttTopics, with space in between>] "
           "[--freq <1 or 2 frequencies in ms, with space in between>]"
           "[--json]\n"
           "  Defaults are:\n"
           "  - Url: opc.mqtt://127.0.0.1:1883\n"
           "  - Topic: topic1 topic2\n"
           "  - Frequency: 600 500\n"
           "  - JSON: Off\n");
}


/**
 * Followed by the main server code, making use of the above definitions */

int main(int argc, char **argv) {
    char *addressUrl = BROKER_ADDRESS_URL;
    char *topic = SUBSCRIBER_TOPIC;
    char *topic2 = SUBSCRIBER_TOPIC2;
    int interval = SUBSCRIBE_INTERVAL;
    int interval2 = SUBSCRIBE_INTERVAL2;
    char *unix_path = "/tmp/capif_pubsub_interval_inv";
    //struct timespec start;
    
    UA_BrokerTransportQualityOfService ATLEASTONCE = UA_BROKERTRANSPORTQUALITYOFSERVICE_ATLEASTONCE;
    UA_BrokerTransportQualityOfService BESTEFFORT = UA_BROKERTRANSPORTQUALITYOFSERVICE_BESTEFFORT;

    //Handle Interrupt and socket data set up
    signal(SIGINT, handle_signal);
    int server_socket;
    int client_socket;
    int connection_result;
    struct sockaddr_un server_addr;


    /* Parse arguments */
    // for (int argpos = 1; argpos < argc; argpos++) {
    //     printf("%s\n",argv[argpos]);
    // }
    for(int argpos = 1; argpos < argc; argpos++) {
        if(strcmp(argv[argpos], "--help") == 0) {
            usage();
            return 0;
        }

        if(strcmp(argv[argpos], "--json") == 0) {
            useJson = true;
            continue;
        }

        if(strcmp(argv[argpos], "--url") == 0) {
            if(argpos + 1 == argc) {
                usage();
                return -1;
            }
            argpos++;
            addressUrl = argv[argpos];
            continue;
        }

        if(strcmp(argv[argpos], "--topic") == 0) {
            if(argpos + 1 == argc) {
                usage();
                return -1;
            }
            argpos++;
            topic = argv[argpos];
            //printf("%s\n", topic);

            if (strstr(argv[argpos + 1], "--") == NULL){
                if(argpos + 1 < argc) {
                    argpos++;
                    topic2 = argv[argpos];
                    //printf("%s\n",topic2);
                }
            } 
            continue;
        }

        if(strcmp(argv[argpos], "--freq") == 0) {
            if(argpos + 1 == argc) {
                usage();
                return -1;
            }
            argpos++;
            if(sscanf(argv[argpos], "%d", &interval) != 1) {
                usage();
                return -1;
            }
            if(interval <= 10) {
                UA_LOG_WARNING(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                               "Publication interval too small");
                return -1;
            }
            
            if (strstr(argv[argpos + 1], "--") == NULL){
                if(argpos + 1 < argc) {
                    argpos++;
                    if(sscanf(argv[argpos], "%d", &interval2) != 1) {
                        usage();
                        return -1;
                    }
                    if(interval2 <= 10) {
                        UA_LOG_WARNING(UA_Log_Stdout, UA_LOGCATEGORY_USERLAND,
                                    "Publication interval too small");
                        return -1;
                    }    
                }
            } 
            continue;
        }

        usage();
        return -1;
    }

    /* Return value initialized to Status Good */
    UA_StatusCode retval = UA_STATUSCODE_GOOD;
    UA_StatusCode retval2 = UA_STATUSCODE_GOOD;
    //A_StatusCode retval2 = UA_STATUSCODE_GOOD;
    UA_Server *server = UA_Server_new();
    UA_ServerConfig *config = UA_Server_getConfig(server);

#if defined(UA_ENABLE_PUBSUB_ENCRYPTION) && !defined(UA_ENABLE_JSON_ENCODING)
    /* Instantiate the PubSub SecurityPolicy */
    config->pubSubConfig.securityPolicies = (UA_PubSubSecurityPolicy*)
        UA_malloc(sizeof(UA_PubSubSecurityPolicy));
    config->pubSubConfig.securityPoliciesSize = 1;
    UA_PubSubSecurityPolicy_Aes128Ctr(config->pubSubConfig.securityPolicies,
                                      &config->logger);
#endif

    UA_ServerConfig_addPubSubTransportLayer(config, UA_PubSubTransportLayerMQTT());

    /* API calls */
    /* Add PubSubConnection */
    retval |= addPubSubConnection(server, addressUrl);
    if (retval != UA_STATUSCODE_GOOD)
        return EXIT_FAILURE;
        
        
    


    /* Add ReaderGroup to the created PubSubConnection */
    retval |= addReaderGroup(server, "ReaderGroup1", &readerGroupIdent, topic, interval, ATLEASTONCE);
    if (retval != UA_STATUSCODE_GOOD){
        printf("Adding Reader Group failed.");
        return EXIT_FAILURE;
    }
    printf("readerGroupIdent: %d\n", readerGroupIdent.identifier);
    
    /* Add DataSetReader to the created ReaderGroup */
    retval |= addDataSetReader(server, readerGroupIdent, "DataSet Reader 1", "DataSet1", &subscribedDataSetIdent);
    if (retval != UA_STATUSCODE_GOOD){
        printf("Adding DataSet Reader failed.");
        return EXIT_FAILURE;
    }
    printf("subscribedDataSetIdent: %d\n", subscribedDataSetIdent.identifier);
    
    /* Add SubscribedVariables to the created DataSetReader */
    retval |= addSubscribedVariables(server, subscribedDataSetIdent, 40000);
    if (retval != UA_STATUSCODE_GOOD){
        printf("Adding Subscribed Variables failed.");
        return EXIT_FAILURE;
    }
    printf("subscribedDataSetIdent: %d\n", subscribedDataSetIdent.identifier);



    /* Add ReaderGroup to the created PubSubConnection */
    retval2 |= addReaderGroup(server, "ReaderGroup2", &readerGroupIdent2, topic2, interval2, BESTEFFORT);
    if (retval2 != UA_STATUSCODE_GOOD){
        printf("Adding Reader Group 2 failed.");
        exit(EXIT_FAILURE);
    }
    printf("readerGroupIdent2: %d\n", readerGroupIdent2.identifier);
        
    /* Add DataSetReader to the created ReaderGroup */
    retval2 |= addDataSetReader(server, readerGroupIdent2, "DataSet Reader 2", "DataSet2", &subscribedDataSetIdent2);
    if (retval2 != UA_STATUSCODE_GOOD){
        printf("Adding DataSet Reader 2 failed.");
        exit(EXIT_FAILURE);
    }
    printf("subscribedDataSetIdent2: %d\n", subscribedDataSetIdent2.identifier);

    /* Add SubscribedVariables to the created DataSetReader */
    retval2 |= addSubscribedVariables(server, subscribedDataSetIdent2,50000);
    if (retval2 != UA_STATUSCODE_GOOD){
        printf("Adding Subscribed Variables 2 failed.");
        exit(EXIT_FAILURE);
    }
    printf("subscribedDataSetIdent2: %d\n", subscribedDataSetIdent2.identifier);

    //retval2 = UA_Server_runUntilInterrupt(server);
    
    // ////// UNIX socket
    // Connect to the Unix socket server
    server_addr.sun_family = AF_UNIX;
    strcpy(server_addr.sun_path, unix_path);

    client_socket = socket(AF_UNIX, SOCK_STREAM, 0);
    if (client_socket == -1) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }
    
    connection_result = connect(client_socket, (struct sockaddr*)&server_addr, sizeof(server_addr));
    if (connection_result == -1) {
        perror("Socket connect failed");
        close(client_socket);
        exit(EXIT_FAILURE);
    }
    

    /////
    int i = 1;
    int interval_help = interval2;
    char* msg_exp_inv = "CAPIF invoker";
                printf(msg_exp_inv);
                ssize_t bytes_written = write(client_socket,msg_exp_inv,strlen(msg_exp_inv));
                if (bytes_written < 0){
                    printf("Unsuccessful message sending.");
                    printf(msg_exp_inv);
                }
    UA_Server_run_startup(server);


    cJSON *jobj;
    jobj = cJSON_CreateObject();
    int random = 0;
    int j = 1;
    // Main loop to read data from Unix server, publish to MQTT, and send to Unix socket
    while (i) {
        // Serve OPC UA requests 
        UA_Server_run_iterate(server,true);
        
        // Read data from server
        char buffer[1024];
        memset(buffer, 0, sizeof(buffer));

        ssize_t bytes_received = read(client_socket, buffer, strlen(buffer));
        if (bytes_received >= 0) {
            // Process received data from server
            char* c_pub_interval = "publishing_interval";
            char* msg ;//= "{\n\t\'publishing_interval\' : \""+itoa(interval_help)+"\"\n}";
            

            if (strstr(buffer,"CAPIF") != NULL) {
                printf(buffer);
                char* msg_exp_inv = "CAPIF invoker";
                printf(msg_exp_inv);
                ssize_t bytes_written = write(client_socket,msg_exp_inv,strlen(msg_exp_inv));
                if (bytes_written < 0){
                    printf("Unsuccessful message sending.");
                    printf("%s",msg_exp_inv);
                }
            }
            else if (strstr(buffer,c_pub_interval)!= NULL ) {
                printf(buffer);
                    // char* buffer = "{ \"publishing_interval\" : \"500\" }";
                    jobj = cJSON_CreateObject(); 
                    jobj = cJSON_Parse(buffer);
                    interval_help = atoi(cJSON_GetObjectItemCaseSensitive(jobj, "publishing_interval")->valuestring);
                    printf("New publishing interval: %d",interval_help);
                    cJSON_Delete(jobj);
                        
                    if (interval_help != interval) {
                    // The requested publishing interval is the same as the last requested value
                        snprintf(msg,"{\n\t\"origin\": \"OPCUA\",\n\t\"publishing_interval\": %d,\n\t\"success\": %d,\n\t\"reason\": \"Publishing interval has not been set yet, or is set incorrectly.\"\n}",interval_help, false);
                        printf(msg);
                        write(client_socket,msg,strlen(msg));
                    }                        
                    else if(interval_help > 50 && interval_help < 60000 && interval_help == interval){
                    // Successfull setting of publsihing interval
                        interval = interval_help;
                        snprintf(msg,"{\n\t\"origin\": \"OPCUA\",\n\t\"publishing_interval\": %d,\n\t\"success\": %d\n}",interval_help, true);
                        printf(msg);
                        write(client_socket,msg,strlen(msg));
                        // Could change subscriber interval looking for published data
                    }
                    else {
                    // The program should not step into this part, but just in case notify, if yes.
                        interval_help = interval;
                        snprintf(msg,"{\n\t\"origin\": \"OPCUA\",\n\t\"publishing_interval\": %d,\n\t\"success\": %d,\n\t\"reason\": \"Too small, or too big interval.\"\n}",interval_help, false);
                        printf(msg);
                        write(client_socket,msg,strlen(msg));
                    }
                
            }
            else {
                // One or some of the arguments were missing.
                snprintf(msg,"{\n\t\"origin\": \"OPCUA\",\n\t\"success\": %d,\n\t\"reason\": \"Missing argument publishing_interval.\"}", false);
                printf(msg);
                write(client_socket,msg,strlen(msg));
            }
            
        }
        if (i == 500){ //Simulate need in change of publishing interval
            if(j == 4){
                if (random > 200) {
                    random = 0;
                }
                char buffersend[1024];
                interval = 500 + random;
                random = random + 100;
                snprintf(buffersend, sizeof(buffersend), "{\n\t\"origin\": \"OPCUA\",\n\t\"change_publishing_interval\": %d\n}", interval);
                // Send data to server
                // clock_gettime(CLOCK_MONOTONIC_RAW, &start);
                // uint64_t delta = start.tv_sec * 1000000 + start.tv_nsec/1000;
                // printf("Starting request to change publishing interval: %d ms", delta);
                ssize_t bytes_sent = write(client_socket, buffersend, strlen(buffersend));
                if (bytes_sent <= 0) {
                    // Handle disconnect or error
                    printf("Error writing to Unix socket\n");
                    //break;
                }
                j = 1;
            }          
            i=1;
            j++;
        }
        else{
            i++;
        }
        // Sleep for a while (simulating periodic updates)
        sleep(0.005); //Subscribe interval cannot be lower then 10 ms. Enough to iterate every half that time.
    }

    UA_Server_run_shutdown(server);
    //UA_Server_runUntilInterrupt(server);
    UA_Server_delete(server);
    close(client_socket);
    unlink(unix_path);

    // UA_Server_delete(server);
    // return retval == UA_STATUSCODE_GOOD ? EXIT_SUCCESS : EXIT_FAILURE;
}
