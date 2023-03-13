import pygame

# RGB colour constants
RED     = (255,   0,   0)
ORANGE  = (255, 165,   0)
YELLOW  = (255, 255,   0)
GREEN   = (  0, 255,   0)
BLUE    = (  0,   0, 255)
BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)
BACKGROUND_COLOR = BLUE

# Menu constants
FONT = "Arial"

class Text():
    def __init__(self, x: int, y: int, text: str, size: int, background_color=BACKGROUND_COLOR):
        self.x, self.y, self.size, self.background_colour = x, y, size, background_color
        self.text = text
        self.font = pygame.font.SysFont(FONT, size)
    
    def update(self, target_surface):
        self.text_surface = self.font.render(self.text, True, YELLOW)
        self.rect = pygame.Rect(self.x, self.y, self.text_surface.get_width(), self.text_surface.get_height())
        self.background = pygame.Surface((self.text_surface.get_size()))
        self.background.fill(self.background_colour)

        # Blit the background to the surface.
        target_surface.blit(self.background, (self.x, self.y))
        # Blit the text on top of the background on the surface.
        target_surface.blit(self.text_surface, (self.x, self.y))


class Button(Text):
    def __init__(self, x: int, y: int, text: str, size: int, background_color: tuple):
        super().__init__(x, y, text, size, background_color)
        self.active = False
    
    def update(self, target_surface):        
        super().update(target_surface)
        # Give the button a yellow border
        pygame.draw.rect(target_surface, YELLOW, self.rect, 2)


class Input(Text):
    def __init__(self, x: int, y: int, size: int):
        super().__init__(x, y, "", size)
    
    def handle_input(self, event):
        if event.key == pygame.K_BACKSPACE:
            # Delete the last character
            self.text = self.text[:-1]
        
        elif event.type == pygame.KEYDOWN:
            # Alphanumeric key input and full stop
            if event.unicode.isalnum() or event.unicode == ".":
                self.text += event.unicode
        
        else:
            # Don't accept any other keys
            pass


class Page():
    current_page = 0
    def __init__(self):
        self.widgets = []
    
    def update(self, target_surface):
        target_surface.fill(BACKGROUND_COLOR)
        for widget in self.widgets:
            widget.update(target_surface)

    def next_page(self):
        Page.current_page += 1
    
    def change_page(self, number):
        Page.current_page = number

    def event_handler(self, event):
        pass