#Lobby class
import threading

class Lobby:
    def __init__(self, id):
        self.id = id
        self.clients = []

    def getId(self):
        return self.id

    def addClient(self,client):
        self.clients.append(client)
        print("Client added to lobby: "+str(self.id))
        self.spawn_thread(client)

    def removeClient(self,index):
        self.clients.remove(index)



    # Sending packets to all clients, excluding the player who initially sent the packet
    def broadcast(self, message, exclude):
        for client in self.clients:
            if (client != exclude):
                    client.send(message)
    
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
                print("Client removed from lobby: "+str(self.id))
                break

    def spawn_thread(self, client):
        thread = threading.Thread(target=self.handle, args=(client,))
        thread.start()


    
