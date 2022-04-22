from drawable import *
from listener import *
from cible import * 
from colors import *
import pygame

class CibleRect(Cible):
    def __init__(self, pos , width, height, color = BLACK, isTarget = False):
        if not isinstance(pos[0], int):
            raise Exception("x is not an int")
        if not isinstance(pos[1], int):
            raise Exception("y is not an int")
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
        self.width = width
        self.height = height
        self.color = color
        self.isTarget = isTarget

    def isInside(self, coord):
        xp = coord[0] - self.x
        yp = coord[1] - self.y
        return xp > 0 and yp > 0 and xp < self.width and yp < self.height
        
    def draw(self, game):
        if self.isTarget :
            pygame.draw.rect(game.screen, RED , pygame.Rect(self.x,self.y,self.width,self.height))
        else:
            pygame.draw.rect(game.screen, self.color, pygame.Rect(self.x,self.y,self.width,self.height),2)
        



        
