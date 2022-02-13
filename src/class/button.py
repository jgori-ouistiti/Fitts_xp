from turtle import width
from drawable import *
from listener import *
import pygame

class Button(Drawable, Listener):
    def __init__(self, pos, mode, width, height, color, selectedColor, text = "", textColor = (0,0,0) ):
    
        self.checkPosType(pos)
        self.pos = pos
        
        if not isinstance(mode, int):
            raise Exception("mode must be of type int")
        self.mode = mode 
        
        if not isinstance(width, int):
            raise Exception("width must be of type int")
        self.width = width
        
        if not isinstance(height, int):
            raise Exception("height must be of type int")
        self.height = height
        
        self.checkColorType(color)
        self.color = color
        
        self.checkColorType(selectedColor)
        self.selectedColor = selectedColor
        
        self.activeColor = self.color
        self.isSelected = False
        self.font = pygame.font.SysFont('Corbel',35)
        self.text = text
        self.text_render = self.font.render(text , True , textColor)
        
    def setFont(self, font):
        self.font = font
        self.setText(self.text)
        
    def setText(self, text):
        self.text = text
        self.text_render = self.font.render(self.text , True , self.color)
           
    def isPosType(self, pos):
        if len(pos) != 2:
            return False
        if (not isinstance(pos[0], int)) or (not isinstance(pos[1], int)):
            return False
        if ((pos[0]<0) or (pos[1]<0) ) :
            return False
        return True
        
    def checkPosType(self, pos):
        if not self.isPosType(pos):
            raise Exception("pos must be of type (int, int)")
        
    def isColorType(self, color):
        if len(color) != 3:
            return False
        for i in range(3):
            if not isinstance(color[i], int):
                return False
            if (color[i] < 0) or (color[i] > 255):
                return False
        return True
        
    def checkColorType(self, color):
        if not self.isColorType(color):
            raise Exception("color must be between (0,0,0) and (255, 255, 255)") 
    
    def isInside(self, cursorPos):
        xp = cursorPos[0] - self.pos[0]
        yp = cursorPos[1] - self.pos[1]
        largeur = int(self.width)
        longueur = int(self.height)
        return 0<=xp and xp <= largeur and 0<=yp and yp <= longueur
    

    def drawButton(self, game): 
        x, y = self.pos
        pygame.draw.rect(game.screen,self.color ,[x, y ,self.width ,self.height])

    def draw(self, cursorPos):
        self.checkPosType(cursorPos)
        
        xc, yc = cursorPos
        x, y = self.pos
        
        tmp_selected = True
        #if (xc - x < 0 or xc - x > self.width or yc - y < 0 or yc - y > self.height):
        if not self.isInside(cursorPos):
            tmp_selected = False
            
        self.isSelected = tmp_selected
        
        if self.isSelected:
            self.active_color = self.selectedColor
        else:
            self.active_color = self.color
            
        pygame.draw.rect(self.screen,self.active_color ,[x, y ,self.width ,self.height])
            
    def action(self, game):
        return self.__name__    
          
        
    
