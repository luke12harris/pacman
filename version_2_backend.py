import socket
import pickle

class Backend:

    def __init__(self, ip: str, port: int): 
        #Connect to the server.        
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientsocket.connect((ip, port))
        self.clientsocket.settimeout(0.1)  #Seconds before a timeout exception is raised
        
        print("Connection established")
    
    def send(self, header:str, payload):
        #Send data to the server
        packet = bytes(pickle.dumps((header, payload)))
        self.clientsocket.send(packet)
    
    def receive(self):
        #Receive data from server.
        try:
            packet = self.clientsocket.recv(1024)
            packet = pickle.loads(packet)
        
        except socket.timeout:
            return None
            
        except pickle.UnpicklingError as e:
            print(e)
            return None

        else:
            return packet