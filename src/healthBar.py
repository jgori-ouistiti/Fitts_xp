import pygame
#from button import *


class HealthBar():
    def __init__(self, timer, largeur=30, posRect=(115, 75), posText = (60,90), textColor = (0,0,0)):
    
        if not isinstance(posRect[0], int):
            raise Exception("x is not an int")
        if not isinstance(posRect[1], int):
            raise Exception("y is not an int")
        self.pos = posRect
        
        self.longueur = timer
        self.largeur = largeur
        
        self.text = "TIME"
        self.posText = posText

        self.font = pygame.font.SysFont('Corbel',35)
        self.text_render = self.font.render(self.text , True , textColor)
        

    def refresh_barre_time(self, game):
        if self.longueur >= 0:
            life_color = min(int( (self.longueur/5)*255) ,255) #level of red = 255 - level of green 
        else : 
            life_color = 0 #temps est negatif donc il n'y a plu de temps donc la barre est rouge
        self.drawRect(game, (255 - life_color,life_color,0))

        #text = pygame.font.SysFont("aerial", 60).render(self.longueur, True, (0, 0, 0))
        #text_rect = text.get_rect(center=self.posText)#position_text
        #game.screen.blit(text, text_rect)


    def drawRect(self, game, color):
        # pos = (int, int)
        # dimension = ( pos, longueur, largeur )
        x, y = self.pos
        dimension = (x, y, self.longueur, self.largeur)
        pygame.draw.rect(game.screen, color, dimension )