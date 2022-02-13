import sys
sys.path.append('./tools')
sys.path.append('./class')
from drawable import *
from game import *
from cible import *
from target_disposition import *
from healthBar import *

def main():
	game = Game(600, 300)
	running = True
	cible = Cible((300,50), 10, (255,0,0))
	game.addListenerDrawable(make_circle_target_list((300,150), 100, 10, (255,0,0), 20))
	game.menu("chooseMode")
	
if __name__ == "__main__":
	main()
