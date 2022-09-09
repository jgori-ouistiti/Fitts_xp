from drawable import *
from listener import *
import pygame

class Cursor(Drawable, Listener):
    def __init__(self, WIDTH, HEIGHT,cursorImage = 'class/cursor/cursor1.png', visible = True):
        self.x = WIDTH/2
        self.y = HEIGHT/2
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.visible = visible
        self.cursorImage = pygame.image.load(cursorImage)
        self.cursorImage = pygame.transform.scale(self.cursorImage, (26, 40))
        self.imagePath = cursorImage
        
    def move(self, dx, dy):
        if self.x + dx > 0 and self.x + dx < self.WIDTH:
            self.x += dx
        if self.y + dy > 0 and self.y + dy < self.HEIGHT:
            self.y += dy
            
    def setVisible(self,visible):
        self.visible = visible
        
    def draw(self, game):
        if not self.visible:
            return
        if self.imagePath == 'class/cursor/cursor3.png':
            game.screen.blit(self.cursorImage, (self.x - 25, self.y - 25))
        else:
            game.screen.blit(self.cursorImage, (self.x, self.y))
    
    def action(self, game, event):
        return 'clic'
