#- - - Different function use to initate target's disposition, size, etc ... 
import sys
sys.path.append('../class')
import math
import pygame
from cible import *

def drawCircle(pos, color, r):
	pygame.draw.circle(screen, color, pos, r)

def drawRect(color, longueur, largeur=30, pos=(115, 75), mot=""):
	""" les valeurs par default servent pour dessiner la barre de temps """
	# pos = (int, int)
		# dimension = ( pos, longueur, largeur )
	x = pos[0]
	y = pos[1]
	dimension = (x, y, longueur*10, largeur)
	pygame.draw.rect(screen, color, dimension )


def regular_circle(nb_of_target, t_color, t_size, play_circle, drawables):
	
	for t in play_circle["targets"]:
		del t
	play_circle["targets"] = []

	theta = 0
	delta_theta = 2*math.pi / nb_of_target
	x,y = play_circle["pos"] #Center of the play circle
	r = play_circle["radius"]
	for i in range(nb_of_target):
		pos = (int(x + r*math.cos(theta)), int(y + r*math.sin(theta)))
		cible = Cible(pos, t_size, t_color)
		play_circle["targets"].append(cible)
		drawables.append(cible)

		drawCircle(pos, t_color, t_size)
		theta += delta_theta
	assign_random_target()
	
def make_circle_target_list(pos, circle_r, nb_of_target, t_color, t_size):
	L = []
	delta_theta = 2*math.pi / nb_of_target
	x, y = pos
	theta = 0
	for i in range(nb_of_target):
		pos = (int(x + circle_r*math.cos(theta)), int(y + circle_r*math.sin(theta)))
		L.append(Cible(pos, t_size, t_color))
		theta += delta_theta
	return L
	
