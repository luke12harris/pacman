import socket
import pickle

class Backend:

    def __init__(self):   
        # Create TCP IPv4 socket object
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def create_socket(self):
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def disconnect(self):
        try:
            self.send("disconnect", "_")
            self.clientsocket.close()
            self.create_socket()
        
        except TimeoutError:
            pass


    def connect(self, ip: str, port: int):
        try:
            self.clientsocket.connect((str(ip), int(port)))
            self.clientsocket.settimeout(0.1)  #Seconds before a timeout exception is raised
            print("Connection established")
        
        except:
            return False
        
        else:
            return True
    
    def send(self, header:str, payload):
        try:
            #Send data to the server
            packet = bytes(pickle.dumps((header, payload)))
            self.clientsocket.send(packet)
        
        except OSError:
            # Socket not connected anymore
            pass
    
    def receive(self):
        #Receive data from server.
        try:
            packet = self.clientsocket.recv(1024)
            packet = pickle.loads(packet)
        
        except socket.timeout:
            return None
            
        except pickle.UnpicklingError:
            return None

        except EOFError:
            return None

        except ConnectionResetError:
            return None

        else:
            return packet