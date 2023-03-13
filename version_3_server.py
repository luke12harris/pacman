import socket
import threading
import pickle
import pygame
from version_3_widgets import *

pygame.init()

class Server(object):
    def __init__(self):
        try:

            self.ip = None
            self.port = None

            # Get the hostname of the machine
            hostname = socket.gethostname()
            
            # Get the available addresses for the hostname on any port
            addresses = socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_STREAM)

            for address in addresses:
                # Find an IPv4 address that is not the loopback address
                if address[0] == socket.AF_INET and address[4][0] != '127.0.0.1':
                    self.ip = address[4][0]
                    break

            #Create TCP IPv4 socket.
            self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Bind the socket to free port.
            self.serversocket.bind((self.ip, 0))

            self.port = self.serversocket.getsockname()[1]

            #Array of connection tuples like (conn, addr) 
            self.clients = []

            self.lobby_load_requests = 0

            self.ready_players = 0
            self.game_load_granted = 0

            self.score = None
            self.usernames = []

            self.screen = pygame.display.set_mode((500, 300))
            self.screen.fill(BACKGROUND_COLOR)
            pygame.display.set_caption("Pacman server")
            

            self.shutdown_flag = threading.Event()

            threading.Thread(target=self.listen).start() 

            self.gui() # Update the screen
        except OSError:
            print("Server currently open")

    def exit(self):
        self.shutdown_flag.set()

        # Close the server
        self.serversocket.close()
        
        # Close threads safely
        for thread in threading.enumerate():
            if thread != threading.current_thread():
                thread.join()
        
        # Quit Pygame
        pygame.quit()

        # Terminate Python
        exit()

    def gui(self):
        class Information(Page):
            def __init__(self, ip: str, port: str):
                self.ip = Text(25, 50, f"IP = {ip}", 48)
                self.port = Text(25, 150, f"Port = {port}", 48)
                self.widgets = [self.ip, self.port]
        
        information_page = Information(self.ip, self.port)

        while True:
            information_page.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

            pygame.display.update()

    def serialise(self, header, payload):
            return bytes(pickle.dumps((header, payload)))
    
    def receive_and_respond(self, conn, address):
        print(f'new connection: {address}')

        def send_to_other_client(packet):
            try:
                for client in self.clients:
                    if client[1] != address:
                        client[0].send(packet)
            except BrokenPipeError:
                pass
        
        def send_to_every_client(packet):
            try:
                for conn, address in self.clients:
                    conn.send(packet)
            
            except BrokenPipeError:
                pass

        while not self.shutdown_flag.is_set():
            #Receive packet object as bytes.
            packet = self.receive(conn)
            
            if packet:
                #Deserialise packet and select the header.
                header = pickle.loads(packet)[0]
                payload = pickle.loads(packet)[1]

                #Perform action depending on the header.
                match header:

                    case "pacman-coordinates":
                        send_to_other_client(packet)
                    
                    case "ghost-coordinates":
                        send_to_other_client(packet)

                    case "pacman-selected":
                        send_to_other_client(packet)
                        self.ready_players += 1
                    
                    case "ghost-selected":
                        send_to_other_client(packet)
                        self.ready_players += 1
                    
                    case "end-game":
                        self.score = payload
                        send_to_every_client(packet)

                    case "lobby-load-request":
                        self.lobby_load_requests += 1

                        if self.lobby_load_requests == 2:
                            # Grant lobby access
                            packet = self.serialise("lobby-load-granted", "_")
                            send_to_every_client(packet)
                        
                            # Reset attributes for the next game
                            self.lobby_load_requests = 0
                            self.lobby_load_granted = 0
                    
                    case "game-load-request":
                        if self.ready_players == 2:
                            packet = self.serialise("start-game", "_")
                            send_to_every_client(packet)
                            self.game_load_granted += 1
                            print(self.game_load_granted)
                        
                        if self.game_load_granted == 2:
                            # Reset attributes for the next game
                            self.ready_players = 0
                            self.game_load_granted = 0
                    
                    case "disconnect":
                        print('disconnect received')
                        self.clients.remove((conn, address))
                        send_to_other_client(packet)

                    case _:
                        print("unexpected header")
            
    def listen(self): 
        #Listen for new connections.
        self.serversocket.listen()

        while not self.shutdown_flag.is_set():

            try:

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
            
            except ConnectionAbortedError:
                # Server socket is closed, dont accept any connections.
                break

    def receive(self, clientsocket): 
        try:
            # Receive a maximum of 1024 bytes
            packet = clientsocket.recv(1024)
        
        except ConnectionResetError:
            return None

        else:
            return packet

server = Server()

