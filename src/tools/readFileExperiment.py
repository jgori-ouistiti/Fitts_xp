from tkinter import Widget
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

    for experience in lines:
        parameters = experience.split(" ")
        print(parameters)
        
        exp_id = parameters[0] 
        type_experience = parameters[1] 

        if type_experience == 'url':
            exp_name = parameters[2]   
            targets = webEx.getTargetsFromUrl(exp_name, WIDTH, HEIGHT, color=Colors.BLACK, displayInfo=True)
            nbMouv = int(parameters[3].strip("\n"))
            list_experiences.append(Experiment(targets, exp_name, exp_id, nbMouv))

        elif type_experience == 'cible': 
            disposition = parameters[2]     #diposition c'est soit "cercle" soit "densite"
            
            ## Disposition est en cercle
            if disposition == "cercle": 
                type_cible = parameters[3]
                if type_cible == "cercle":  
                    rayon_D = int(parameters[4])        #correspond au rayon pour la disposition en cercle
                    rayon_cercle = int(parameters[5])   #correspond au rayon d'une cible
                    nbCible = int(parameters[6])
                    pos = parameters[7]
                    i = 7
                    if pos[0]=="(":
                        pos = pos.strip("(),")
                        pos = (int(pos[0]),int(pos[1]))
                        i = 8
                    else : 
                        pos = (WIDTH/2, HEIGHT/2)             
                    targets = make_circle_target_list(pos, rayon_D, nbCible, Colors.GREEN, rayon_cercle)
                    
                    nbMouv = int(parameters[i].strip("\n"))
                    list_experiences.append(Experiment(targets, type_cible, exp_id, nbMouv))
                #elif type_cible=="rect":

            ## Disposition est en densite
            elif disposition == "densite":
                dimensions = (WIDTH, HEIGHT)

                center = parameters[3]
                center = center.strip("(),")
                center = (int(center[0]),int(center[1]))

                ID = int(parameters[4])
                A  = int(parameters[5])
                p  = float(parameters[6])
                jmax = int(parameters[7])
                targets = make_2D_distractor_target_list(dimensions, center, ID, A, p, Colors.BLACK, jmax)
                nbMouv = int(parameters[8].strip("\n"))
                list_experiences.append(Experiment(targets, disposition, exp_id, nbMouv))

    f.close()
    return GameExperiment(WIDTH, HEIGHT, list_experiences)