import pygame

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
        self.__dx = 0
        self.__dy = 0
        self.__speed = speed
    
    def __move(self):
        keys = pygame.key.get_pressed()                         # Get array of key-states
        
        if keys[pygame.K_LEFT]:                                 # Left arrow press
            self.__dx = -self.__speed

        elif keys[pygame.K_RIGHT]:                              # Right arrow press
            self.__dx = self.__speed

        elif keys[pygame.K_UP]:                                 # Up arrow press
            self.__dy = -self.__speed

        elif keys[pygame.K_DOWN]:                               # Down arrow press
            self.__dy = self.__speed

        # Update coordinates
        self.rect.x += self.__dx
        self.rect.y += self.__dy

    def __wall_collision_checker(self):
        # Get an array of wall objects that have collided with the sprite.
        collided_walls = pygame.sprite.spritecollide(self, Wall.wall_group, False)

        if collided_walls:
            # This is the amount of pixels that the sprite could go into the wall in one frame
            tolerance = self.__speed

            for wall in collided_walls:

                top_diff = self.rect.top - wall.rect.bottom
                bottom_diff = self.rect.bottom - wall.rect.top
                left_diff = self.rect.left - wall.rect.right
                right_diff = self.rect.right - wall.rect.left

                if abs(top_diff) == tolerance:                  # Moved upwards into the wall
                    self.__dy = 0
                    self.rect.y -= top_diff

                if abs(bottom_diff) == tolerance:               # Moved downwards into the wall
                    self.__dy = 0
                    self.rect.y -= bottom_diff


                if abs(left_diff) == tolerance:                 # Moved leftwards into the wall
                    self.__dx = 0
                    self.rect.x -= left_diff

                if abs(right_diff) == tolerance:                # Moved rightwards into the wall
                    self.__dx = 0
                    self.rect.x -= right_diff
    
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
        self.__wall_collision_checker()


class Pacman(Playable):

    pacman_group = pygame.sprite.Group()

    def __init__(self, x, y, size: tuple, color: tuple, speed: int):
        super().__init__(x, y, size, color, speed)              # Create a playable object
        self.score = 0                                          # Set the default score

    def _add_to_groups(self):
        super()._add_to_groups()                                # Add to the collective container
        Pacman.pacman_group.add(self)                           # Add to the pacman container
    
    def __pellet_checker(self):
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
        self.__pellet_checker()


class Ghost(Playable):
    ghost_group = pygame.sprite.Group()

    def __init__(self, x, y, size: tuple, color: tuple, speed: int):
        super().__init__(x, y, size, color, speed)
    
    def _add_to_groups(self):
        super()._add_to_groups()
        Ghost.ghost_group.add(self)

    def main(self):
        super().main()


game = Game()
pacman = Pacman(30, 30, PACMAN_SIZE, YELLOW, 2)

# Place wall objects on the screen
Wall(0, 0, (420, 30), BLACK)
Wall(0, 0, (30, 70), BLACK)
Wall(0, 60, (390, 30), BLACK)

# Place pellet objects in a line. One per grid.
[Pellet(i, 40, PELLET_SIZE, ORANGE) for i in range(40, 420, SIZE)]

clock = pygame.time.Clock()                                     # Create a Clock object
FPS = 60                                                        # The framerate constant

# Game loop
while True:
    clock.tick(FPS)                                             # Set the max FPS to 60
    pacman.main()                                               # Update Pacman
    game.main()                                                 # Update the screen
