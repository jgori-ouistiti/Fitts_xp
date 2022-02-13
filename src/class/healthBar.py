import pygame
from drawable import *


class HealthBar(Drawable):
    def __init__(self, timer, longueur = 200, largeur=30, posRect=(115, 75), posText = (60,90), textColor = (0,0,0)):
    
        if not isinstance(posRect[0], int):
            raise Exception("x is not an int")
        if not isinstance(posRect[1], int):
            raise Exception("y is not an int")
        self.pos = posRect
        
        self.timer = timer
        self.maxtime = timer
        self.maxlongueur = longueur
        self.longueur = longueur
        life_color = min(int( (self.timer/self.longueur)*255) ,255)
        if life_color < 0:
            life_color = 0
        self.color = (255 - life_color, life_color, 0) 
        self.largeur = largeur
        
        self.text = "TIME"
        self.posText = posText
         

        self.font = pygame.font.SysFont('Corbel',35)
        self.text_render = self.font.render(self.text , True , textColor)
        

    def addSubTime(self, timer):
        self.timer += timer
        if self.timer > self.maxtime:
            self.timer = self.maxtime
       	
        if self.timer >= 0:
            life_color = min(int( (self.timer/self.maxtime)*255) ,255) #level of red = 255 - level of green 
        else : 
            life_color = 0 #temps est negatif donc il n'y a plu de temps donc la barre est rouge
        self.color = (255 - life_color, life_color, 0)
        self.longueur = int(self.timer/self.maxtime * self.maxlongueur)

        
        #text = pygame.font.SysFont("aerial", 60).render(self.longueur, True, (0, 0, 0))
        #text_rect = text.get_rect(center=self.posText)#position_text
        #game.screen.blit(text, text_rect)
        
    def setTime(self, time):
        self.timer = time


    def draw(self, game):
        x, y = self.pos
        dimension = (x, y, self.longueur, self.largeur)
        pygame.draw.rect(game.screen, self.color, dimension )
