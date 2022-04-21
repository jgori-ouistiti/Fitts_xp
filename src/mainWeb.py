import sys
sys.path.append('./tools')
sys.path.append('./class')
from drawable import *
from game import *
from cible import *
from target_disposition import *
from healthBar import *
import webExtractor as webEx
import colors as Colors

URL = "https://moodle-sciences.upmc.fr/moodle-2021/"

def main():
    pygame.init()
    infoObject = pygame.display.Info()
    WIDTH = infoObject.current_w - 200
    HEIGHT = infoObject.current_h - 200
    game = Game(WIDTH, HEIGHT)
    running = True
    
    #Generating targets with URL
    game.listTarget = webEx.getTargetsFromUrl(URL, WIDTH, HEIGHT, displayInfo = True)
    
    game.infiniteTime = True
    
    game.menu("chooseMode")

if __name__ == "__main__":
    main()
