from drawable import *
from listener import *
import pygame

class Cible(Drawable, Listener):
    def __init__(self, pos , r, color, isTarget = False):
        if not isinstance(pos[0], int):
            raise Exception("x is not an int")
        if not isinstance(pos[1], int):
            raise Exception("y is not an int")
        if not isinstance(r, int):
            raise Exception("r is not an int")
        if len(color) != 3:
            raise Exception("color must be a tuple like (R,G,B)")
        for c in color:
            if not isinstance(c, int):
                raise Exception("color is not a tuple of int")
            if ((c<0) or (c>255)) :
                raise Exception("byte of color must be between 0 and 255")
        if not isinstance(isTarget, bool):
            raise Exception("isTarget must be a boolean")
        self.x = pos[0]
        self.y = pos[1]
        self.r = r
        self.color = color
        self.isTarget = isTarget

    def cliqued(self):
        if self.isTarget :
            self.isTarget = False
            return 0
        return 1

    def isInside(self, coord):
        xp = abs(coord[0] - self.x)
        yp = abs(coord[1] - self.y)
        return xp**2 + yp**2 < self.r**2

    def newColor(self, color):
        if len(color) != 3:
            raise Exception("color must be a tuple like (R,G,B)")
        for c in color:
            if not isinstance(c, int):
                raise Exception("color is not a tuple of int")
            if ((c<0) or (c>255)) :
                raise Exception("byte of color must be between 0 and 255")
        self.color = color
        
    def draw(self, game):
        if self.isTarget :
            pygame.draw.circle(game.screen, (255,0,0) , (self.x,self.y), self.r)
        else:
            pygame.draw.circle(game.screen, self.color, (self.x,self.y), self.r)
        
    def action(self, game, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.isInside(pygame.mouse.get_pos()):
                tmp = self.isTarget
                if (self.isTarget) :
                    game.score += 1
                    game.assignRandomTarget()
                else:
                    game.score -= 1
                return ("cible", tmp)



        
