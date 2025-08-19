# © Ericsson AB 2024 - All Rights Reserved. No part of this software may be reproduced in any form without the written permission of the copyright owner.
# Distribution error
# No
#
# Disclaimer
# Controlled by agreement
#
# Change clause
# Controlled by agreement

import socket
import sys
import os
import time
import select
from subprocess import call
import subprocess
import json

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf

import psutil

def find_leftover_processes():
    leftovers = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name']
            cmdline = ' '.join(proc.info['cmdline'])

            if 'Connexion.py' in cmdline or any(term in name for term in ['xterm', 'gnome-terminal', 'lxterminal']):
                print(f"Found leftover: PID={proc.pid}, Name={name}, Cmd={cmdline}")
                leftovers.append(proc)
            elif 'seal_user_NRM_tester.py' in cmdline or any(term in name for term in ['xterm', 'gnome-terminal', 'lxterminal']):
                print(f"Found leftover: PID={proc.pid}, Name={name}, Cmd={cmdline}")
                leftovers.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return leftovers


def kill_orphaned_connexion():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'python3' in proc.info['name'] and 'Connexion.py' in ' '.join(proc.info['cmdline']):
            print(f"Killing old Connexion server process: {proc.pid}")
            proc.kill()

def cleanup_zombies():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'python3' and proc.info['pid'] != os.getpid():
            print(f"Cleaning up orphaned process {proc.info['pid']}")
            proc.terminate()

def terminate_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.terminate()
        parent.terminate()
        gone, alive = psutil.wait_procs(children + [parent], timeout=5)
        for p in alive:
            p.kill()
    except psutil.NoSuchProcess:
        pass


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def default_limit_bw(eth2):
    # Filter for limited traffic
    return f"""sudo tc qdisc replace dev {eth2} root handle 1: htb default 10 
    \nsudo tc class add dev {eth2} parent 1: classid 1:10 htb rate 100mbit ceil 100mbit prio 4\n"""

def filter_limit_bw(tupple, bw, bw_ext, eth2, classid):
    # Filter for limited traffic
    return f"""sudo tc class add dev {eth2} parent 1: classid 1:{classid} htb rate {bw}{bw_ext} ceil {bw}{bw_ext} prio 1 
    sudo tc filter add dev {eth2} protocol ip parent 1: 
    flower ip_proto {tupple['protocol']} src_ip {tupple['srcIp']} dst_ip {tupple['dstIp']} src_port {tupple['srcPort']} dst_port {tupple['dstPort']}  
    action pass classid 1:{classid}\n"""
    #action pass classid 1:20\n"""

def change_filter_limit_bw(bw, bw_ext, eth2, classid):
    #mbit
    return f"""sudo tc class change dev {eth2} classid 1:{classid} htb rate {bw}{bw_ext} ceil {bw}{bw_ext}"""
    



# user must have sourced opt ros2 etc in .bashrc
def run_in_user_terminal(cmd):
    return '''sudo -Hu starcore DISPLAY=$DISPLAY x-terminal-emulator -ue bash -i -c "%s"''' % (cmd)


def run_in_terminal(pid, cmd):
    return '''dbus-launch x-terminal-emulator --maximise --layout=LAYOUT -e  bash -c "mnexec -a %d %s" ""''' % (pid, cmd)
    # return '''dbus-launch x-terminal-emulator --no-dbus --new-tab -e  bash -c "%s" ""''' % ( cmd)

def run_in_xterm_terminal(pid, cmd):
    return '''xterm -fa 'Mono' -fs 10 -bg white -fg black -e bash -c "mnexec -a %d %s, sleep 3" ""''' % (pid, cmd)
    

def rp_disable(host):
    ifaces = host.cmd('ls /proc/sys/net/ipv4/conf')
    ifacelist = ifaces.split()
    for iface in ifacelist:
       if iface != 'lo': host.cmd('sysctl net.ipv4.conf.' + iface + '.rp_filter=0')

class VLANHost( Host ):
    "Host connected to VLAN interface"

    # pylint: disable=arguments-differ
    def config( self, vlan=100, **params ):
        """Configure VLANHost according to (optional) parameters:
           vlan: VLAN ID for default interface"""

        r = super( VLANHost, self ).config( **params )

        ifaces = self.cmd('ls /proc/sys/net/ipv4/conf')
        ifacelist = ifaces.split()
        for iface in ifacelist:
            if iface != 'lo': self.popen(run_in_user_terminal('sysctl net.ipv4.conf.' + iface + '.rp_filter=0'))

        intf = self.defaultIntf()
        # remove IP from default, "physical" interface'Popen' object has no attribute 'split'
        self.cmd( 'ifconfig %s inet 0' % intf )
        # create VLAN interface
        self.cmd( 'vconfig add %s %d' % ( intf, vlan ) )
        # assign the host's IP to the VLAN interface
        self.cmd( 'ifconfig %s.%d inet %s' % ( intf, vlan, params['ip'] ) )
        # update the intf name and host's intf map
        newName = '%s.%d' % ( intf, vlan )
        # update the (Mininet) interface to refer to VLAN interface name
        intf.name = newName
        # add VLAN interface to host's name to intf map
        self.nameToIntf[ newName ] = intf

        return r

class LinuxRouter(Node):
    #Router as node with IP forwarding enabled.

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Enable forwarding on the router
        self.cmd('sysctl net.ipv4.ip_forward=1')
        # ifaces = self.cmd('ls /proc/sys/net/ipv4/conf')
        # ifacelist = ifaces.split()
        # for iface in ifacelist:
        #     if iface != 'lo': self.cmd('sysctl net.ipv4.conf.' + iface + '.rp_filter=0')

    def terminate(self):
        # Disable forwarding on the router
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


links = {}
class CustomTopo (Topo):
    def build(self, **_opts):
        ##>>Build the intended topology
            global links
            info( '*** Adding controller\n' )
            info( '*** Add node (router)\n' )
            info( '*** Add switches\n')
            #TODO: Add node as a router, which has IPv4 forwarding enabled (LinuxRouter)
            r1 = self.addNode('r1', cls=LinuxRouter, ip="10.1.1.1/24", mac="AA:00:00:00:00:00")
            #r2 = self.addHost('r2',cls=LinuxRouter, ip="10.1.0.1/24")
            
        ##Can add multiple switches for emulating hosts at multiple locations
        #TODO: Add switches and set stp to 1 for dynamic mapping
            s1 = self.addSwitch('s1',  cls=OVSKernelSwitch, failMode='standalone', stp=1) #ip='10.1.1.255/24',
            s2 = self.addSwitch('s2',  cls=OVSKernelSwitch, failMode='standalone', stp=1) #ip='10.1.2.255/24',
            s3 = self.addSwitch('s3',  cls=OVSKernelSwitch, failMode='standalone', stp=1) #ip='10.1.3.255/24',
            s4 = self.addSwitch('s4',  cls=OVSKernelSwitch, failMode='standalone', stp=1) #ip='10.1.4.255/24',

            
        #Adding hosts
        #TODO: Set default route for routing and parse IP, MAC and CLS of hosts
            info( '*** Add hosts\n')
            talker_host = self.addHost('publisher', cls=Host, ip='10.1.1.2/24', mac='BB:00:00:00:00:10' ,defaultRoute='via 10.1.1.1') #, vlan = 10
            cloud_listener_host = self.addHost('cloud_b', cls=Host, ip='10.1.2.2/24', mac='CC:00:00:00:00:20', defaultRoute='via 10.1.2.1' ) #, vlan = 20
            subscriber_host = self.addHost('subscriber', cls=Host, ip='10.1.3.2/24', mac='DD:00:00:00:00:30', defaultRoute='via 10.1.3.1' ) #, vlan = 30
            capif_host = self.addHost('capif', cls=Host, ip='10.1.4.2/24', mac='EE:00:00:00:00:040', defaultRoute='via 10.1.4.1' ) #, vlan = 40
            NR_server_sim_host = self.addHost('connexion', cls=Host, ip='10.1.2.50/24', mac='CC:00:00:00:00:50', defaultRoute='via 10.1.2.1' ) #, vlan = 50
            # local = self.addHost('local', cls=VLANHost, inNamespace=False) ## for mininet control

            info( '*** Add links\n')
        #QoS setting for tc-flow(s)
            #wifi_qos = {'bw':50,'delay':'20ms','loss':1,'max_queue_size':10,'jitter':'5'}
            wifi_qos = {'bw':50,'delay':'0ms','loss':0,'max_queue_size':10,'jitter':'0'}
            
            
        #TODO tc-flow
            links["L1"] = self.addLink(s1, r1, intfName='s1-eth0', intfName2='r1-eth1', cls=TCLink, **wifi_qos, params2={'ip' : '10.1.1.1/24'}) #Link between Router and Switch 1
            links["L2"] = self.addLink(s2, r1, intfName='s2-eth0', intfName2='r1-eth2', cls=TCLink, **wifi_qos, params2={'ip' : '10.1.2.1/24'}) #Link between Router and Switch 2
            links["L3"] = self.addLink(s3, r1, intfName='s3-eth0', intfName2='r1-eth3', cls=TCLink, **wifi_qos, params2={'ip' : '10.1.3.1/24'}) #Link between Router and Switch 3
            links["L4"] = self.addLink(s4, r1, intfName='s4-eth0', intfName2='r1-eth4', cls=TCLink, **wifi_qos, params2={'ip' : '10.1.4.1/24'}) #Link between Router and Switch 4
            links["L5"] = self.addLink(s1, talker_host, intfName='s1-eth1', intfName2='publisher-eth0', cls=TCLink , **wifi_qos) #OPC UA publisher
            links["L6"] = self.addLink(s2, cloud_listener_host, intfName='s2-eth1', intfName2='cloud-eth0', cls=TCLink , **wifi_qos) #Cloud MQTT broker
            links["L7"] = self.addLink(s3, subscriber_host, intfName='s3-eth1', intfName2='subscriber-eth0', cls=TCLink , **wifi_qos) #OPC UA subscriber
            links["L8"] = self.addLink(s4, capif_host, intfName='s4-eth1', intfName2='capif-eth0', cls=TCLink , **wifi_qos) #CAPIF
            links["L9"] = self.addLink(s2, NR_server_sim_host, intfName='s2-eth2', intfName2='connexion-eth0', cls=TCLink , **wifi_qos) #NR server simulation
        #Mininet autmatically links switches, no need to add links between them
            


            

requested_flowids = {}
def main():
    global links, requested_flowids
    #For default value
    wifi_qos = {'bw':50,'delay':'0ms','loss':0,'max_queue_size':10,'jitter':'0'}

    print("run this in a sudo -H bash")
    setLogLevel( 'info' )
    
    try:
        os.unlink("/tmp/mininet_control2.s")
    except FileNotFoundError:
        pass

# custtopo = CustomTopo()
    # net = Mininet( topo=custtopo,
    #                build=False,
    #                ipBase='10.0.0.0/8')
    net = Mininet( topo=None,
                    build=False,
                    ipBase='10.0.0.0/8')

##>>Build the intended topology
    global links
    info( '*** Adding controller\n' )
    info( '*** Add node (router)\n' )
    info( '*** Add switches\n')
    #TODO: Add node as a router, which has IPv4 forwarding enabled (LinuxRouter)
    r1 = net.addHost('r1', cls=LinuxRouter, ip="10.1.1.1/24", mac="AA:00:00:00:00:00")
        
##Can add multiple switches for emulating hosts at multiple locations
    #TODO: Add switches and set stp to 1 for dynamic mapping
    s1 = net.addSwitch('s1',  cls=OVSKernelSwitch, failMode='standalone', stp=1) #ip='10.1.1.255/24',
    s2 = net.addSwitch('s2',  cls=OVSKernelSwitch, failMode='standalone', stp=1) #ip='10.1.2.255/24',
    s3 = net.addSwitch('s3',  cls=OVSKernelSwitch, failMode='standalone', stp=1) #ip='10.1.3.255/24',
    s4 = net.addSwitch('s4',  cls=OVSKernelSwitch, failMode='standalone', stp=1) #ip='10.1.4.255/24',

        
#Adding hosts
    #TODO: Set default route for routing and parse IP, MAC and CLS of hosts
    info( '*** Add hosts\n')
    talker_host = net.addHost('publisher', cls=Host, ip='10.1.1.2/24', mac='BB:00:00:00:00:10' ,defaultRoute='via 10.1.1.1') #, vlan = 10
    cloud_listener_host = net.addHost('cloud_b', cls=Host, ip='10.1.2.2/24', mac='CC:00:00:00:00:20', defaultRoute='via 10.1.2.1' ) #, vlan = 20
    subscriber_host = net.addHost('subscriber', cls=Host, ip='10.1.3.2/24', mac='DD:00:00:00:00:30', defaultRoute='via 10.1.3.1' ) #, vlan = 30
    capif_host = net.addHost('capif', cls=Host, ip='10.1.4.2/24', mac='EE:00:00:00:00:040', defaultRoute='via 10.1.4.1' ) #, vlan = 40
    NR_server_sim_host = net.addHost('connexion', cls=Host, ip='10.1.2.50/24', mac='CC:00:00:00:00:50', defaultRoute='via 10.1.2.1' ) #, vlan = 50
    # local = self.addHost('local', cls=VLANHost, inNamespace=False) ## for mininet control

    info( '*** Add links\n')
#QoS setting for tc-flow(s)
    #wifi_qos = {'bw':50,'delay':'20ms','loss':1,'max_queue_size':10,'jitter':'5'}
    wifi_qos = {'bw':50,'delay':'0ms','loss':0,'max_queue_size':10,'jitter':'0'}
        
        
#TODO tc-flow
    links["L1"] = net.addLink(s1, r1, intfName='s1-eth1', intfName2='r1-eth1', cls=TCLink, **wifi_qos, params2={'ip' : '10.1.1.1/24'}) #Link between Router and Switch 1
    links["L2"] = net.addLink(s2, r1, intfName='s2-eth1', intfName2='r1-eth2', cls=TCLink, **wifi_qos, params2={'ip' : '10.1.2.1/24'}) #Link between Router and Switch 2
    links["L3"] = net.addLink(s3, r1, intfName='s3-eth1', intfName2='r1-eth3', cls=TCLink, **wifi_qos, params2={'ip' : '10.1.3.1/24'}) #Link between Router and Switch 3
    links["L4"] = net.addLink(s4, r1, intfName='s4-eth1', intfName2='r1-eth4', cls=TCLink, **wifi_qos, params2={'ip' : '10.1.4.1/24'}) #Link between Router and Switch 4
    links["L5"] = net.addLink(s1, talker_host, intfName='s1-eth2', intfName2='publisher-eth0', cls=TCLink , **wifi_qos) #OPC UA publisher
    links["L6"] = net.addLink(s2, cloud_listener_host, intfName='s2-eth2', intfName2='cloud-eth0', cls=TCLink , **wifi_qos) #Cloud MQTT broker
    links["L7"] = net.addLink(s3, subscriber_host, intfName='s3-eth2', intfName2='subscriber-eth0', cls=TCLink , **wifi_qos) #OPC UA subscriber
    links["L8"] = net.addLink(s4, capif_host, intfName='s4-eth2', intfName2='capif-eth0', cls=TCLink , **wifi_qos) #CAPIF
    links["L9"] = net.addLink(s2, NR_server_sim_host, intfName='s2-eth3', intfName2='connexion-eth0', cls=TCLink , **wifi_qos) #NR server simulation
    #Mininet autmatically links switches, no need to add links between them
    print(links)
    
    #Default network TC-link characteristics for all links
    wifi_qos = {'bw':50,'delay':'0ms','loss':0,'max_queue_size':10,'jitter':'0'}                      

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    # for controller in net.controllers:
    #     controller.start()

    # i=1
    # for link in net.links:
    #     links[f"L{i}"] = link 
    #     i+=1
    # print(links)
    for a in links.keys():
        print(f"{a} : {links[a]}")
        # print(f"{a} : {links[a].intf1} <-> {links[a].intf2}")
    time.sleep(5)


    info( '*** Starting switches\n')
    net.start()
    info( '*** Routing Table on Router:\n' )
    info( net[ 'r1' ].cmd( 'route' ) )
    
#TODO RP filter disable, so that routing required messages are not dropped even when a route is not found (says no route, when it found one)
    rp_disable(net['r1'])
#
    
    # avoid any setup delay by performing an all-pairs ping
    time.sleep(3)
    print("---------------------")
    net.pingAll(5)
    #net.pingAll(10)
    #Host ping routers
    # net.ping([net['publisher'],net['s1']])
    net.ping([net['publisher'],net['r1']])

    #Hosts pinging eachother
    net.ping([net['publisher'],net['cloud_b']])
    net.ping([net['publisher'],net['subscriber']])
    net.ping([net['cloud_b'],net['subscriber']])
    net.ping([net['publisher'],net['capif']])
    # net['publisher'].cmdPrint('ping -c 4 127.0.0.1:3306')

    info( '*** Post configure switches and hosts\n')
# #TODO: Change talker and listener cmd to OPC UA, also set up other hosts
                              #systemctl start mysqld
    NR_server_database_cmd = "sudo mysql\n\nDROP USER 'admin'@'10.123.123.2';\nflush privileges;\nCREATE USER 'admin'@'10.123.123.2'IDENTIFIED WITH mysql_native_password BY 'Admin1Pass';\nGRANT ALL PRIVILEGES ON *.* TO 'admin'@'10.123.123.2';\nexit\n"
    NR_server_sim_cmd = 'python3 ../../A_7\ 3GPP\ NRM\ emulation/connexion/Connexion.py'
# #For testing
    seal_user = 'python3 ../../SEAL/seal/seal_user_NRM_tester.py'
    # mininet_controll = "python3 ../../A_7\ 3GPP\ NRM\ emulation/connexion/mininet_unix_server_sim2.py"


    print('\n\n*****\n')
# #Set up virtual interface to connect to the local machine for using MySQL
    NR_server_sim_host = net.get('connexion')
    info('*** Cleaning stale veth interfaces if any\n')
    os.system('ip link delete veth-host 2>/dev/null || true')
    os.system('ip link delete veth-nrm 2>/dev/null || true')
    
    info('*** Creating veth pair between host and NRM - Connexion\n')
    os.system('ip link add veth-host type veth peer name veth-nrm')
    os.system(f'ip link set veth-nrm netns {NR_server_sim_host.pid}')
    os.system('ip addr add 10.123.123.1/24 dev veth-host')
    os.system('ip link set veth-host up')
    os.system("sudo ufw allow from 10.123.123.0/24 to any port 3306")
    os.system(f"mount --bind /tmp/ /tmp/") #/tmp/mininet_control.s
    os.system(f"nsenter -t {NR_server_sim_host.pid} -m mount --bind /tmp/ /tmp/")
    time.sleep(2)

    NR_server_sim_host.cmdPrint('ip addr add 10.123.123.2/24 dev veth-nrm')
    NR_server_sim_host.cmdPrint('ip link set veth-nrm up')
    NR_server_sim_host.cmdPrint('ip route add default via 10.123.123.1')

    time.sleep(2)
    # For debugging connectivity issues with connecting to local machine MySQL
    # net['connexion'].cmdPrint('ping -c 4 10.123.123.1')
    # net['connexion'].cmdPrint('ping -c 4 10.123.123.2')
    # net['connexion'].cmdPrint('ip a | grep veth')
    # os.system('ip a | grep veth-host')


    



    info("\nStarting '%s'\n"%NR_server_sim_cmd)
#TODO: Start NRM server simulation
    # net['connexion'].cmdPrint("sudo lsns -t net")
    database = net['connexion'].cmdPrint("sudo DEBIAN_FRONTEND=noninteractive apt install -y mysql-server\n")
    database = net['connexion'].cmdPrint(NR_server_database_cmd)#, shell=True)
    database = net['connexion'].cmdPrint("sudo mysql\nSELECT HOST,USER,plugin FROM mysql. user;\nexit\n")#, shell=True)
    # net['connexion'].cmdPrint("sudo systemctl status mysql")
    
    time.sleep(2)
    sock = start_unix_socket()



  #TODO: Start NRM server simulation
    # nrm_server_sim_process = net['connexion'].popen(NR_server_sim_cmd, shell=True, stdout=open('/tmp/connexion_stdout.log', 'w'),stderr=open('/tmp/connexion_stderr.log', 'w'))    
    # nrm_server_sim_process = net['connexion'].popen(run_in_xterm_terminal(net['connexion'].pid, NR_server_sim_cmd), shell=True, stdout=open('/tmp/connexion_stdout.log', 'w'),stderr=open('/tmp/connexion_stderr.log', 'w'))
    nrm_server_sim_process = net['connexion'].popen(run_in_terminal(net['connexion'].pid, NR_server_sim_cmd), shell=True, stdout=open('/tmp/connexion_stdout.log', 'w'),stderr=open('/tmp/connexion_stderr.log', 'w'))
    # nrm_server_sim_process = net['connexion'].cmdPrint(NR_server_sim_cmd)
    net['connexion'].cmdPrint("sudo ss -tuln")
    net['connexion'].cmdPrint("sudo cat /proc/net/tcp")
    


#     info("Starting '%s'\n"%mininet_controll)
# #TODO: Start mininet controller (communicates with NRM on UNIX socket)
#     mininet_controll_process = net['connexion'].popen(run_in_user_terminal(mininet_controll), shell=True)

    #outs, errs = controller_process.communicate()
    #print(outs)
    #print(errs)
    
    print("Starting Mininet controll socket")
    # sock = start_unix_socket()
    poller = select.poll()
    #h1 = net['C1']  # so we can call class method fdToNode
    net['cloud_b'].cmdPrint("ping -c 4 10.1.2.50")
    time.sleep(10)
    net['connexion'].cmdPrint('netstat -an | grep LISTEN')


    net['cloud_b'].cmdPrint("curl http://10.1.2.50:7777")



    info("Starting '%s'\n"%seal_user)
    # seal_user_process = net['cloud_b'].popen(seal_user, shell=True, stderr=open('/tmp/seal_stderr.log', 'w'))
    # seal_user_process = net['cloud_b'].popen(run_in_xterm_terminal(net['subscriber'].pid,seal_user), shell=True, stderr=open('/tmp/seal_stderr.log', 'w'))
    seal_user_process = net['subscriber'].popen(run_in_terminal(net['subscriber'].pid,seal_user), shell=True, stderr=open('/tmp/seal_stderr.log', 'w'))
    # net['cloud_b'].cmdPrint(seal_user)
    

    #event_mask = select.POLLIN | select.POLLPRI | select.POLLOUT | select.POLLERR | select.POLLHUP
    event_mask = select.POLLIN | select.POLLHUP
    poller.register(seal_user_process.stdout, event_mask)
    poller.register(sock, select.POLLIN)

    
    print("Started listening\n")
    
    classid = 20
    try:
        print("Start polling from socket...\n")
        while True:
            data, address = next(monitor_poll(poller, sock, seal_user_process.stdout))
            #data, address = next(monitor_poll2(poller, sock))
            if data is None:
                i = 1
                print("exited, we are exiting as well\n")
                break
            
            else:
                print(data)
                try:
                    data = json.loads(data.decode('utf-8'))
                    command = data['command'].strip().split(" ")
                    command.append('extended')
                except:
                    command = data.decode('utf-8').strip().split(" ")
                print(command)
                if len(command) == 3 or len(command) == 4:

                    #Change bandwidth to suit subscription
                    if command[1] == "bandwidth":
                        bw = int(command[2]) if command[2].isdigit() else None
                        if bw is None:
                            bw = float(command[2]) if isfloat(command[2]) else None

                        #Set tc-flow or link bandwidth
                        if bw is not None and command[0] in links.keys():
                            custom_wifi_qos = dict(wifi_qos)
                            if len(command) == 4:
                                if data['min_con'] == command[1]:
                                    custom_wifi_qos['bw'] = round(float(data['bw']), 4)
                                    print(sock,address, "Setting bw to %f\n" % (custom_wifi_qos['bw']))

                                    #TODO: check if there is tc-filter on host machine, create or update tc filter and bw setting
                                    for link in net.links:
                                        for intf in [link.intf1, link.intf2]:
                                            
                                            #Is this link the interface with the right IP
                                            if intf.node.IP(intf=intf) == data['flowID']['srcIp']:
                                                print(f"{intf.node.name}:{intf.name} -> {intf.node.IP(intf=intf)}")
                                                #Was a tc-flow filter created previously?
                                                
                                                #Is the source machine of 5tuple in the the registered tc-flow machines
                                                if intf.node.name not in requested_flowids.keys():
                                                    #No. Add it and let it store multiple flows
                                                    requested_flowids[intf.node.name] = []
                                                
                                                #Because of classid this is the new check if flowID/5tuple TC-flow exist
                                                flowIDinrequested_flowids = False
                                                for tc in requested_flowids[intf.node.name]:
                                                    if tc['srcIp'] == data['flowID']['srcIp'] and tc['dstIp'] == data['flowID']['dstIp']:
                                                            if tc['srcPort'] == data['flowID']['srcPort'] and tc['dstPort'] == data['flowID']['dstPort']:
                                                                    if tc['protocol'] == data['flowID']['protocol']:
                                                                        flowIDinrequested_flowids = True
                                                                        
                                                #Does the 5tuple TC-flow exist, if no: create, if yes: update setting
                                                if flowIDinrequested_flowids == False:
                                                # if data['flowID'] not in requested_flowids[intf.node.name]:

                                                    #Default settings was set? 
                                                    tc_in_host = False
                                                    for tc in requested_flowids[intf.node.name]:
                                                        if tc['srcIp'] == data['flowID']['srcIp']:
                                                            tc_in_host = True
                                                            break
                                                    #If not, then set
                                                    if tc_in_host == False:
                                                        create_tc_filter_def = default_limit_bw(intf.name)                                                        
                                                        print('Create tc-flow filter')
                                                        # print(create_tc_filter_def)
                                                        net[intf.node.name].cmdPrint(create_tc_filter_def)

                                                    #Otherwise it is new 5-tuple request with existing default/fallback tc class                                                     
                                                    #Create bw setting on filter with 5-tuple/flowid
                                                    data['flowID']['classid'] = classid
                                                    res = filter_limit_bw(data['flowID'], data['bw'], data['bw_type'], intf.name, classid)
                                                    classid += 10
                                                    requested_flowids[intf.node.name].append(data['flowID'])
                                                else:
                                                    #Change the bw setting on existing filter
                                                    classid_tmp = None
                                                    for tc in requested_flowids[intf.node.name]:
                                                        if tc['srcIp'] == data['flowID']['srcIp'] and tc['dstIp'] == data['flowID']['dstIp']:
                                                            if tc['srcPort'] == data['flowID']['srcPort'] and tc['dstPort'] == data['flowID']['dstPort']:
                                                                    if tc['protocol'] == data['flowID']['protocol']:
                                                                        classid_tmp = tc['classid']
                                                                        
                                                    #Ther was an issue when filter for this tc-flow was first created or corrupted data
                                                    if classid_tmp == None:
                                                        print("Classid wasn't saved for certain user")
                                                        print(data['flowID'])
                                                    res = change_filter_limit_bw(data['bw'], data['bw_type'], intf.name, classid_tmp)

                                                #Now tc-flow default exists, create new filter or update
                                                print("\n")
                                                net[intf.node.name].cmdPrint(res)
                                                print("\n")
                                                break

                                    #Exited for cycle with break
                                    respond(sock,address, "Setting bw to %d\n" % (round(float(data['bw']), 4)))
                                    
                                else: 
                                    respond(sock,address, "<Incosistent request>\n")

                            else:
                                custom_wifi_qos['bw'] = int(bw)
                                #Set channel settings for both ends
                                links[command[0]].intf1.config(**custom_wifi_qos)
                                links[command[0]].intf2.config(**custom_wifi_qos)
                                print(sock,address, "Setting bw to %d\n" % (custom_wifi_qos['bw']))
                                respond(sock,address, "Setting bw to %d\n" % (custom_wifi_qos['bw']))
                                print(custom_wifi_qos)

                        else:
                            respond(sock,address, "<Link (%s)> <bandwidth>\n" % (",".join(links.keys())))




                    #GroupManagement / Change Vlan
                    elif command[1] == "vlan":
                        vlan = int(command[2]) if command[2].isdigit() else None
                        if vlan is not None and command[0] in links.keys():
                            # custom_wifi_qos = dict(wifi_qos)
                            # set VLAN of of VLANHOST
                            print(vlan)
                            print(sock,address, "Setting vlan to %d\n" % (vlan))
                            # links[command[0]].intf1.config(vlan=vlan)
                            # links[command[0]].intf2.config(vlan=vlan)
                            # links[command[0]].intf1.config(**custom_wifi_qos)
                            # links[command[0]].intf2.config(**custom_wifi_qos)
                            respond(sock,address, "Setting vlan to %d\n" % (vlan))
                        else:
                            respond(sock,address, "<User (%s)> <vlan>\n" % (",".join(links.keys())))
                    
                    
                    #Delay change because of distance
                    if command[1] == "delay":
                        #Check if delay is a number (float/int)
                        delay = int(command[2]) if command[2].isdigit() else None
                        if delay is None:
                            delay = float(command[2]) if isfloat(command[2]) else None

                        if delay is not None and command[0] in links.keys():
                            custom_wifi_qos = dict(wifi_qos)
                            # custom_wifi_qos['delay'] = str(delay) + " ms"
                            try:
                                custom_wifi_qos['delay'] = str(f"{round(float(delay), 3)}{data['delay_ext']}" )
                            except:
                                custom_wifi_qos['delay'] = str(f"{int(delay)}{data['delay_ext']}" )
                            
                            print(custom_wifi_qos)
                            print(sock,address, "Setting delay to %f\n%s\n" % (delay, custom_wifi_qos['delay']))
                            
                            print(command[0])
                            print(links[command[0]])
                            links[command[0]].intf1.config(delay=custom_wifi_qos['delay'])
                            links[command[0]].intf2.config(delay=custom_wifi_qos['delay'])
                            # links[command[0]].intf1.config(**custom_wifi_qos)
                            # links[command[0]].intf2.config(**custom_wifi_qos)
                            # links[command[0]].config(delay = custom_wifi_qos['delay'])
                            print("Setting delay to %f (%s)" % (delay,custom_wifi_qos['delay']))
                            respond(sock,address, "Setting delay to %f (%s)" % (delay,custom_wifi_qos['delay']))
                            
                        else:
                            respond(sock,address, "<Link (%s)> <bandwidth>\n" % (",".join(links.keys())))
                    
                
                    
    except KeyboardInterrupt:
        print("Exiting becausese of Ctrl-C...\n")

        terminate_process_tree(seal_user_process.pid)
        time.sleep(3)
        terminate_process_tree(nrm_server_sim_process.pid)
        time.sleep(3)
        try:
            seal_user_process.terminate()
            seal_user_process.wait(timeout=5)
        except seal_user_process.TimeoutExpired:
            print(f"{seal_user_process} didn’t terminate in time, trying again...")
            try:
                seal_user_process.wait(timeout=5)
            except seal_user_process.TimeoutExpired:
                print(f"{seal_user_process} didn’t terminate in time. Killing...")
                seal_user_process.kill()
        try:
            nrm_server_sim_process.terminate()
            nrm_server_sim_process.wait(timeout=5)
        except nrm_server_sim_process.TimeoutExpired:
            print(f"{nrm_server_sim_process} didn’t terminate in time. Killing...")
            try:
                nrm_server_sim_process.wait(timeout=5)
            except nrm_server_sim_process.TimeoutExpired:
                print(f"{nrm_server_sim_process} didn’t terminate in time. Killing...")
                nrm_server_sim_process.kill()  
        
        if os.path.exists("/tmp/mininet_control.s"):
          os.remove("/tmp/mininet_control.s")  
        

    
    finally:
        
        print("Terminating seal_user_process")
        terminate_process_tree(seal_user_process.pid)
        time.sleep(3)
        print("Terminating nrm_server_sim_process")
        terminate_process_tree(nrm_server_sim_process.pid)
        time.sleep(3)

        try:
            seal_user_process.terminate()
            seal_user_process.wait(timeout=5)
        except seal_user_process.TimeoutExpired:
            print(f"{seal_user_process} didn’t terminate in time, trying again...")
            try:
                seal_user_process.wait(timeout=5)
            except seal_user_process.TimeoutExpired:
                print(f"{seal_user_process} didn’t terminate in time. Killing...")
                seal_user_process.kill()
        time.sleep(3)
        try:
            nrm_server_sim_process.terminate()
            nrm_server_sim_process.wait(timeout=5)
        except nrm_server_sim_process.TimeoutExpired:
            print(f"{nrm_server_sim_process} didn’t terminate in time. Killing...")
            try:
                nrm_server_sim_process.wait(timeout=5)
            except nrm_server_sim_process.TimeoutExpired:
                print(f"{nrm_server_sim_process} didn’t terminate in time. Killing...")
                nrm_server_sim_process.kill()

        print("Closing socket...\n")
        time.sleep(3)
        sock.close()
        info('*** Cleaning stale veth interfaces if any\n')
        os.system('ip link delete veth-host 2>/dev/null || true')
        os.system('ip link delete veth-nrm 2>/dev/null || true')
        if os.path.exists("/tmp/mininet_control.s"):
            os.remove("/tmp/mininet_control.s") 
        #Terminate mininet controller socket and processess
  
        time.sleep(2)
        #Close hosts
        net['subscriber'].terminate()
        net['publisher'].terminate()
        net['cloud_b'].terminate()
        net['capif'].terminate()
        net['connexion'].terminate()

        print("Stopping Mininet...\n")
        net.stop()
        #Stop any lingering x-terminal-emulators
        os.system("pkill x-terminal-emulator")

        #At the end stop every orphaned process
        time.sleep(2)
        cleanup_zombies()
        kill_orphaned_connexion()
        time.sleep(2)
        # leftover = find_leftover_processes()
        # if len(leftover) > 0:
        #     print("Leftover processes:")
        #     for proc in leftover:
        #         print(f"PID: {proc.pid}, Name: {proc.name()}, Cmdline: {proc.cmdline()}")
        #         proc.kill()
        # else:
        #     print("No leftover processes found.")
        print(find_leftover_processes())

##### End of main()
    
    



def start_unix_socket():
    addr = "/tmp/mininet_control2.s"
    if os.path.exists(addr):
      os.remove(addr)    

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    sock.bind(addr)
    os.chmod(addr, 0o777)
    return sock
    
def monitor_poll(poller, sock, stdout): # we need sock and stdout, sock is the input commands from mininet_control, stdin is the output of Turlesim, but because now we are running 2 processes in Turtlesim its only for SIGHUP 
    while True:
        ready = poller.poll( 50 )

        for fd, event in ready:
            if event & select.POLLHUP and fd == stdout.fileno():
                yield None, None
            if event & select.POLLIN:
                if fd == stdout.fileno():
                    # line = stdout.readline()
                    # if not line:
                    #     pass
                    # print(line) #this is the output of the terminal emulator
                    pass
                    
                else: # we got data from the socket
                    if sock.fileno() == fd:
                        data, address = sock.recvfrom(4096)
                        # print(data,address)
                        yield data, address

                        
def respond(sock, addr, s):
    if addr:
        sock.sendto(s.encode(), addr)

if __name__ == '__main__':
    setLogLevel( 'info' )
    main()
