import socket
import threading
import json
import Stroid_Raider_Lobby

# Connection Data
ip = '127.0.0.1'
port = 55555

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ip, port))
server.listen()

test = """{ "cmd": "lobby_info", "id": 0.0 }"""
print(test)
print(len(test))
test = json.loads(test)
print("Decode Test: "+str(test["id"]))

# List of lobbies
lobbies = []
next_id = 1000 #next id to be given to a new lobby

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

        #Add the client to the correct lobby

        
        lobby_packet = client.recv(512)
        print(lobby_packet)
        print("UTF-8 Decode:")
        print(lobby_packets)
        lobby_packet = lobby_packet.decode('utf-8') #Prepare the information to be handled by the json decoder
        lobby_packet = lobby_packet.strip(lobby_packet[-1])
        print(lobby_packet)
        print(len(lobby_packet))
        lobby_info = json.loads(lobby_packet)

        _success = False

        if (lobby_info["cmd"] == "lobby_info"):
            lobby_id = lobby_info["id"]

            #- Look for an existing lobby to add the client into
            for lobby in lobbies:
                if (lobby.getId() == lobby_id):
                    lobby.addClient(client)
                    _success = True
                    break

            #- If a lobby doesn't exist, make one and add the client to that.
        if (_success == False & isinstance(lobby_id,int)):
            temp_lobby = Lobby(next_id)
            print("Lobby created: "+next_id)
            next_id += 1

            temp_lobby.addClient(client)
            lobbies.append(temp_lobby)
            _success = True

        # Pass the data off into a handling thread:
        if (_success == True):
            print("Starting a thread...")
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

#Begin the server
receive()
