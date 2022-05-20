import sys
import os.path
from unittest.result import failfast
sys.path.append('./tools')
sys.path.append('./class')
from drawable import *
from gameExperiment import *
from cible import *
from target_disposition import *
from healthBar import *
from experiment import *
from generateModel import *
from sensitiveCursor import *
import webExtractor as webEx

import colors as Colors
import readFileExperiment as fonctions

def main():

    pygame.init()
    pygame.event.set_grab(True)
    
    #Get user's screen resolution
    infoObject = pygame.display.Info()
    WIDTH = infoObject.current_w - 200      ##on peut les ajouter dans config
    HEIGHT = infoObject.current_h - 200     ##on peut les ajouter dans config

    cursor = None
    bg_color = Colors.WHITE
    cursorImage = 'class/cursor/cursor3.png'

    running = True

    ### Permet creation d'une experience à partir d'un fichier
    filename = "experience.txt"
    game = fonctions.readFileExperiment(filename, WIDTH, HEIGHT)
    game.menu("chooseMode")

    ### Permet de manupiler les differents modes
    #game = Game(WIDTH, HEIGHT)
    #game.menu("chooseMode")
if __name__ == "__main__":
    main()
