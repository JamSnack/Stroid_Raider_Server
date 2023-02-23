#Lobby class
from encodings import utf_8
import threading
import json

class Lobby:
    def __init__(self, id, packet_size):
        self.id = id #lobby_id
        self.clients = [] #list of clients
        self.lobby_host = None #the client who is hosting the lobby
        self.packet_size = packet_size
        self.next_player_id = 0 #Used to assign player ids

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
        data = """{ "cmd" : "lobby_connect_success", "l_id" : """ + str(self.id) + """, "plr_id" : """ + str(self.next_player_id) + " }"

        data = str(json.loads(data)).replace("'", '"')
        data = data.encode("utf_8")
        #print(data)
        client.send(data)


        
        if (client != self.lobby_host):
            data = """{ "cmd" : "player_connected", "p_id" : """ + str(self.next_player_id) + " }"
            data = str(json.loads(data)).replace("'", '"')
            data = data.encode("utf_8")
            
            self.lobby_host.send(data)

        self.next_player_id += 1


    # Sending packets to all clients, excluding the player who initially sent the packet (server to clients) OR send it to the packet to the lobby host (client to server)
    def broadcast(self, message, exclude):
        if (exclude == self.lobby_host):
            for client in self.clients:
                if (client != exclude):
                        client.send(message)
        else:
            self.lobby_host.send(message)
    
     # Handling Messages From Clients
    def handle(self, client):
        break_client = False

        while True:

            message_length = 0
            header = b''
            while True:
                try:
                    _c = client.recv(1) #recv one byte from the client
                    print(_c)

                    if (_c == b'|'):
                        try:
                            print("H : " + str(header))
                            message_length = int(header)
                        except Exception as e:
                            print(e)
                            message_length = -1
                        break
                    else:
                        header = header + _c
                except:
                    break_client = True
                    break
            
            #We have constructed the header at this point, use it to receieve and distribute the rest of the packet
            chunks = []
            bytes_received = 0

            while bytes_received < message_length:
                try:
                    data = client.recv(message_length - bytes_received)
                    
                    bytes_received = bytes_received + len(data)
                    chunks.append(data)
                    #print('bytes_received')
                    

                    #we have received all of the data: broadcast it and then reset. Otherwise append to chunks.
                    if (bytes_received == message_length):
                        prepared_data = b''.join(chunks)

                        #1. b'\x00{ "h": 0.0, "cmd": "player_move", "p_id": 1.0, "v": -1.0, "s": 0.0 }'
                        print(prepared_data)

                        self.broadcast(prepared_data, client) #think this'll work?
                
                except:
                    print("Error receiving data: " + str(b''.join(chunks)))
                    break_client = True


            if break_client:
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
        message = self.constructPacket(cmd='"player_disconnected"')
        self.broadcast(message, client)



    
