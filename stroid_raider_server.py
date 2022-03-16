import socket
import threading
import json
import Stroid_Raider_Lobby as Lobby
from ast import literal_eval

# Connection Data
ip = '127.0.0.1'
port = 55555

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ip, port))
server.listen()

test = """{ "cmd": "lobby_info", "id": 0.0 }"""
print(test)
print(type(test))
print(len(test))
test = json.loads(test)
print("Decode Test: "+str(test["id"]))

# List of lobbies
lobbies = []

# Properly unpack packets and split them
def unpack(packet):
    _str = packet.split("{")
    new_str = []

    for n in _str:
        _n = "{"+n
        #_n = json.loads(_n)
        new_str.append(_n)

    print("New string:")
    print(new_str)
    return new_str

# Receiving / Listening Function
def receive():
    next_id = 1000

    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        #Add the client to the correct lobby
        
        lobby_packet = client.recv(512)
        #lobby_packets = unpack(lobby_packet)
        print(lobby_packet)
        print(len(lobby_packet))
        lobby_packet = lobby_packet.decode('utf-8').replace('\x00', '')
        #lobby_packet = lobby_packet.strip()
        print(lobby_packet)
        print(type(lobby_packet))
        print(len(lobby_packet))
        lobby_packet = json.loads(lobby_packet)
        

        # Extract the correct id
        lobby_id = -1

        if (lobby_packet["cmd"] == "lobby_info"):
            lobby_id = lobby_packet["id"]
        print("Requested Lobby ID:")
        print(lobby_id)
                
        _success = False

        if (lobby_id != -1):
            #- Look for an existing lobby to add the client into
            for lobby in lobbies:
                if (lobby.getId() == lobby_id):
                    lobby.addClient(client)
                    _success = True
                    break

            #- If a lobby doesn't exist, make one and add the client to that.
        if (_success == False & isinstance(lobby_id,int)):
            temp_lobby = Lobby.Lobby(next_id)
            print("Lobby created: "+str(temp_lobby.getId()))

            temp_lobby.addClient(client)
            lobbies.append(temp_lobby)

        # Pass the data off into a handling thread:
            print("Starting a thread...")
            temp_lobby.spawn_thread(client)

            next_id += 1

#Begin the server
receive()
