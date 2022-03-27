import sys
sys.path.append('./tools')
sys.path.append('./class')
from drawable import *
from game import *
from cible import *
from target_disposition import *
from healthBar import *
import colors as Colors

def main():
    pygame.init()
    infoObject = pygame.display.Info()
    WIDTH = infoObject.current_w - 200
    HEIGHT = infoObject.current_h - 200
    game = Game(WIDTH, HEIGHT)
    running = True
    #game.addListenerDrawable(make_circle_target_list((WIDTH/2,HEIGHT/2), HEIGHT/3, 10, Colors.DARK_GREEN, 90))
    #game.addListenerDrawable(make_2D_distractor_target_list((WIDTH,HEIGHT), (int(WIDTH/2), int(HEIGHT/2) ), 3, 40, 0.25, Colors.BLACK))
    #game.menu("chooseMode")
    game.addTest(3, "circle", make_circle_target_list((WIDTH/2,HEIGHT/2), HEIGHT/3, 10, Colors.DARK_GREEN, 90))
    game.addTest(3, "2D    ", make_2D_distractor_target_list((WIDTH,HEIGHT), (int(WIDTH/2), int(HEIGHT/2) ), 3, 40, 0.25, Colors.BLACK))
    game.menu("experiment")

if __name__ == "__main__":
    main()
