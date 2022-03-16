#Lobby class
import threading

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
        self.spawn_thread(client)

    def removeClient(self,index):
        self.clients.pop(index)


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
                #print("Data is: "+str(message))
                self.broadcast(message, client)
            except:
                #print("//data failed!//")
                # Something went horribly wrong! Disconnect the client.
                index = self.clients.index(client)
                self.removeClient(index)
                client.close()

                #if (self.lobby_host == client): TO-DO: Host migration
                print("Client removed from lobby: "+str(self.id))
                break

    def spawn_thread(self, client):
        thread = threading.Thread(target=self.handle, args=(client,))
        thread.start()

    def toString(self):
        _str = str(self.getId())+":\n- Clients:\n"

        for c in self.clients:
            _str += "-- "+str(c)+"\n"

        return _str



    
