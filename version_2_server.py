import socket
import threading
import pickle

class Server(object):
    def __init__(self):
        #The machine's IP
        self.ip = "192.168.0.225"
        
        #Hardcoded port
        self.port = 12345

        print(f'Socket = {self.ip}:{self.port}')
        
        #Create TCP IPv4 socket.
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((self.ip,self.port))

        #Array of connection tuples like (conn, addr) 
        self.clients = []

        self.listen()
    
    def receive_and_respond(self, conn, address):
        print(f'new connection: {address}')

        def send_to_other_client(packet):
            for client in self.clients:
                if client[1] != address:
                    client[0].send(packet)

        while True:
            #Receive packet object as bytes.
            packet = self.receive(conn)
            
            if packet:
                #Deserialise packet and select the header.
                header = pickle.loads(packet)[0]

                #Perform action depending on the header.
                match header:

                    case "pacman-coordinates":
                        send_to_other_client(packet)
                    
                    case "ghost-coordinates":
                        send_to_other_client(packet)

                    case _:
                        print("unexpected header")

    def listen(self): 
        #Listen for new connections.
        self.serversocket.listen()
        while True:
            #Accept connection with socket.
            conn, address = self.serversocket.accept() 

            #Add client socket information to list.
            self.clients.append((conn, address))

            #Start a thread to monitor this connection.
            threading.Thread(target=self.receive_and_respond, args=(conn, address)).start() 

            '''
            https://docs.python.org/3.10/library/socket.html#socket.socket.accept
            conn is a new socket object usable to send and receive data on the connection,
            address is the address bound to the socket on the other end of the connection.
            '''

    def receive(self, clientsocket): 
        # Receive a maximum of 1024 bytes
        return clientsocket.recv(1024)


server = Server()
