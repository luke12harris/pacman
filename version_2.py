import pygame
from version_2_backend import Backend

# Initialise Pygame modules
pygame.init()

# RGB colour constants
RED     = (255,   0,   0)
ORANGE  = (255, 165,   0)
YELLOW  = (255, 255,   0)
GREEN   = (  0, 255,   0)
BLUE    = (  0,   0, 255)
BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)
BACKGROUND_COLOR = BLUE

# Game constants (pixels)
DIMENSIONS = (420, 420)                                                 # Dimensions of the game window
SIZE = 30                                                               # Grid side length
PACMAN_SIZE = (SIZE, SIZE)                                              # Dimensions of Pacman / Ghost
PELLET_SIZE = (10,10)                                                   # Dimensions of a pellet

class Game():
    def __init__(self):
        
        self.screen = pygame.display.set_mode(DIMENSIONS)               # Create the window
        self.screen.fill(BACKGROUND_COLOR)                              # Set the color
        pygame.display.set_caption("Pacman")                            # Set the title
    
    def __event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:                               # Exit button pressed
                pygame.quit()                                           # Close the game
                exit()

    def __update(self):
        self.screen.fill(BACKGROUND_COLOR)                              # Reset screen
        Placeable.all_group.draw(self.screen)                           # Draw objects on screen
        pygame.display.update()                                         # Update screen

    def main(self):
        self.__event_handler()
        self.__update()


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
        self.__last_key = None
    
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
                if keys[key]:                                                                       # A direction key is pressed
                    new_position = self.rect.move(directions[key])                                  # Find new coordinates
                    if not any(wall.rect.colliderect(new_position) for wall in Wall.wall_group):    # No wall collisions
                        self.rect = new_position                                                    # Update coordinates
                        self.__last_key = key
                        break
            else:                                                                                   # Wall collisions
                if self.__last_key:                                                                 # Validation for initial None state
                    new_position = self.rect.move(directions[self.__last_key])                      # Find coordinates if moved in last directon
                    if not any (wall.rect.colliderect(new_position) for wall in Wall.wall_group):   # If there are no new collisions
                        self.rect = new_position                                                    # Update coordinates
    
    def __boundary_checker(self):
        # Find the size of the window
        x_min = 0
        x_max = DIMENSIONS[0] - self.__width
        y_min = 0
        y_max = DIMENSIONS[1] - self.__height

        if self.rect.x < x_min:                                         # Too far left
            self.rect.x = x_min
        
        elif self.rect.x > x_max:                                       # Too far right
            self.rect.x = x_max

        if self.rect.y < y_min:                                         # Too far up
            self.rect.y = y_min
        
        elif self.rect.y > y_max:                                       # Too far down
            self.rect.y = y_max

    def main(self):
        self.__move()
        self.__boundary_checker()


class Pacman(Playable):

    pacman_group = pygame.sprite.Group()

    def __init__(self, x, y, size: tuple, color: tuple, speed: int):
        super().__init__(x, y, size, color, speed)              # Create a playable object
        self.score = 0                                          # Set the default score

    def _add_to_groups(self):
        super()._add_to_groups()                                # Add to the collective container
        Pacman.pacman_group.add(self)                           # Add to the pacman container
    
    def pellet_checker(self):
        # Get an array of pellet objects that have collided with the sprite and then remove them from pellet_group.
        collided_pellets = pygame.sprite.spritecollide(self, Pellet.pellet_group, True)

        # Increase the score by one per pellet
        if collided_pellets:
            for pellet in collided_pellets:
                self.score += 1                                        
                Placeable.all_group.remove(pellet)
                print(f'score = {self.score}')
    
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


def create_maze():
    '''
    Creates wall and pellet objects from a file template.
    The position of each character in the file is used to determine its grid coordinates.
    The object that the character represents is created and placed at its grid coordinates.
    Key:
        "x" = wall
        "o" = pellet
    '''
    # Open the file that contains the maze data.
    with open("mini-maze.txt", "r") as f:
        # Iterate over each line of the file.
        for row, line in enumerate(f):
            # Iterate over each character in the line.
            for col, char in enumerate(line):
                if char == "x": 
                    # Create a Wall object.
                    Wall(col*SIZE, row*SIZE, (SIZE, SIZE), BLACK)
                elif char == "o":
                    # Create a Pellet object.
                    Pellet(col*SIZE+10, row*SIZE+10, PELLET_SIZE, ORANGE)
                else:
                    # Create an empty grid.
                    pass

backend = Backend("192.168.0.225", 12345)
game = Game()
create_maze()
pacman = Pacman(30, 30, PACMAN_SIZE, YELLOW, 2)
ghost = Ghost(90, 30, PACMAN_SIZE, RED, 2)

def pacman_send():
    header = "pacman-coordinates"
    payload = tuple(pacman.rect[:2])
    backend.send(header, payload)

def ghost_send():
    header = "ghost-coordinates"
    payload = tuple(ghost.rect[:2])
    backend.send(header, payload)

def update_other_coordinates():
    packet = backend.receive()
    
    if packet:
        header = packet[0]
        payload = packet[1]

        #Update coordinates of the uncontrolled character
        if header == "pacman-coordinates":
            pacman.rect[:2] = payload
            pacman.pellet_checker()
        
        elif header == "ghost-coordinates":
            ghost.rect[:2] = payload

clock = pygame.time.Clock()                                     # Create a Clock object
FPS = 60                                                        # The framerate constant

inp = input("p for pacman, g for ghost: ")

if inp == "p":
    controlling_pacman = True
else:
    controlling_pacman = False
print(controlling_pacman)

# Game loop
while True:
    clock.tick(FPS)                                             # Set the max FPS to 60
    if controlling_pacman:
        pacman.main()                                           # Update Pacman
        pacman_send()
    else:
        ghost.main()                                            # Update Ghost
        ghost_send()
    
    update_other_coordinates()
    
    game.main()                                                 # Update the screen
