import socket
import os
# Set the path for the Unix socket
socket_path = '/tmp/mininet_control.s'

# remove the socket file if it already exists
try:
    os.unlink(socket_path)
except OSError:
    if os.path.exists(socket_path):
        raise

# Create the Unix socket server
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Bind the socket to the path
server.bind(socket_path)

# Listen for incoming connections
server.listen(1)

# accept connections
print('Server is listening for incoming connections...')
connection, client_address = server.accept()

def read_unix():
        # receive data from the client
    while True:
        data, client_address = connection.recv(1024)
        if data:
            #TODO: search for command and respond
            command = data.decode().strip().split(" ")
            data = data.decode()
            print(data)

            if len(command) == 3:
                #Change bandwidth to suit subscription
                if command[1] == "bandwidth":
                    bw = int(command[2]) if command[1].isdigit() else None
                    if bw is not None:
                        print("{command[0]} {command[1]} {command[2]}")
                        connection.sendto(200, client_address)
                        #return "Setting bw to %d\n" % bw
                        print("Setting bw to %d\n" % bw)
                        

                #GroupManagement / Change Vlan
                elif command[1] == "vlan":
                    vlan = int(command[2]) if command[1].isdigit() else None
                    if bw is not None:
                        print("{command[0]} {command[1]} {command[2]}")
                        connection.sendto(200, client_address)
                        #return "Setting vlan to %d\n" % (vlan)
                        print("Setting vlan to %d\n" % (vlan))
                
                #Delay change because of distance
                elif command[1] == "delay":
                    delay = int(command[2]) if command[1].isdigit() else None
                    if bw is not None:
                        print("{command[0]} {command[1]} {command[2]}")
                        connection.send(200)
                        #return "Setting delay to %f\n" % delay
                        print("Setting delay to %f\n" % delay)
                           
                
                #Invalid/unsupported command
                else:
                    print()


            else:
                #Subscription BW change
                if ("change_bandwidth" in data) :
                    print("{data.links} bandwidth {data.change_bandwidth}")
                    # Send a response back to the client
                    response = 'Accepted'
                    connection.sendall(response.encode())

                #Group VLAN change
                elif ("change_vlan" in data):
                    print("{data.device} vlan {data.change_vlan}")
                    # Send a response back to the client
                    response = 'Accepted'
                    connection.sendall(response.encode())
                
                #User link delay change
                elif ("change_delay" in data):
                    print("{data.links} delay {data.change_delay}")
                    # Send a response back to the client
                    response = 'Accepted'
                    connection.sendall(response.encode())
                
                #Not recognized message
                else:
                    print("Command not recognized: {data}")
                    # Send a response back to the client
                    response = 'Denied'
                    connection.sendall(response.encode())
            



try:
    try:
        #print('Connection from', str(connection).split(", ")[0][-4:])
        read_unix()
    except KeyboardInterrupt:        
        # close the connection
        print("Closing Connection")
        connection.close()
        # remove the socket file
        os.unlink(socket_path)
    except :
        print("error trying to read message from client")
    
except KeyboardInterrupt:        
    # close the connection
    print("Closing Connection")
    connection.close()
    # remove the socket file
    os.unlink(socket_path)
