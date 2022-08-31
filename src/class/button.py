from drawable import *
from listener import *
import gameExperiment as gE
import pygame

class Button(Drawable, Listener):
    def __init__(self, pos, mode, width, height, color, selectedColor, text = "", image = None, textColor = (0,0,0) ):
    
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
        
        self.active_color = self.color
        self.isSelected = False
        self.font = pygame.font.SysFont('Corbel',35)
        self.text = text
        self.text_render = self.font.render(text , True , textColor)
        
        #Image
        self.imagePath = image
        if image != None:
            self.buttonImage = pygame.image.load(image)
            self.buttonImage = pygame.transform.scale(self.buttonImage, (width, height))
        
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

    def draw(self, game):
        
        xc, yc = pygame.mouse.get_pos()
        x, y = self.pos
        
        tmp_selected = self.isSelected
        
        #if (xc - x < 0 or xc - x > self.width or yc - y < 0 or yc - y > self.height):
        if self.isInside(pygame.mouse.get_pos()):
            tmp_selected = False
        else:
            tmp_selected = True
        #Est-ce que la couleur doit changer ?
        if self.imagePath == None:
            if self.isSelected != tmp_selected : 
                self.isSelected = tmp_selected
                if self.isSelected:
                    self.active_color = self.selectedColor
                else:
                    self.active_color = self.color
             
            text_x = x + int(self.width/2)
            text_y = y + int(self.height/2)
            
            text_rect = self.text_render.get_rect(center=(text_x, text_y))
            
            pygame.draw.rect(game.screen,self.active_color ,[x, y ,self.width ,self.height])
            game.screen.blit(self.text_render, text_rect)
        else:
            game.screen.blit(self.buttonImage, (x, y))
        
            
    def action(self, game, event):
        if not isinstance(game, gE.GameExperiment): 
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.JOYBUTTONDOWN:    
                if (self.isInside(pygame.mouse.get_pos())):
                    return "button", self.mode   
        else: 
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.JOYBUTTONDOWN:    
                if (self.isInside(game.getCursorPos())):
                    return "button", self.mode 
          
        
    
