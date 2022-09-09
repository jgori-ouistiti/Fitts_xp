from tkinter import Widget
import colors as Colors
import sys
sys.path.append('../class')
from experiment import *
import webExtractor as webEx
import random
from gameExperiment import *
from makeExperiments import *

def readFileExperiment(filename, width, height, title = None, fullscreen = True):
    f = open(filename, "r")
    
    if title == None:
        title = "Experiment file : "+filename

    list_experiences = []
    list_random_experiences = []
    listTimePause = dict()
    nbExperience = 0

    lines = f.readlines()

    # gerener les experiences et les pauses
    lines = lines[0:]
    
    default_cursor = True
    cursor = SensitiveCursor(width, height, cursorImage = 'class/cursor/cursor1.png', dx_sens = 3, dy_sens = 3, sens_type = 'adaptive') 
    cursor_used = cursor
    
    device_used = None
    
    isRandom = False #If set to True, all next experiments will appear in a random order until set to False or end of file

    noPause = False #If set to False : make a pause between two experiments

    for line in lines:
        if line.startswith("pause"):
            elements = line.split(":")
            timePause = int(elements[1].strip("\n"))  # time of pause between 2 experiences
            listTimePause[nbExperience] = timePause
            
        elif line.startswith("cursor"):
            elements = line.split(" ")
            if 'os' in elements[1].lower():
                default_cursor = False
                cursor_used = None
            elif 'virtual' in elements[1].lower():
                default_cursor = False
                cursor_used = cursor
            elif 'default' in elements[1].lower():
                default_cursor = True
                cursor_used = None
                
        elif line.startswith("device"):
            elements = line.split(" ")
            if 'mouse' in elements[1].lower():
                device_used = 'mouse'
                default_cursor = True
            elif 'controller' in elements[1].lower():
                device_used = 'controller'
                default_cursor = False
                cursor_used = cursor
                
            elif 'touchpad' in elements[1].lower():
                device_used = 'touchpad'
                default_cursor = True
            elif 'stylus' in elements[1].lower():
                device_used = 'stylus'
                default_cursor = True
            elif 'default' in elements[1].lower():
                device_used = None
                default_cursor = True
        
        elif line.startswith("noPause"):
            elements = line.split(" ")
            if 'true' in elements[1].lower():
                noPause = True
            elif 'false' in elements[1].lower():
                noPause = False
                
        elif line.startswith("random"):
            elements = line.split(" ")
            if 'true' in elements[1].lower():
                isRandom = True
            elif 'false' in elements[1].lower():
                random.shuffle(list_random_experiences)
                list_experiences += list_random_experiences
                list_random_experiences = []
                isRandom = False

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
                if isRandom:
                    list_random_experiences.append(experiment)
                else:
                    list_experiences.append(Experiment(targets, exp_name, exp_id, nbMouv, cursor = cursor_used, noPause = noPause, default_cursor = default_cursor, input_device = device_used))

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
                        if isRandom:
                            list_random_experiences.append(experiment)
                        else:
                            list_experiences.append(Experiment(targets, type_cible, exp_id, nbMouv, noPause = noPause))
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
                    if isRandom:
                        list_random_experiences.append(experiment)
                    else:
                        list_experiences.append(Experiment(targets, disposition, exp_id, nbMouv, cursor = cursor_used, noPause = noPause, default_cursor = default_cursor, input_device = device_used))
                    
            elif type_experience == 'random':
                #Distance
                if parameters[2][0] == '[':
                    tmp = parameters[2].strip('[]')
                    tmp = tmp.split(',')
                    distance = list(map(lambda x : int(x), tmp))
                else:
                    distance = int(parameters[2])
                #Radius
                if parameters[3][0] == '[':
                    tmp = parameters[3].strip('[]')
                    tmp = tmp.split(',')
                    radius = list(map(lambda x : int(x), tmp))
                else:
                    radius = int(parameters[3])
                nb_mouvement = int(parameters[4])
                experiment = CircleRandomExp(width, height, 
                        'Random with W = '+str(radius)+', distance = '+str(distance), 
                        exp_id = exp_id, maxTrials = nb_mouvement, target_radius = radius, distance = distance, dx_sens = 1, dy_sens = 1, target_color = Colors.RED, buffer = 30, cursor = cursor_used, noPause = noPause, default_cursor = default_cursor, input_device = device_used)
                if isRandom:
                    list_random_experiences.append(experiment)
                else:
                    list_experiences.append(experiment)
                
            elif type_experience == 'lineV':
                #Distance
                if parameters[2][0] == '[':
                    tmp = parameters[2].strip('[]')
                    tmp = tmp.split(',')
                    distance = list(map(lambda x : int(x), tmp))
                else:
                    distance = int(parameters[2])
                #Radius
                if parameters[3][0] == '[':
                    tmp = parameters[3].strip('[]')
                    tmp = tmp.split(',')
                    radius = list(map(lambda x : int(x), tmp))
                else:
                    radius = int(parameters[3])
                nb_mouvement = int(parameters[4])
                experiment = TwoTargetsExp(width, height,
                        'Two Targets with W = '+str(radius)+', distance = '+str(distance)+', rad = PI/2',
                        math.pi/2,distance, target_radius = radius, maxTrials = nb_mouvement, exp_id = exp_id, cursor = cursor_used, noPause = noPause, default_cursor = default_cursor, input_device = device_used)
                if isRandom:
                    list_random_experiences.append(experiment)
                else:
                    list_experiences.append(experiment)
                
            elif type_experience == 'lineH':
                #Distance
                if parameters[2][0] == '[':
                    tmp = parameters[2].strip('[]')
                    tmp = tmp.split(',')
                    distance = list(map(lambda x : int(x), tmp))
                else:
                    distance = int(parameters[2])
                #Radius
                if parameters[3][0] == '[':
                    tmp = parameters[3].strip('[]')
                    tmp = tmp.split(',')
                    radius = list(map(lambda x : int(x), tmp))
                else:
                    radius = int(parameters[3])
                nb_mouvement = int(parameters[4])
                experiment = TwoTargetsExp(width, height,
                        'Two Targets with W = '+str(radius)+', distance = '+str(distance)+', rad = 0',
                        0,distance, target_radius = radius, maxTrials = nb_mouvement, exp_id = exp_id, cursor = cursor_used, noPause = noPause, default_cursor = default_cursor, input_device = device_used)
                if isRandom:
                    list_random_experiences.append(experiment)
                else:
                    list_experiences.append(experiment)
            
            elif type_experience == 'line':
                #Distance
                if parameters[2][0] == '[':
                    tmp = parameters[2].strip('[]')
                    tmp = tmp.split(',')
                    distance = list(map(lambda x : int(x), tmp))
                else:
                    distance = int(parameters[3])
                #Radius
                if parameters[3][0] == '[':
                    tmp = parameters[3].strip('[]')
                    tmp = tmp.split(',')
                    radius = list(map(lambda x : int(x), tmp))
                else:
                    radius = int(parameters[3])
                nb_mouvement = int(parameters[4])
                angle = int(parameters[5])
                experiment = TwoTargetsExp(width, height,
                        'Two Targets with W = '+str(radius)+', distance = '+str(distance)+', rad = '+str(angle),
                        angle,distance, target_radius = radius, maxTrials = nb_mouvement, exp_id = exp_id, cursor = cursor_used, noPause = noPause, default_cursor = default_cursor, input_device = device_used)
                if isRandom:
                    list_random_experiences.append(experiment)
                else:
                    list_experiences.append(experiment)
            
            elif type_experience == 'circleH':
                distance = int(int(parameters[2]))
                radius = int(parameters[3])
                nbCible = int(parameters[4])
                if nbCible %2 == 0: 
                    nbCible += 1
                experiment = CircleExp(width, height,
                        'Circle experiment with W = '+str(radius)+', distance = '+str(distance)+', nb_of_target = '+str(nbCible),
                        nbCible,distance, target_radius = radius, maxTrials = nbCible, way_H = True, exp_id = exp_id, cursor = cursor_used, noPause = noPause, default_cursor = default_cursor, input_device = device_used)
                if isRandom:
                    list_random_experiences.append(experiment)
                else:
                    list_experiences.append(experiment)
            
            elif type_experience == 'circleAH':
                distance = int(int(parameters[2]))
                radius = int(parameters[3])
                nbCible = int(parameters[4])
                if nbCible %2 == 0: 
                    nbCible += 1
                experiment = CircleExp(width, height,
                        'Circle experiment with W = '+str(radius)+', distance = '+str(distance)+', nb_of_target = '+str(nbCible),
                        nbCible,distance, target_radius = radius, maxTrials = nbCible, way_H = False, exp_id = exp_id, cursor = cursor_used, noPause = noPause, default_cursor = default_cursor, input_device = device_used)
                if isRandom:
                    list_random_experiences.append(experiment)
                else:
                    list_experiences.append(experiment)
                
            elif type_experience == 'circle':
                distance = int(int(parameters[2]))
                radius = int(parameters[3])
                nbCible = int(parameters[4])
                if nbCible %2 == 0: 
                    nbCible += 1
                is_H = True
                sens = parameters[5]
                if 'AH' in sens:
                    is_H = False
                experiment = CircleExp(width, height,
                        'Circle experiment with W = '+str(radius)+', distance = '+str(distance)+', nb_of_target = '+str(nbCible),
                        nbCible,distance, target_radius = radius, maxTrials = nbCible, way_H = is_H, exp_id = exp_id, cursor = cursor_used, noPause = noPause, default_cursor = default_cursor, input_device = device_used)
                if isRandom:
                    list_random_experiences.append(experiment)
                else:
                    list_experiences.append(experiment)
            nbExperience += 1
    f.close()
    if len(list_random_experiences) != 0:
        random.shuffle(list_random_experiences)
        list_experiences += list_random_experiences
    return GameExperiment(width, height, list_experiences, listTimePause, title = title, fullscreen = fullscreen)
