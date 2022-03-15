import socket
import threading

# Connection Data
ip = '127.0.0.1'
port = 55555

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ip, port))
server.listen()

# array of client sockets
clients = []
host = -1

# Sending packets to all clients, excluding the player who initially sent the packet
def broadcast(message, exclude):
    for client in clients:
        if (client != exclude):
                client.send(message)


        # Handling Messages From Clients
def handle(client):
        while True:
                #print("//data received!//")
                try:
                        #print("//data received!//")
                        # Relay those messages!
                        message = client.recv(512) #No idea how to make this data size accurate. 512 should be good but no clue!
                        #print("Data is: "+str(message))
                        broadcast(message, client)
                except:
                        #print("//data failed!//")
                        # Something went horribly wrong! Disconnect the client.
                        index = clients.index(client)
                        clients.remove(client)
                        client.close()
                        break

# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        clients.append(client)

        if (host == -1):
                game_host = client
                print("New host is: "+str(client))

        # Print And Broadcast Nickname
        #broadcast("Someone joined!".encode('ascii'), client)

        # Pass the data off into a handling thread:
        print("Starting a thread...")
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

#Begin the server
receive()
