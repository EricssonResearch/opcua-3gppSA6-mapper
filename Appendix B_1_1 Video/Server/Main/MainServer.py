import socket
import time
import random

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('127.0.0.1', 5001)
server_socket.bind(server_address)

server_socket.listen(1)

resolutions = ["1920x1080x1EE", "1280x720x5EEE", "640x480x15EEE", "160x120x30EEE"]

while True:
    client_socket, client_address = server_socket.accept()

    while True:
        resolution = random.choice(resolutions)
        client_socket.sendall(resolution.encode())
        time.sleep(5)

        print(resolution)
        
    client_socket.close()
