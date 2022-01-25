import pygame
import sys
import math
import random
sys.path.append('./class')
from cible import *

#window
WIDTH = 1080
HEIGHT = 920

#colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#screen
BACKGROUND_COLOR = WHITE

targets_radius = 60
targets_number = 10
not_targets_color = BLUE
targets_color = RED


#Targets spawn on an invisible circle
play_circle = {
        "radius" : 300,
        "pos" : (WIDTH/2, HEIGHT/2), #Center of the circle
        "targets" : [] #List of targets
        }
        
#game parameters
default_timer = 5.0 #timer default value when starting the 'game'
timer_bonus = 2.0 #add amount to timer when hitting a target
timer_miss  = -3.0 #remove amout to timer when missing a target

def getpos():
    return pygame.mouse.get_pos()

def drawCircle(pos, color, r):
    pygame.draw.circle(screen, color, pos, r)

def addTarget(color, length):
    pos = getpos()
    play_circle["targets"].append(Cible(pos, length, color))
    drawCircle(pos, color, length) 

def shoot():
    pos = getpos()
    hit = False
    for t in play_circle["targets"]:
        if t.isInside(pos):
            if (t.isTarget):
                hit = True
                t.newColor(not_targets_color)
                t.isTarget = False
                assign_random_target()
            drawCircle((t.x, t.y), t.color, t.r)
    if hit:
        return timer_bonus
    return timer_miss

def assign_random_target():
    i = random.randint(0,len(play_circle["targets"]) - 1)
    t = play_circle["targets"][i]
    t.isTarget = True
    t.color = targets_color
    drawCircle((t.x, t.y), t.color, t.r)

def init_targets(nb_of_target, t_color, t_size):
    theta = 0
    delta_theta = 2*math.pi / nb_of_target
    x,y = play_circle["pos"] #Center of the play circle
    r = play_circle["radius"]
    for i in range(nb_of_target):
        pos = (int(x + r*math.cos(theta)), int(y + r*math.sin(theta)))
        play_circle["targets"].append(Cible(pos, t_size, t_color))
        drawCircle(pos, t_color, t_size)
        theta += delta_theta
        
    assign_random_target()
    pygame.time.set_timer(pygame.USEREVENT, 100)
    
def refresh_screen():
    screen.fill(BACKGROUND_COLOR)
    for t in play_circle["targets"]:
        drawCircle((t.x, t.y), t.color, t.r)

def play():
    global running, screen
    global timer
    timer = default_timer
    pygame.init()
    my_font = pygame.font.SysFont("aerial", 60)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("TEST CIBLES")
    screen.fill(BACKGROUND_COLOR)
    pygame.display.update()
    running = True
    isReleased = True
    text = my_font.render("PRESS SPACE TO BEGIN", True, BLACK)
    text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
    screen.blit(text, text_rect)
    pygame.display.update()
    game_started = False
    while running:
        ev = pygame.event.get()

        for event in ev:
            
            if event.type == pygame.MOUSEBUTTONDOWN and game_started:
                timer += shoot()
                pygame.display.update()
                isReleased = False
            
            if event.type == pygame.MOUSEBUTTONUP:
                isReleased = True

            if isReleased == False:
                pygame.display.update()
      
            if event.type == pygame.USEREVENT:
                refresh_screen()
                timer -= 0.1      
                text = my_font.render("{:.1f}".format(timer), True, RED)
                text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
                screen.blit(text, text_rect)
                pygame.display.update()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    addTarget(BLUE, targets_radius)
                    pygame.display.update()
                      
                if event.key == pygame.K_SPACE:
                    screen.fill(BACKGROUND_COLOR)
                    for t in play_circle["targets"]:
                        del t
                    init_targets(targets_number, not_targets_color, targets_radius)
                    game_started = True
                    pygame.display.update()
            if event.type == pygame.QUIT:
                running = False
play()
