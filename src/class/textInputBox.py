import sys
sys.path.append('./tools')
import pygame
import colors as Colors
from button import *

"""
Ce fichier permet de creer une page avec un input box de text, cad on peut ecrire dans l'interface
"""


class TextInputBox(pygame.sprite.Sprite):
    def __init__(self, pos, width, height, width_texte=400, height_texte=100, color=Colors.BLACK, bg_color=Colors.WHITE, bg_color_text = Colors.LIGHT_BLUE):
        super().__init__()
        self.width = width
        self.height = height
        self.pos = pos

        self.color = color
        self.bg_color = bg_color
        self.bg_color_text = bg_color_text
        
        self.width_texte = width_texte
        self.height_texte = height_texte
        self.image = None
        self.active = False
        self.text = ""
        self.rect = None
        self.button_ok = Button((int(pos[0]-220),int(self.pos[1])), 1, 200, 60 , (200, 50, 50), Colors.RED, "Ok")
        self.have_name = False

    def set_text(self, mot = "", have_name = True):
        """
            Remplace le text par mot
        """
        self.text = mot
        #self.have_name = have_name

    def render_text(self, font):
        texte = font.render(self.text, True, self.color, self.bg_color_text)
        self.width_texte = max(self.width_texte, texte.get_width()+10)
        self.height_texte = max(self.height_texte, texte.get_height()+10)
        self.image = pygame.Surface((self.width_texte, self.height_texte), pygame.SRCALPHA)
        self.image.fill(self.bg_color_text)
        self.image.blit(texte, (5, 2))
        pygame.draw.rect(self.image, self.color, self.image.get_rect().inflate(-5, -5), 2) 
        self.rect = self.image.get_rect(topleft = self.pos)

    def update(self,game, event_list, phrase = ""):
        #if self.have_name == False :
        #    phrase = self.font.render("Veuillez mettre votre nom", True, Colors.BLACK)
        #else : 
        #    phrase = self.font.render("Veuillez mettre votre prenom", True, Colors.BLACK)

        phrase_interface = game.font.render(phrase, True, Colors.BLACK)
        game.screen.blit(phrase_interface,(self.pos[0]-40, self.pos[1]-50))
        
        self.button_ok.draw(game)

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:    
                if (self.button_ok.isInside(pygame.mouse.get_pos())):
                    phrase_interface = game.font.render("Thank You !", True, Colors.BLACK)
                    game.screen.blit(phrase_interface,(self.pos[0]-230, self.pos[1]+60))
                    pygame.display.flip()
                    self.active = False
            if event.type == pygame.KEYDOWN : 
                if event.key == pygame.K_RETURN:
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_RETURN:
                    self.text = self.text
                else:
                    self.text += event.unicode

            self.render_text(game.font)
            
            