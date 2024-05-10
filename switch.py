import socket
import select

HOST = '127.0.0.1'  
PORT = 65432        


switch_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
switch_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
switch_socket.bind((HOST, PORT))
switch_socket.listen()

sockets_list = [switch_socket]
clients = {}

def receive_message(client_socket):
    try:
        message = client_socket.recv(1024)
        if not message:
            return False
        return {'data': message}
    except:
        return False

print("Switch is running and listening for connections...")

try:
    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

        for notified_socket in read_sockets:
            if notified_socket == switch_socket:
                client_socket, client_address = switch_socket.accept()
                sockets_list.append(client_socket)
                clients[client_socket] = client_address
                print(f"Accepted new connection from {client_address[0]}:{client_address[1]}")
            else:
                message = receive_message(notified_socket)
                if message is False:
                    print(f"Closed connection from {clients[notified_socket]}")
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    continue

                user = clients[notified_socket]
                print(f"Received message from {user}: {message['data'].decode()}")

                for client_socket in clients:
                    if client_socket != notified_socket:
                        client_socket.send(message['data'])

except KeyboardInterrupt:
    print("Switch shutdown.")
    switch_socket.close()
