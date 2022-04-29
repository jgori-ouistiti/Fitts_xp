import sys
import os.path
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
        if os.path.isfile(model_filename):
            experiments = readModel(model_filename, maxTrials = 10)
        else:
            experiments = generateModel(URLS, WIDTH, HEIGHT, filename = model_filename, maxTrials = 10)
    
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
    experiments[0].set_x_sensibility(-1)
    
    game = GameExperiment(WIDTH, HEIGHT, experiments)
    
    
    running = True
 
    game.menu("chooseMode")

if __name__ == "__main__":
    main()
