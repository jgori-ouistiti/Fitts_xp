import sys
import os.path
from os import walk
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
from makeExperiments import *
import webExtractor as webEx
import colors as Colors
import pygame
import math

URLS = {"moodle":"https://moodle-sciences.upmc.fr/moodle-2021/",\
        #"wikipedia":"https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Accueil_principal",\
        #"google_search":"https://www.google.com/search?channel=fs&client=ubuntu&q=wikipedia",\
        #"amazon":"https://www.amazon.fr/gp/bestsellers/?ref_=nav_cs_bestsellers",\
        #"bnp":"https://mabanque.bnpparibas/"
        }

def getURL(i):
    if not sys.argv[i] in URLS.keys():
        raise Exception(sys.argv[i] + " not found in the url examples")
    return URLS[sys.argv[i]]

def main():

    pygame.init()
    pygame.event.set_grab(True)
    
    #Get user's screen resolution
    infoObject = pygame.display.Info()
    WIDTH = infoObject.current_w - 200
    HEIGHT = infoObject.current_h - 200
    
    model_filename = 'tools/models.pkl'
    experiments = None
    
    if not '--url' in sys.argv:
        if '--model' in sys.argv:
            if os.path.isfile(model_filename):
                experiments = readModel(model_filename, maxTrials = 10)
            else:
                experiments = generateModel(URLS, WIDTH, HEIGHT, filename = model_filename, maxTrials = 10)
                
        #-------Using a specific parameter for an experience will save on previous file corresponding to the experiment name-------
        elif '--random' in sys.argv:
            experiments = [CircleRandomExp(WIDTH, HEIGHT, 
                'Circle Random with r = 30, distance = 300', 
                0, maxTrials = 20, target_radius = 30, distance = 300,dx_sens = 1, dy_sens = 1, target_color = Colors.RED, buffer = 30)]
            saveExperiment(experiments[0], 'experiments\Random_R20_D300.pkl')
            
        elif '--lineH' in sys.argv:
            experiments = [TwoTargetsExp(WIDTH, HEIGHT,
                'Two Targets with r = 30, distance = 500, rad = 0',
                0,500, target_radius = 30)]
            saveExperiment(experiments[0], 'experiments\HorizontalTwoTargets_R30_D500.pkl')
            
        elif '--lineV' in sys.argv:
            experiments = [TwoTargetsExp(WIDTH, HEIGHT,
                'Two Targets with r = 30, distance = 500, rad = PI/2',
                math.pi/2,500, target_radius = 30)]
            saveExperiment(experiments[0], 'experiments\VerticalTwoTargets_R30_D500.pkl')
            
        elif '--circleH' in sys.argv:
            experiments = [CircleExp(WIDTH, HEIGHT,
                'Two Targets with r = 30, distance = 500, nb_of_target = 25',
                25,200, target_radius = 30, maxTrials = 26, way_H = True)]
            saveExperiment(experiments[0], 'experiments\Circle_R30_D200_N25_H.pkl')
            
        elif '--circleAH' in sys.argv:
            experiments = [CircleExp(WIDTH, HEIGHT,
                'Two Targets with r = 30, distance = 500, nb_of_target = 25',
                25,200, target_radius = 30, maxTrials = 26, way_H = False)]
            saveExperiment(experiments[0], 'experiments\Circle_R30_D200_N25_AH.pkl')
            
        #--------------------------------------------------------------------------------------------------------------------------
        #DEFAULT LOAD ALL THE EXPERIMENTS IN FOLDER '\experiment'
        else:
            filenames = next(walk("experiments/"), (None, None, []))[2]  # [] if no file
            print(filenames)
            experiments = []
            for file in filenames:
                if file[-4:] == '.pkl':
                    experiments.append(loadExperiment('experiments/'+file))
            
    
    else:
        for i in range(len(sys.argv)):
            if sys.argv[i] == '--url':
                URL = sys.argv[i+1]
                experiments = [Experiment(\
                    webEx.getTargetsFromUrl(URL, WIDTH, HEIGHT, displayInfo = True), "url", 0, maxTrials = 5)]
                break
                
    #Add experiments
            
    #=-=-=-=-=-EXPERIMENT TEST=-=-=-=-=-
    #experimentAmazon = Experiment(\
    #    webEx.getTargetsFromUrl(URLS["amazon"], WIDTH, HEIGHT, displayInfo = True), "Amazon experiment", 1, maxTrials = 5)
        
    #experimentGoogle = Experiment(\
    #    webEx.getTargetsFromUrl(URLS["google_search"], WIDTH, HEIGHT, displayInfo = True), "Google search experiment", 2, maxTrials = 5)
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    
    #Change the sensibility for the first experiment (TEST)
    #experiments[0].set_x_sensibility(-1)
    
    game = GameExperiment(WIDTH, HEIGHT, experiments, title='Fitts 2.O')
    
    
    running = True
 
    game.menu("chooseLanguage")

if __name__ == "__main__":
    main()
