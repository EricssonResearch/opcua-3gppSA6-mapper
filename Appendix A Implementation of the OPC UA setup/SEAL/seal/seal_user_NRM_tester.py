from mimetypes import init
from operator import ne
import time

from QoS_mapper import QoSmapper

from SEAL import SEAL
from SEAL_state_machine import SEAL_state_machine



networkexposure = SEAL()
#url_SEAL = 'http://172.16.7.10:5500'
active_topics = {}
domain_id = 0
seal_sm = None
broker= "127.0.0.1"#"10.1.1.2"
port1=8883

destinationIPv4= "10.1.3.2"
destinationPort= 6464
sourceIPv4 = "10.1.1.2"
sourcePort = 6565
protocol = "TCP"
protocol2 = "UDP"


class qos_profil:
    reliability = 0
    lifespan_miliseconds = 0
    duration_miliseconds = 0
    liveliness = 0
    lease_duration_nanoseconds = 0 *1000



class Ros2QoS_parser:
    def __init__(self, qos = 3):
        self.qos_profile = qos_profil
        if qos <= 0 or qos > 2:
            self.qos_profile.reliability = 0
        else:
            self.qos_profile.reliability = qos
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








def main(args=None):
    seal_sm = SEAL_state_machine("seal", networkexposure, domain_id)
    global destinationIPv4, destinationPort, sourceIPv4, sourcePort


    srcaddress = sourceIPv4
    srcport = sourcePort
    dstaddress = destinationIPv4
    dstport = destinationPort
    current_rate = 600
    current_bw = 10000
    window_rate = 500
    qos = 1
    grpDesc = "groupd_dest_example"


    print("reliability: " + str(qos))
    ros2qos_parser = Ros2QoS_parser(qos)
    qos_profile2 = ros2qos_parser.get_qos(qos)
    PDB_Ros2, PELR_Ros2 = ros2qos_parser.parseQoS(qos_profile2,current_rate)
    #PDB_Ros2, PELR_Ros2 = 0 ,0 #retRos2QoS


    PDB_measured = 1. / current_rate * 10e3
    print("PDB_measured: "+ str(PDB_measured))
    if PDB_measured > PDB_Ros2:
        print("WARNING: ROS2 lifespan/MQTT keepalive setting is too low")
    # ezt az erteket ki kellene talalni

    if abs(current_rate/window_rate-1) < 0.1:
        RT = "GBR"
    else:
        RT = "Non-GBR"
    print("RT: "+ RT)

    DRAW = 2000




        
    print("PDB_Ros2: "+ str(PDB_Ros2))
    print("PELR_Ros2: "+ str(PELR_Ros2))
    #print(*pub_info, sep = "| *** |")
    qos_mapper = QoSmapper()
    RT = None
    PL = 2
    #PDB = 80

    qos_mapper_result = qos_mapper.getQCI(RT, PL, PDB_measured, PELR_Ros2, current_bw, DRAW)

    qci, example_service = qos_mapper_result
    if qci is None:
        qci = -1
    if example_service is None:
        example_service = "no proper service found"
    print("QCI:" + str(qci))
    print("Example service: " + example_service)

    #----------------------------------------------------------
    #networkexposure.CreateDeviceGroup("GROUP_ID")
    #networkexposure.AddDeviceAsMemberToDeviceGroup("GROUP_ID")
    #----------------------------------------------------------

    # print("\n\nGET LocationAreaInfo")
    # networkexposure.LocationAreaInfoRetrieval()

    #Create a unicast subscription --> sets bandwidth and delay (first location is close to enodeB 0, minimal delay)
    #Delay is calculated based on physical distance from enodeB 0
    print("\n\nCreate (POST) Unicast-subscription -- First request: if no server on port retry every 10 seconds")
    networkexposure.NetworkResourceAdaptation( qci, "1000 KB/s", "100 KB/s", destinationIPv4, destinationPort, sourceIPv4, sourcePort, protocol, "bidirectional")
    print("\n\nGET Unicast-subscription")
    networkexposure.NetworkResourceAdaptationGET()

    time.sleep(5)
    #Create group for users of a service or services --> sets VLAN setting for devices in group
    print("\n\nCreate (POST) Group")
    networkexposure.CreateDeviceGroup(grpDesc)
    time.sleep(5)
    print("\n\nGET Groups with val-service-id and val-group-id")
    networkexposure.RetriveDeviceGroups(grpDesc)


    time.sleep(5)
    #Create Location reporting configuration --> Set location to enodeB 1
    print("\n\nCreate (POST) LocationReporting")
    networkexposure.CreateLocReportingConfig()
    time.sleep(5)
    print("\n\nGET LocationReporting")
    networkexposure.RetrieveLocReportingConfig()


    # print("\n\nGET LocationAreaInfo")
    # networkexposure.LocationAreaInfoRetrieval()

    # print("\n\nGET LocationAreaInfo")
    # networkexposure.LocationAreaInfoRetrieval()

    time.sleep(5)
    #Change settings --> Changes delay for valuser (server randomly assigns enodeB location to UE)
    print("\n\nUPDATE (PUT) LocationReporting")
    networkexposure.UpdateLocReportingConfig()

    # print("\n\nGET LocationAreaInfo")
    # networkexposure.LocationAreaInfoRetrieval(loc_type="enodeB", loc="4847")

    time.sleep(5)
    print("\n\nModify (PATCH) LocationReporting")
    networkexposure.ModifyLocReportingConfig()

    # print("\n\nGET LocationAreaInfo")
    # networkexposure.LocationAreaInfoRetrieval(loc_type="enodeB", loc="4847")

    #Update device group setting, this will change VLAN of UE
    print("\n\nGET Group")
    networkexposure.GetDeviceGroup()
    time.sleep(5)
    print("\n\nUPDATE (PUT) Group")
    networkexposure.UpdateDeviceGroup(grpDesc)
    time.sleep(5)
    print("\n\nModify (PATCH) Group")
    networkexposure.ModifyDeviceGroup(grpDesc)

    # print("\n\nGET LocationAreaInfo")
    # networkexposure.LocationAreaInfoRetrieval(loc_type="enodeB", loc="4847")

    time.sleep(5)
    #Update unicast subscription --> changes bandwidth and delay (automaticly generates new location as if received new location report)
    print("\n\nUpdate (POST) Unicast-subscription")
    networkexposure.NetworkResourceAdaptation( qci, "666 KB/s", "512 KB/s", destinationIPv4, destinationPort, sourceIPv4, sourcePort, protocol, "bidirectional", True)
    
    time.sleep(5)
    #Create a multicast subscription (geo loc included) --> sets bw and delay
    print("\n\nCreate (POST) Multicast-subscription")
    networkexposure.NetworkResourceAdaptationMulti( qci, "6000 KB/s", "100 KB/s", destinationIPv4, destinationPort, sourceIPv4, sourcePort, protocol, "bidirectional")
    print("\n\nGET Multicast-subscription")
    networkexposure.NetworkResourceAdaptationMultiGET()
    
    time.sleep(5)
    #Update multisubs settings --> Can contain new location --> sets new delay
    print("\n\nUpdate (POST) Multicast-subscription")
    networkexposure.NetworkResourceAdaptationMulti( qci, "999 KB/s", "1000 KB/s", destinationIPv4, destinationPort, sourceIPv4, sourcePort, protocol2, "bidirectional", True)
    time.sleep(5)

    # print("\n\nGET LocationAreaInfo")
    # networkexposure.LocationAreaInfoRetrieval(loc_type="enodeB", loc="4847")

    #Update unicast subscription --> changes bandwidth and delay (automaticly generates new location as if received new location report)
    print("\n\nUpdate (POST) Unicast-subscription")
    networkexposure.NetworkResourceAdaptation( qci, "5.02 MB/s", "500 KB/s", destinationIPv4, destinationPort, sourceIPv4, sourcePort, protocol2, "bidirectional", True)
    
    time.sleep(5)


    




try:
    if __name__ == '__main__':
        main()
        time.sleep(10)
        print("\n\nDELETE Group")
        networkexposure.DeleteDeviceGroup()
        print("\n\nDELETE Unicast-subscription")
        networkexposure.NetworkResourceAdaptationDELETE()
        print("\n\nDELETE Multicast-subscription")
        networkexposure.NetworkResourceAdaptationMultiDELETE()
        print("\n\nDELETE  LocationReporting")
        networkexposure.DeleteLocReportingConfig()
        print("Exiting")

#User initiated shutdown with keyboard interrupt
except KeyboardInterrupt:
    #Delete created subscriptions, groups and location reporting services
    print("\n\nDELETE Group")
    networkexposure.DeleteDeviceGroup()
    print("\n\nDELETE Unicast-subscription")
    networkexposure.NetworkResourceAdaptationDELETE()
    print("\n\nDELETE Multicast-subscription")
    networkexposure.NetworkResourceAdaptationMultiDELETE()
    print("\n\nDELETE  LocationReporting")
    networkexposure.DeleteLocReportingConfig()

    print("CTRL-C: Exiting")
    time.sleep(2)
