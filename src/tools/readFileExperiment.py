import colors as Colors
import sys
sys.path.append('../class')
from experiment import *
import webExtractor as webEx
from gameExperiment import *


def readFileExperiment(filename, WIDTH, HEIGHT):
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
    return GameExperiment(WIDTH, HEIGHT, list_experiences)