#Lobby class
from encodings import utf_8
import threading
import json

class Lobby:
    def __init__(self, id):
        self.id = id
        self.clients = []
        self.lobby_host = None

    def getId(self):
        return self.id

    def getClients(self):
        return self.clients

    def addClient(self,client):
        #The first player in the lobby is desegnated as the host.
        if (len(self.clients) == 0):
            self.lobby_host = client

        #Add the new client to clients and start a thread for them.
        self.clients.append(client)
        print("Client added to lobby: "+str(self.id))
        
        #Spawn a thread for this client
        self.spawn_thread(client)

        #Send lobby info
        self.sendLobbyInfo(client)


    def removeClient(self,index):
        self.clients.pop(index)


    def sendLobbyInfo(self, client):
        data = """{ "cmd" : "lobby_connect_success", "l_id" : """+ str(self.id) + " }"

        data = str(json.loads(data)).replace("'", '"')
        data = data.encode("utf_8")
        #print(data)
        client.send(data)


    # Sending packets to all clients, excluding the player who initially sent the packet OR send it to the host
    def broadcast(self, message, exclude):
        if (exclude == self.lobby_host):
            for client in self.clients:
                if (client != exclude):
                        client.send(message)
        else:
            self.lobby_host.send(message)
    
     # Handling Messages From Clients
    def handle(self, client):
        while True:
            #print("//data received!//")
            try:
                #print("//data received!//")
                # Relay those messages!
                message = client.recv(512) #No idea how to make this data size accurate. 512 should be good but no clue!
                
                print("Data is: "+str(message))
                self.broadcast(message, client)
            except:
                #print("//data failed!//")
                # Something went horribly wrong! Disconnect the client.
                index = self.clients.index(client)
                self.removeClient(index)
                client.close()

                #if (self.lobby_host == client): TO-DO: Host migration
                print("Client removed from lobby: "+str(self.id))
                self.message_disconnect(client)
                break

    def spawn_thread(self, client):
        thread = threading.Thread(target=self.handle, args=(client,))
        thread.start()


    def toString(self):
        _str = str(self.getId())+":\n- Clients:\n"

        for c in self.clients:
            _str += "-- "+str(c)+"\n"

        return _str

    # Properly unpack packets and split them
    def preparePacket(packet):
        packet_strings = packet.split("{")
        loaded_packet_list = []

        for i in packet_strings:
            if (i != ""):
                new_string = "{"+i
                new_string = json.loads(new_string)
                loaded_packet_list.append(new_string)

        return loaded_packet_list

    def constructPacket(self, **data):
        _counter = 0
        str_json = "{"
        for key, value in data.items():
            if (_counter > 0):
                str_json += ","

            str_json += f""" "{key}" : {value}"""
            _counter += 1

        str_json += "}"
        #print("String json: "+str_json)
        #str_json = json.loads(str_json)
        str_json = str_json.encode("utf-8") #encode the json into byte form
        return str_json


    def message_disconnect(self, client):
        #TO-DO Store playernames in a lobby client?
        message = self.constructPacket(cmd='"player_disconnected"')
        self.broadcast(message, client)



    
