import pygame
import sys
import math
import random
sys.path.append('./class')
from cible import *
from button import *

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
        
# Mode :
MODE_SIMPLE = 1
MODE_MAX = 2

# Taille Rectangle pour les modes
LONGUEUR = 200
LARGEUR = 100

#game parameters
## mode simple
default_timer = 10.0 #timer default value when starting the 'game'
timer_bonus = 2.0 #add amount to timer when hitting a target
timer_miss  = -3.0 #remove amout to timer when missing a target
## mode maximise score 
limit_timer = 10.0 #qd limite d'une partie pour le jeu ou on maximise le score en peu de temps

def getpos():
    return pygame.mouse.get_pos()

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

def drawMode(rect):
    rect.draw(getpos())
    x, y = rect.pos
    x = int(x+100)
    y = int(y+50)
    write_screen(rect.text, True, BLUE, (x,y) )

def addTarget(color, length):
    pos = getpos()
    play_circle["targets"].append(Cible(pos, length, color))
    drawCircle(pos, color, length) 

def assign_random_target():

    global actual_target
    
    i = random.randint(0,len(play_circle["targets"]) - 1)
    t = play_circle["targets"][i]
    t.isTarget = True
    t.color = targets_color
    drawCircle((t.x, t.y), t.color, t.r)
    actual_target = t

def init_targets(nb_of_target, t_color, t_size):

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

#=========

def refresh_screen(aff_mode=False):
    screen.fill(BACKGROUND_COLOR)
    
    global drawables
    for d in drawables:
        if isinstance(d, Button) and aff_mode:
            #d.draw(getpos())
            drawMode(d)
        if isinstance(d, Cible) and aff_mode==False:
            drawCircle((d.x, d.y), d.color, d.r)   

def refresh_barre_time(time):
    if time >= 0:
        life_color = min(int( (time/5)*255) ,255) #level of red = 255 - level of green 
    else : 
        life_color = 0 #temps est negatif donc il n'y a plu de temps donc la barre est rouge
    drawRect((255 - life_color,life_color,0), time)
    text = my_font.render("Time", True, BLACK)
    text_rect = text.get_rect(center=(60,90))
    screen.blit(text, text_rect)

def write_screen(mot, booleen, color, dimension):
    text = my_font.render(mot, booleen, color)
    text_rect = text.get_rect(center=dimension)
    screen.blit(text, text_rect)

#======== 
def menu_principal(text, text_rect):
    if len(play_circle["targets"]) != 0:
        if play_circle["targets"][0] in drawables:
            for t in play_circle["targets"]:
                drawables.remove(t)
    refresh_screen()
    screen.blit(text, text_rect)

def choix_mode(List_button):
    print("Veuillez choisir un mode : ")
    print(MODE_SIMPLE , " : mode simple")
    print(MODE_MAX, " : mode maximiser score en un temps constant")
    #mode = int(input())
    mode = -1
    pos = getpos()
    for button in List_button:
        if button.isInside(pos):
            mode = button.mode
    return mode

def maj_score(): 
    """
        Retourne le temps et le point associee lorsqu'il appuie sur la map
    """
    global cursor_distances
    pos = getpos()
    hit = False
    for t in play_circle["targets"]:
        if t.isInside(pos): #verifie s'il est dans le cercle
            if (t.isTarget): #verifie si c'est dans le cercle du target
                hit = True
                t.newColor(not_targets_color)
                t.isTarget = False
                actual_target = assign_random_target()
                
                #saving the cursor path
                extraction_data.append(cursor_distances)
                cursor_distances = []
                
            #drawCircle((t.x, t.y), t.color, t.r)
    if hit: 
        # a bien viser dans la cible
        return timer_bonus, 1
    return timer_miss, -1

def end_game(alive_time = -1.0, score=0):
    pygame.time.set_timer(pygame.USEREVENT, 0)
    for t in play_circle["targets"]:
        del t
    play_circle["target"] = []
    screen.fill(BACKGROUND_COLOR)
    write_screen("Game over !", True, BLACK, (WIDTH/2, HEIGHT/2 - 200) )
    #text = my_font.render("Game over !", True, BLACK)
    #text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2 - 200))
    #screen.blit(text, text_rect)
    write_screen("Score : "+str(score), True, BLACK,(WIDTH/2, HEIGHT/2 - 100))
    #text = my_font.render("Score : "+str(score), True, BLACK)
    #text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2 - 100))
    #screen.blit(text, text_rect)
    if alive_time > 0 :
        text = my_font.render("You survived " + "{:.1f}".format(alive_time) + " seconds", True, BLACK)
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
        screen.blit(text, text_rect)
    write_screen("Press SPACE to retry !", True, BLACK,(WIDTH/2, HEIGHT/2 + 100))
    #text = my_font.render("Press SPACE to retry !", True, BLACK)
    #text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2 + 100))
    #screen.blit(text, text_rect)
    
    
    
#=========== Data retribution part ==============

def distance_to_target():
    x,y = getpos()
    distance = math.sqrt( (x-actual_target.x)**2 + (y-actual_target.y)**2)
    cursor_distances.append(distance)

def iter_data():
    extraction_data.add(cursor_distances)
    cursor_distances = []

def save_data_in_file(filename):
    f = open(filename, 'w')
    f.write(str(extraction_data))
    f.close()

#==============================================

def play(mode=MODE_SIMPLE):
    
    global running, screen, my_font, drawables
    timer = default_timer
    drawables = []
    
    global actual_target
    actual_target = None
    
    global extraction_data, cursor_distances #set of user's cursor distance of target when playing
    
    cursor_distances = []
    extraction_data = []
    
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

    play_button = Button((int(WIDTH/3), int(HEIGHT/2)), screen, MODE_SIMPLE,  LONGUEUR, LARGEUR, RED, BLACK, text="MODE_1")
    play_button2 = Button((int(WIDTH*2/3), int(HEIGHT/2)), screen, MODE_MAX, LONGUEUR, LARGEUR, GREEN, BLACK, text="MODE_2")

    drawables.append(play_button)
    drawables.append(play_button2)

    pygame.display.update()

    game_started = False
    
    menu = 0
    choix_fait = False
    mode = -1
    
    while running:
        ev = pygame.event.get()
        
        #if menu == 0:
        #    menu_principal(text, text_rect)

        for event in ev:
            
            if event.type == pygame.MOUSEBUTTONDOWN and game_started:
                temps, point = maj_score()
                if mode == MODE_SIMPLE:
                    timer += temps
                    score += point
                elif mode == MODE_MAX: 
                    if point>0:
                        score += point
                pygame.display.update()
                isReleased = False
            
            if event.type == pygame.MOUSEBUTTONUP:
                isReleased = True

            if isReleased == False:
                pygame.display.update()
      
            if event.type == pygame.USEREVENT:
                refresh_screen()

                # affiche la barre de temps
                refresh_barre_time(timer)
                
                #DATA FOR PROJECT
                distance_to_target()

                if mode==MODE_SIMPLE:
                    timer -= 0.01      
                    alive_time += 0.01
                elif mode==MODE_MAX:
                    timer -= 0.01


                write_screen("{:.1f}".format(timer), True, RED,(WIDTH/2 , HEIGHT/2))
                write_screen("Score : " + str(score), True, GREEN, (260,50))
                pygame.display.update()

                if timer<=0: # temps ecoule, fin de la partie
    
                    game_started = False
                    choix_fait=False
                    menu = 0
                    mode = -1
                    if score < 0:
                        score = 0
                    
                    end_game(alive_time, score)
                    drawables.append(play_button)
                    drawables.append(play_button2)
                    
                    pygame.display.update()
                    print("fin")
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t: # permet de creer des nouveaux target avec la touche T
                    addTarget(BLUE, targets_radius)
                    pygame.display.update()

                if event.key ==pygame.K_SPACE and choix_fait==True and game_started==False:
                    init_targets(targets_number, not_targets_color, targets_radius)
                    if menu == 0:
                        drawables.remove(play_button)
                        drawables.remove(play_button2)
                        refresh_screen()
                        pygame.display.update()
                        menu = 1
                    game_started = True 
                    alive_time = 0
                    score = 0

                    pygame.time.set_timer(pygame.USEREVENT, 10)
                    

                #elif event.key ==pygame.K_SPACE and game_started==False:
                #    choix_fait=False
                #    screen.fill(BACKGROUND_COLOR)
                #    drawables.append(play_button)
                #    refresh_screen(True)
                #    text = my_font.render("CHOOSE YOUR MODE",True, BLACK)
                #    text_rect = text.get_rect(center=(WIDTH/4, HEIGHT/4))
                #    screen.blit(text, text_rect)
                #    pygame.display.update()
                  
            if event.type == pygame.MOUSEBUTTONDOWN and game_started == False and choix_fait==False: 
                
                ##affiche les modes
                drawables.append(play_button)
                drawables.append(play_button2)
                refresh_screen(True)

                write_screen("CHOOSE YOUR MODE",True, BLACK,(WIDTH/3, HEIGHT/3))

                mode = choix_mode([play_button, play_button2]) 
                pygame.display.update()
                
                
                if mode==MODE_SIMPLE:
                    timer = default_timer
                    choix_fait=True
                elif mode==MODE_MAX:
                    timer = limit_timer
                    choix_fait=True
                print("choix fait, le mode : ", mode, choix_fait)
                print("jeu a commencer ? Reponse : ", game_started)

                if choix_fait==True:
                    screen.fill(BACKGROUND_COLOR)
                    text = my_font.render("WHEN YOU ARE READY, PRESS SPACE TO BEGIN", True, BLACK)
                    text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
                    screen.blit(text, text_rect)
                    pygame.display.update()
                
                
            if event.type == pygame.QUIT:
                running = False

    save_data_in_file("resultat.txt")

def main():
    print("Bienvenue au jeu des cibles")
    
    play()
    
    print("Fin de la game")
    
main()
