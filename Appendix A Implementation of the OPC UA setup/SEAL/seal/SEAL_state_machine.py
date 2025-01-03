from transitions import Machine
import random

from SEAL import SEAL

class SEAL_state_machine(object):

    # Define some states. Most of the time, narcoleptic superheroes are just like
    # everyone else. Except for...
    states = ['no_auth','no_group', 'group_created', 'connection_in_group']

    def __init__(self, name, seal, ros2_domain_id):

        # No anonymous superheroes on my watch! Every narcoleptic superhero gets
        # a name. Any name at all. SleepyMan. SlumberGirl. You get the idea.
        self.name = name
        self.seal = seal
        self.ros2_domain_id = ros2_domain_id

        # What have we accomplished today?
        #self.kittens_rescued = 0

        # Initialize the state machine
        self.machine = Machine(model=self, states=SEAL_state_machine.states, initial='no_auth')

        # # Add some transitions. We could also define these using a static list of
        # self.machine.add_transition(trigger='get_auth_token', source='no_auth', dest='no_group', conditions=['is_call_login'])
        # self.machine.add_transition(trigger='create_group', source='no_group', dest='group_created', conditions=['is_call_group_creation'])
        # self.machine.add_transition(trigger='add_connection_to_group', source='group_created', dest='connection_in_group', conditions=['is_call_AddDeviceAsMemberToDeviceGroup'])

        # self.machine.add_transition()

    def is_call_login(self):
        ok = 0
        ret = self.seal.Login()
        if (ret == 200):
            ok =1
        return ok

    def is_call_group_creation(self):
        ok = 0
        ret = self.seal.CreateDeviceGroup(self.ros2_domain_id)
        #print("RET, valGroupId:")
        #print(ret)
        #print(self.seal.valGroupId)
        if (ret == 200):
            ok =1
        return ok

    def is_call_AddDeviceAsMemberToDeviceGroup(self):
        ok = 0
        ret = self.seal.AddDeviceAsMemberToDeviceGroup()
        if (ret == 200):
            ok =1
        return ok
    
    def NewNetworkResourceAdaptation(self, QCI, uplinkMaxBitRate, downlinkMaxBitRate, dstIp, dstPort, srcIp,srcPort, protocol, direction):
        ok = 0
        ret = self.seal.NetworkResourceAdaptation(QCI, uplinkMaxBitRate, downlinkMaxBitRate, dstIp, dstPort, srcIp,srcPort, protocol, direction)

        if (ret == 200):
            ok = 1
        return ok
