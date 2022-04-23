import sys
sys.path.append('./tools')
sys.path.append('./class')
from drawable import *
from gameExperiment import *
from cible import *
from target_disposition import *
from healthBar import *
from experiment import *
import webExtractor as webEx
import colors as Colors

URLS = {"moodle":"https://moodle-sciences.upmc.fr/moodle-2021/",\
        "wikipedia":"https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Accueil_principal",\
        "google_search":"https://www.google.com/search?channel=fs&client=ubuntu&q=wikipedia",\
        "amazon":"https://www.amazon.fr/gp/bestsellers/?ref_=nav_cs_bestsellers",\
        "youtube":"https://www.youtube.com/",\
        "bnp":"https://mabanque.bnpparibas/"}

def getURL(i):
    if not sys.argv[i] in URLS.keys():
        raise Exception(sys.argv[i] + " not found in the url examples")
    return URLS[sys.argv[i]]

def main():

    pygame.init()
    
    #Get user's screen resolution
    infoObject = pygame.display.Info()
    WIDTH = infoObject.current_w - 200
    HEIGHT = infoObject.current_h - 200
    
    Targets = None
    for i in range(len(sys.argv)):
        if sys.argv[i] == '--example':
            URL = getURL(i+1)
            #Generating targets with URL
            Targets = webEx.getTargetsFromUrl(URL, WIDTH, HEIGHT, displayInfo = True)
            break
        if sys.argv[i] == '--url':
            URL = sys.argv[i+1]
            Targets = webEx.getTargetsFromUrl(URL, WIDTH, HEIGHT, displayInfo = True)
            break
            
    #=-=-=-=-=-EXPERIMENT TEST=-=-=-=-=-
    experimentAmazon = Experiment(\
        webEx.getTargetsFromUrl(URLS["amazon"], WIDTH, HEIGHT, displayInfo = True), "Amazon experiment", 1, maxTrials = 5)
        
    experimentGoogle = Experiment(\
        webEx.getTargetsFromUrl(URLS["google_search"], WIDTH, HEIGHT, displayInfo = True), "Google search experiment", 2, maxTrials = 5)
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    game = GameExperiment(WIDTH, HEIGHT, [experimentAmazon, experimentGoogle])
    
    running = True
    
    game.listTarget = Targets
    
    game.menu("chooseMode")

if __name__ == "__main__":
    main()
