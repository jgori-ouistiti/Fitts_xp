from tkinter import Widget
import colors as Colors
import sys
sys.path.append('../class')
from experiment import *
import webExtractor as webEx
from gameExperiment import *
from makeExperiments import *

def readFileExperiment(filename, width, height, title = None):
    f = open(filename, "r")
    
    if title == None:
        title = "Experiment file : "+filename

    list_experiences = []
    listTimePause = dict()
    nbExperience = 0

    lines = f.readlines()

    # gerener les experiences et les pauses
    lines = lines[0:]

    for line in lines:
        if line.startswith("pause"):
            elements = line.split(":")
            timePause = int(elements[1].strip("\n"))  # time of pause between 2 experiences
            listTimePause[nbExperience] = timePause

        elif (line[0] == ';') or line[0] == '\n': #comment line
            continue 

        else:
            print(" -- Génération de l'experience n°", nbExperience)

            parameters = line.split(" ")

            exp_id = parameters[0]
            type_experience = parameters[1]

            if type_experience == 'url':
                exp_name = parameters[2]
                targets = webEx.getTargetsFromUrl(exp_name, width, height, color=Colors.BLACK, displayInfo=True)
                nbMouv = int(parameters[3].strip("\n"))
                list_experiences.append(Experiment(targets, exp_name, exp_id, nbMouv))

            elif type_experience == 'cible':
                disposition = parameters[2]  # diposition c'est soit "cercle" soit "densite"

                ## Disposition est en cercle
                if disposition == "cercle":
                    type_cible = parameters[3]
                    if type_cible == "cercle":
                        rayon_D = int(parameters[4])  # correspond au rayon pour la disposition en cercle
                        rayon_cercle = int(parameters[5])  # correspond au rayon d'une cible
                        nbCible = int(parameters[6])
                        pos = parameters[7]
                        i = 7
                        if pos[0] == "(":
                            pos = pos.strip("()")
                            pos = pos.split(",")
                            pos = (int(100/int(pos[0]) * width), int(100/int(pos[1]) * height))
                            i = 8
                        else:
                            pos = (width / 2, height / 2)
                        targets = make_circle_target_list(pos, rayon_D, nbCible, Colors.GREEN, rayon_cercle)

                        nbMouv = int(parameters[i].strip("\n"))
                        list_experiences.append(Experiment(targets, type_cible, exp_id, nbMouv))
                    # elif type_cible=="rect":

                ## Disposition est en densite
                elif disposition == "densite":
                    dimensions = (width, height)

                    center = parameters[3]
                    center = center.strip("()")
                    center = center.split(",")
                    center = (int(100/int(center[0]) * width), int(100/int(center[1]) * height))

                    ID = int(parameters[4])
                    A = int(parameters[5])
                    p = float(parameters[6])
                    jmax = int(parameters[7])
                    targets = make_2D_distractor_target_list(dimensions, center, ID, A, p, Colors.BLACK, jmax)
                    nbMouv = int(parameters[8].strip("\n"))
                    list_experiences.append(Experiment(targets, disposition, exp_id, nbMouv))
                    
            elif type_experience == 'random':
                distance = int(parameters[2])
                radius = int(parameters[3])
                nb_mouvement = int(parameters[4])
                experiment = CircleRandomExp(width, height, 
                        'Circle Random with r = '+str(radius)+', distance = '+str(distance), 
                        exp_id = exp_id, maxTrials = nb_mouvement, target_radius = radius, distance = distance, dx_sens = 1, dy_sens = 1, target_color = Colors.RED, buffer = 30)
                list_experiences.append(experiment)
                
            elif type_experience == 'lineV':
                distance = int(parameters[2])
                radius = int(parameters[3])
                nb_mouvement = int(parameters[4])
                experiment = TwoTargetsExp(width, height,
                        'Two Targets with r = '+str(radius)+', distance = '+str(distance)+'rad = PI/2',
                        math.pi/2,distance, target_radius = radius, maxTrials = nb_mouvement, exp_id = exp_id)
                list_experiences.append(experiment)
                
            elif type_experience == 'lineH':
                distance = int(parameters[2])
                radius = int(parameters[3])
                nb_mouvement = int(parameters[4])
                experiment = TwoTargetsExp(width, height,
                        'Two Targets with r = '+str(radius)+', distance = '+str(distance)+'rad = 0',
                        0,distance, target_radius = radius, maxTrials = nb_mouvement, exp_id = exp_id)
                list_experiences.append(experiment)
            
            elif type_experience == 'line':
                distance = int(parameters[2])
                radius = int(parameters[3])
                nb_mouvement = int(parameters[4])
                angle = int(parameters[5])
                experiment = TwoTargetsExp(width, height,
                        'Two Targets with r = '+str(radius)+', distance = '+str(distance)+'rad = '+str(angle),
                        angle,distance, target_radius = radius, maxTrials = nb_mouvement, exp_id = exp_id)
                list_experiences.append(experiment)
            
            elif type_experience == 'circleH':
                distance = int(parameters[2])
                radius = int(parameters[3])
                nbCible = int(parameters[4])
                if nbCible %2 == 0: 
                    nbCible += 1
                experiment = CircleExp(width, height,
                        'Two Targets with r = '+str(radius)+', distance = '+str(distance)+', nb_of_target = '+str(nbCible),
                        nbCible,distance, target_radius = radius, maxTrials = nbCible, way_H = True, exp_id = exp_id)
                list_experiences.append(experiment)
            
            elif type_experience == 'circleAH':
                distance = int(parameters[2])
                radius = int(parameters[3])
                nbCible = int(parameters[4])
                if nbCible %2 == 0: 
                    nbCible += 1
                experiment = CircleExp(width, height,
                        'Two Targets with r = '+str(radius)+', distance = '+str(distance)+', nb_of_target = '+str(nbCible),
                        nbCible,distance, target_radius = radius, maxTrials = nbCible, way_H = False, exp_id = exp_id)
                list_experiences.append(experiment)
                
            elif type_experience == 'circle':
                distance = int(parameters[2])
                radius = int(parameters[3])
                nbCible = int(parameters[4])
                if nbCible %2 == 0: 
                    nbCible += 1
                is_H = True
                sens = parameters[5]
                if 'AH' in sens:
                    is_H = False
                experiment = CircleExp(width, height,
                        'Two Targets with r = '+str(radius)+', distance = '+str(distance)+', nb_of_target = '+str(nbCible),
                        nbCible,distance, target_radius = radius, maxTrials = nbCible, way_H = is_H, exp_id = exp_id)
                list_experiences.append(experiment)
            nbExperience += 1
    f.close()
    return GameExperiment(width, height, list_experiences, listTimePause, title = title)