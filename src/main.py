import sys
sys.path.append('./tools')
sys.path.append('./class')
from drawable import *
from game import *
from cible import *
from target_disposition import *
from healthBar import *

def main():
	game = Game(800, 600)
	running = True
	game.addListenerDrawable(make_circle_target_list((400,300), 200, 10, (0,0,255), 50))
	game.menu("chooseMode")
	
if __name__ == "__main__":
	main()
