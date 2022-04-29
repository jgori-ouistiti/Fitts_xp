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


def main():

    pygame.init()
    pygame.event.set_grab(True)
    
    #Get user's screen resolution
    infoObject = pygame.display.Info()
    WIDTH = infoObject.current_w - 200      ##on peut les ajouter dans config
    HEIGHT = infoObject.current_h - 200     ##on peut les ajouter dans config
    

    filename = "experience.txt"
    f = open(filename, "r")

    list_experiences = []
    lines = f.readlines()

    print("lines: ", lines)
    for experience in lines:
        parameters = experience.split(" ")
        print("=========")
        print(parameters)
        
        exp_id = parameters[0] 
        type_experience = parameters[1] 

        if type_experience == 'url':
            print("C'est URL :" )
            exp_name = parameters[2]   
            targets = webEx.getTargetsFromUrl(exp_name, WIDTH, HEIGHT, color=Colors.BLACK, displayInfo=True)
            print("target : ", targets)
            nbMouv = int(parameters[3].strip("\n"))
            print("Nb mouvement :", nbMouv)
            list_experiences.append(Experiment(targets, exp_name, exp_id, nbMouv))
            print("Experience ajouter !")

        print("=========")

    f.close()
    
    game = GameExperiment(WIDTH, HEIGHT, list_experiences)
    
    
    running = True
 
    game.menu("chooseMode")


if __name__ == "__main__":
    main()
