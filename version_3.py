import pygame
from version_3_backend import Backend
from version_3_widgets import *

# Initialise Pygame modules
pygame.init()

# Game constants (pixels)
DIMENSIONS = (510, 500)                                         # Dimensions of the game window
SIZE = 30                                                       # Length of each grid
PELLET_SIZE = 10                                                # Length of each pellet

# Game initialisation
screen = pygame.display.set_mode(DIMENSIONS)                    # Create the window
screen.fill(BACKGROUND_COLOR)                                   # Set the initial colour
pygame.display.set_caption("Pacman")                            # Set the title

backend = Backend()                                             # Create the backend and the socket 

clock = pygame.time.Clock()                                     # Create a Clock object
FPS = 60                                                        # The framerate constant

controlling_pacman = None


class Placeable(pygame.sprite.Sprite):

    all_group = pygame.sprite.Group()                           # A container for sprites
    
    def __init__(self, x, y, size: tuple, color: tuple):
        
        # Make the sprite.
        pygame.sprite.Sprite.__init__(self)                     # Create a new sprite object
        self.image = pygame.Surface(size)                       # Create the sprite image
        self.image.fill(color)                                  # Set the sprite's colour

        self.rect = self.image.get_rect()                       # Create a rect with the bounds of the sprite
        self.rect.x = x                                         # Move the sprite to the initial x point
        self.rect.y = y                                         # Move the sprite to the initial y point

        self._add_to_groups()                                   # Add to the sprite container
    
    def _add_to_groups(self):
        Placeable.all_group.add(self)


class Wall(Placeable):

    wall_group = pygame.sprite.Group()

    def __init__(self, x, y, size: tuple, color: tuple):
        super().__init__(x, y, size, color)                     # Create a placeable object

    def _add_to_groups(self):
        super()._add_to_groups()                                # Add to the collective sprite container
        Wall.wall_group.add(self)                               # Add to the wall sprite container


class Pellet(Placeable):
    
    pellet_group = pygame.sprite.Group()

    def __init__(self, x, y, size: tuple, color: tuple):
        super().__init__(x, y, size, color)                     # Create a placeable object
    
    def _add_to_groups(self):
        super()._add_to_groups()                                # Add to the collective sprite container
        Pellet.pellet_group.add(self)                           # Add to the wall sprite container


class Playable(Placeable):

    def __init__(self, x, y, size: tuple, color: tuple, speed: int):
        super().__init__(x, y, size, color)                     # Create a placeable object
        
        # Create private instance attributes
        self.__width = size[0]
        self.__height = size[1]
        self.__speed = speed
        self.last_key = None

        self.spawn = (x, y)
    
    def move_to_spawn(self):
        self.rect.x, self.rect.y = self.spawn
    
    def __move(self):
        
        directions = {
            pygame.K_LEFT: (-self.__speed, 0),
            pygame.K_RIGHT: (self.__speed, 0),
            pygame.K_UP: (0, -self.__speed),
            pygame.K_DOWN: (0, self.__speed)
        }

        keys = pygame.key.get_pressed()                                                             # Get array of key-states
        if keys:
            for key in directions:
                if keys[key]:                                                                       # Arrow key is pressed
                    new_position = self.rect.move(directions[key])                                  # Find new coordinates
                    if not any(wall.rect.colliderect(new_position) for wall in Wall.wall_group):    # No wall collisions
                        self.rect = new_position                                                    # Update coordinates
                        self.last_key = key
                        break
            else:                                                                                   # No arrow key is pressed
                if self.last_key:                                                                 # Validation for initial state being falsy
                    new_position = self.rect.move(directions[self.last_key])                      # Find coordinates if moved in last directon
                    if not any (wall.rect.colliderect(new_position) for wall in Wall.wall_group):   # No wall collisions
                        self.rect = new_position                                                    # Update coordinates
    
    def __check_for_teleport(self):
        #Find the width of the observable window
        x_min = 0 + self.__width
        x_max = DIMENSIONS[0] - self.__width

        if self.rect.x < x_min:
            # Teleport to the right
            self.rect.x = x_max
        
        elif self.rect.x > x_max:
            # Teleport to the left
            self.rect.x = x_min

    def main(self):
        self.__move()
        self.__check_for_teleport()


class Pacman(Playable):

    pacman_group = pygame.sprite.Group()

    def __init__(self, x, y, size: tuple, color: tuple, speed: int):
        super().__init__(x, y, size, color, speed)              # Create a playable object
        self.score = 0                                          # Set the default score

    def _add_to_groups(self):
        super()._add_to_groups()                                # Add to the collective container
        Pacman.pacman_group.add(self)                           # Add to the pacman container
    
    def pellet_checker(self):
        # Get an array of pellet objects that have collided with Pacman and then remove them from pellet_group.
        collided_pellets = pygame.sprite.spritecollide(self, Pellet.pellet_group, True)

        # Increase the score by one per pellet
        if collided_pellets:
            for pellet in collided_pellets:
                self.score += 1                                        
                Placeable.all_group.remove(pellet)
    
    def has_ghost_eaten_pacman(self):
        # Checks if a Ghost sprite is colliding with the Pacman sprite.
        # Returns true if the Ghost has eaten Pacman.
        collision = pygame.sprite.spritecollide(self, Ghost.ghost_group, False)
        return True if collision else False
    
    def main(self):
        super().main()
        self.pellet_checker()


class Ghost(Playable):
    ghost_group = pygame.sprite.Group()

    def __init__(self, x, y, size: tuple, color: tuple, speed: int):
        super().__init__(x, y, size, color, speed)
    
    def _add_to_groups(self):
        super()._add_to_groups()
        Ghost.ghost_group.add(self)

    def main(self):
        super().main()


class Start(Page):
    def __init__(self):
        # Create the widgets.
        self.title = Text(25, 50, "Pacman!", 48)
        self.startbutton = Button(25, 200, "Play", 48, BLACK)
        self.widgets = [self.title, self.startbutton]
    
    def event_handler(self, event):
        # Left mouse button click on the start button.
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.startbutton.rect.collidepoint(event.pos):
                self.next_page()
    
    def change_title(self, text: str):
        # Updates the title text to the given value.
        self.title.text = text


class IP(Page):
    ip = None
    def __init__(self):
        # Create the widgets.
        self.title = Text(25, 50, "Enter IP", 48)
        self.input = Input(25, 200, 48)
        self.submit = Button(25, 300, "Submit", 48, BLACK)
        self.widgets = [self.title, self.input, self.submit]
    
    def event_handler(self, event):
        # Keyboard input is handled by the input object.
        if event.type == pygame.KEYDOWN:
            self.input.handle_input(event)

        # Left mouse button click on the submit button.
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit.rect.collidepoint(event.pos):
                # Save the input.
                IP.ip = self.input.text
                # Reset page for next time.
                self.reset_input()
                self.next_page()
    
    def reset_input(self):
        # Empty the IP input for retry.
        self.input.text = ""
    

class Port(Page):
    port = None
    def __init__(self):
        # Create the widgets.
        self.title = Text(25, 50, "Enter Port", 48)
        self.input = Input(25, 200, 48)
        self.submit = Button(25, 300, "Submit", 48, BLACK)
        self.widgets = [self.title, self.input, self.submit]
        self.retry = False
    
    def connect_to_server(self):
        # Attempts to connect to the server using the user's input.
        # Returns true if a conenction is established.
        global backend
        connected = backend.connect(IP.ip, Port.port)
        return True if connected else False
    
    def event_handler(self, event):
        # Keyboard input event is handled by the input object if the page isn't in retry state.
        if event.type == pygame.KEYDOWN and not self.retry:
            self.input.handle_input(event)
        
        # Left mouse button click on the submit button
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit.rect.collidepoint(event.pos):

                if not self.retry:
                    Port.port = self.input.text
                    self.reset_input()

                    #Attempt a server connection.
                    success = self.connect_to_server()

                    if success:
                        self.next_page()
                        
                    else:
                        # Connection unsuccessful.
                        # Change page to be in the retry state.
                        self.title.text = "Incorrect Information"
                        self.submit.text = "Click Here To Retry"
                        self.input.text = ""
                        self.retry = True
                else:
                    #Submit button pressed while in retry state.
                    self.retry = False
                    # Reset page to initial state.
                    self.title.text = "Enter Port Number"
                    self.submit.text = "Submit"
                    # Change page to IP input.
                    self.change_page(1)
    
    def reset_input(self):
        # Empty the port input for retry.
        self.input.text = ""


class Interim(Page):
    def __init__(self):
        # Create the widgets.
        self.title = Text(25, 50, "Waiting for sync", 48)
        self.widgets = [self.title]
        self.lobby_load_request_sent = False
    
    def update(self, target_surface):
        # Update the widgets.
        super().update(target_surface)

        if not self.lobby_load_request_sent:
            # Send an load request.
            backend.send("lobby-load-request", "_")
            self.lobby_load_request_sent = True
        
        packet = backend.receive()
        if packet:
            header = packet[0]

            # When all players are at the Interim page.
            if header == "lobby-load-granted":   
                self.lobby_load_request_sent = False
                self.next_page()
            
            # A player has disconnected from the server.
            elif header == "disconnect":
                # Disconnect the client.
                backend.disconnect()
                # Change to the start page.
                self.change_page(0)
                # Update the title to inform the player.
                pages[0].change_title("Player disconnected")


class Lobby(Page):
    def __init__(self):
        # Create the widgets.
        self.title = Text(25, 50, "Pick your character", 48)
        self.pacman = Button(25, 150, "Pacman", 48, BLACK)
        self.ghost = Button(25, 250, "Ghost", 48, BLACK)
        self.widgets = [self.title, self.pacman, self.ghost]
        self.buttons = [self.pacman, self.ghost]
        #Load the sound effect for when the game starts.
        self.intro_music = pygame.mixer.Sound("start.wav")

        self.local_button_active = False
    
    def event_handler(self, event):
        global controlling_pacman
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            
            # Pacman button is pressed.
            if self.pacman.rect.collidepoint(event.pos) and not self.pacman.active and not self.local_button_active:
                # Let the other player know.
                backend.send("pacman-selected", "_")
                self.pacman.active = True
                self.pacman.background_colour = GREEN
                controlling_pacman = True
                self.local_button_active = True
            
            # Ghost button is pressed.
            elif self.ghost.rect.collidepoint(event.pos) and not self.ghost.active and not self.local_button_active:
                # Let the other player know.
                backend.send("ghost-selected", "_")
                self.ghost.active = True
                self.ghost.background_colour = GREEN
                controlling_pacman = False
                self.local_button_active = True
        
    def update(self, target_surface):
        # Update page. Draw widgets.
        super().update(target_surface)
        
        backend.send("game-load-request", "_")
        packet = backend.receive()
        if packet:
            header = packet[0]
            # Other player has selected the Pacman button.
            if header == "pacman-selected":
                self.pacman.background_colour = RED
                self.pacman.active = True
            
            # Other player has selected the Ghost button.
            elif header == "ghost-selected":
                self.ghost.background_colour = RED
                self.ghost.active = True
            
            # Both players have selected a character.
            elif header == "start-game":
                # Reset the page
                self.pacman.background_colour = BLACK
                self.pacman.active = False
                self.ghost.background_colour = BLACK
                self.ghost.active = False
                self.local_button_active = False

                # Update the player label depending on what character button is pressed.
                pages[5].update_player_label_text()
                # Play the intro music.
                self.intro_music.play()
                self.next_page()

            # A player has disconnected from the server.
            elif header == "disconnect":
                # Disconnect the client.
                backend.disconnect()
                # Change to the start page.
                self.change_page(0)
                # Update the title to inform the player.
                pages[0].change_title("Player disconnected")


class Game(Page):
    def __init__(self):
        self.maze_number = 0
        
        # Create the game objects.
        self.create_maze()
        self.pacman = Pacman(30, 30, (SIZE, SIZE), YELLOW, 2)
        self.ghost = Ghost(450, 240, (SIZE, SIZE), RED, 2)
        
        # Create the widgets.
        self.score_label = Text(50,300,"Score = 0", 48)
        self.player_label = Text(50, 350, "Playing as ?", 48)
        self.mute_button = Button(50, 400, "Mute", 48, GREEN)
        self.mute = False
        self.widgets = [self.score_label, self.player_label, self.mute_button]

        # Load the sound effects.
        self.death_sound_effect = pygame.mixer.Sound("death.wav")
        self.victory = pygame.mixer.Sound("victory.wav")

    def create_maze(self):
        mazes = ["maze1.txt", "maze2.txt", "maze3.txt"]
        '''
        Creates wall and pellet objects from a file template.
        The position of each character in the file is used to determine its grid coordinates.
        The object that the character represents is created and placed at its grid coordinates.
        Key:
            "x" = wall
            "o" = pellet
        '''
        # Open the file that contains the maze data.
        with open(mazes[self.maze_number], "r") as f:
            # Iterate over each line of the file.
            for row, line in enumerate(f):
                # Iterate over each character in the line.
                for col, char in enumerate(line):
                    if char == "x": 
                        # Create a Wall object.
                        Wall(col*SIZE, row*SIZE, (SIZE, SIZE), BLACK)
                    elif char == "o":
                        # Create a Pellet object.
                        Pellet(col*SIZE+PELLET_SIZE, row*SIZE+PELLET_SIZE, (PELLET_SIZE, PELLET_SIZE), ORANGE)
                    else:
                        # Create an empty grid.
                        pass
        
        if self.maze_number == len(mazes) - 1:
            # Go back to the first maze.
            self.maze_number = 0
        else:
            # Go to the next maze.
            self.maze_number += 1

    def update_player_label_text(self):
        # Updates the label to display what character the player is controlling.
        global controlling_pacman
        if controlling_pacman: 
            self.player_label.text = "Controlling Pacman"
        else:
            self.player_label.text = "Controlling Ghost"

    def update(self, target_surface):
        global controlling_pacman
        
        # Move sprite in control.
        (self.pacman if controlling_pacman else self.ghost).main()

        # Send coordinates to other player.
        header = "pacman-coordinates" if controlling_pacman else "ghost-coordinates"
        payload = tuple(self.pacman.rect[:2]) if controlling_pacman else tuple(self.ghost.rect[:2])
        backend.send(header, payload)

        # Receive coordinates.
        packet = backend.receive()
        if packet:
            header, payload = packet[0], packet[1]

            match header:
                case "pacman-coordinates":
                    self.pacman.rect[:2] = payload
                    self.pacman.pellet_checker()
                
                case "ghost-coordinates":
                    self.ghost.rect[:2] = payload
                
                case "end-game":
                    # End the game.
                    # Play the game over sound effect.
                    self.death_sound_effect.play()
                    # Update the Post Game page score label.
                    pages[6].update_score_label(self.pacman.score)
                    # Reset the page for the next time.
                    self.reset()
                    self.pacman.score = 0
                    controlling_pacman = False
                    # Change to the Post Game page
                    self.next_page()
                    return

                # An other player has disconnected from the server.
                case "disconnect":
                    # Disconnect the client.
                    backend.disconnect()
                    # Change to the start page.
                    self.change_page(0)
                    # Update the title to inform the player.
                    pages[0].change_title("Player disconnected")
                
                case "_":
                    print('unexpected header')

        self.score_label.text = f'Score = {self.pacman.score}'

        # Game over check.
        if self.pacman.has_ghost_eaten_pacman():
            backend.send("end-game", self.pacman.score)
        
        # Check for victory if all pellets eaten.
        if len(Pellet.pellet_group) == 0:
            # Play the victory sound effect.
            self.victory.play()
            # Reset the page.
            self.reset()
            # Load the next maze.
            self.create_maze()

        # Reset surface and draw HUD.
        super().update(target_surface)
        # Draw sprites.
        Placeable.all_group.draw(target_surface)
        pygame.display.update()
    
    def reset(self):
        # Resets the page and its sprites.
        self.pacman.move_to_spawn()
        self.ghost.move_to_spawn()

        self.pacman.last_key = None
        self.ghost.last_key = None

        Placeable.all_group.remove(Wall.wall_group)
        Placeable.all_group.remove(Pellet.pellet_group)
        Pellet.pellet_group.empty()
        Wall.wall_group.empty()

    def event_handler(self, event):
        # Left mouse button clicked on mute button.
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.mute_button.rect.collidepoint(event.pos):
                # Toggle mute button state.
                self.mute = not self.mute
                
                if self.mute:
                    self.mute_button.background_colour = RED
                    # Stop audio playback.
                    pygame.mixer.pause()
                
                else:
                    self.mute_button.background_colour = GREEN
                    # Resume audio playback.
                    pygame.mixer.unpause()


class PostGame(Page):
    def __init__(self):
        # Create the widgets.
        self.title = Text(25, 50, "GAME OVER", 48)
        self.score_label = Text(25, 100, f"Score", 48)
        self.submit = Button(25, 250, "Play again", 48, BLACK)
        self.widgets = [self.title, self.score_label, self.submit]
    
    def update_score_label(self, value):
        # Updates the score label to contain the given value.
        self.score_label.text = f"Score = {value}"
    
    def event_handler(self, event):
        # Left mouse button press on the play again button.
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit.rect.collidepoint(event.pos):
                self.change_page(3)

    def update(self, target_surface):
        super().update(target_surface)
        packet = backend.receive()
       
        if packet:
            header = packet[0]
            
            # A player has disconnected from the server.
            if header == "disconnect":
                # Disconnect the client.
                backend.disconnect()
                # Change to the start page.
                self.change_page(0)
                # Update the title to inform the player.
                pages[0].change_title("Player disconnected")
    

# Create the pages for the GUI.
page0= Start()
page1 = IP()
page2 = Port()
page3 = Interim()
page4 = Lobby()
page5 = Game()
page6 = PostGame()

# Holds the sequence that the pages are to be accessed
pages = [page0, page1, page2, page3, page4, page5, page6]

# Game loop
while True:
    
    # Set the max FPS to 60
    clock.tick(FPS)

    # Update the screen's page
    pages[Page.current_page].update(screen)

    for event in pygame.event.get():
        # Exit button
        if event.type  == pygame.QUIT:
            backend.send("disconnect", "_")
            # Uninitialise pygame
            pygame.quit()
            # Close program
            exit()
        
        # Handle any events for the page
        pages[Page.current_page].event_handler(event)

    pygame.display.update()
