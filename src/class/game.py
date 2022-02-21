import sys
sys.path.append('../class')
from target_disposition import *
from turtle import pos
import pygame
import random
from drawable import *
from listener import *
from healthBar import *
from button import *
from colors import *

class Game :
    def __init__(self, width, height, bg_color = WHITE):
        self.font = pygame.font.SysFont("aerial", 60)
        self.screen    = pygame.display.set_mode((width, height))
        pygame.display.set_caption("TEST CIBLES")
        self.width     = width
        self.height    = height
        self.listener  = dict() #Key = Listener object, value = boolean (True if listening, False if not listening) 
        self.drawables = dict() #Key = Drawable object, value = boolean (True if is on screen, False if not )
        self.bg_color  = bg_color #background color
        self.running   = False
        self.barTime = HealthBar(5, posText=(110,100), posRect=(30,30))
        self.time = 100
        self.score = 0
        self.nb_target = 0
        self.target_radius = 0
        self.cursor_position = []
        self.cursor_position_list = []
        self.active_target = None
        
    def draw(self):
        for d, v in self.drawables.items():
            if v == True:
                d.draw(self)

    def refreshScreen(self, update = True):
        self.screen.fill(self.bg_color)
        self.draw()
        if update:
            pygame.display.update()
            
    def addDrawable(self, d):
        if (hasattr(d, "__len__")):
            for d_item in d:
                if isinstance(d_item, Drawable):
                    self.listener.append(d_item)
                else:
                    print("Warning : ",d_item," found but not drawable")
        elif (not isinstance(d, Drawable)):
            raise Exception("d is not drawable")
        else:
            self.drawables[d] = True
        
    def addListener(self, l):
        if isinstance(l, Cible):
            self.nb_target += 1
        if (hasattr(l, "__len__")):
            for l_item in l:
                if isinstance(l_item, Listener):
                    self.listener[l_item] = True
                else:
                    print("Warning : ",l_item," found but not a listener")
        elif (not isinstance(l, Listener)):
            raise Exception("l is not a listener")
        else:
            self.listener[l] = True
        
    def removeDrawable(self, d):
        if (hasattr(d, "__len__")):
            for d_item in d:
                if d_item in self.drawables.keys():
                    del self.drawables[d_item]
        elif d in self.drawables.keys():
            del self.drawables[d]
            
    def removeListener(self, l):
        if (hasattr(l, "__len__")):
            for l_item in l:
                if l_item in self.listener.keys():
                    if isinstance(l_item, Cible):
                        self.nb_target -= 1
                    del self.listener[l_item]
        elif l in self.listener.keys():
            if isinstance(l, Cible):
                self.nb_target -= 1
            del self.listener[l]
            
    def addListenerDrawable(self, ld):
        if (hasattr(ld, "__len__")):
            for ld_item in ld:
                if (not isinstance(ld_item, Drawable) or not isinstance(ld_item, Listener)):
                    print("Warning : ",l_item," found but not a listener or drawable")
                else:
                    if isinstance(ld_item, Cible):
                        self.nb_target += 1
                    self.drawables[ld_item] = True
                    self.listener[ld_item] = True
            return
        if (not isinstance(ld, Drawable) and not isinstance(ld, Listener)):
            raise Exception("ld is not a listener and not drawable")
        if (not isinstance(ld, Listener)):
            raise Exception("ld is not a listener")
        if (not isinstance(ld, Drawable)):
            raise Exception("ld is not drawable")
        if isinstance(ld, Cible):
            self.nb_target += 1
        self.drawables[ld] = True
        self.listener[ld] = True
        
    def removeListenerDrawable(self, ld):
        if (hasattr(ld, "__len__")):
            for item in ld:
                if item in self.drawables.keys() and item in self.listener.keys():
                    del self.drawables[item]
                    del self.listener[item]
        elif ld in self.drawables.keys() and ld in self.listener.keys():
            del self.drawables[ld]
            del self.listener[ld]
        else:
            raise Exception("ld not in listener drawable")

    def hideDrawable(self, d):
        self.drawables[d] = False
    
    def hideListener(self, l):
        self.listener[l] = False
        
    def hideListenerDrawable(self, ld):
        self.hideDrawable(ld)
        self.hideListener(ld)
        
    def hideAllDrawable(self):
        for d in self.drawables.keys():
            self.drawables[d] = False
            
    def hideAllListener(self):
        for l in self.listener.keys():
            self.listener[l] = False

    def showAllDrawable(self):
        for d in self.drawables.keys():
            self.drawables[d] = True
            
    def showAllListener(self):
        for l in self.listener.keys():
            self.listener[l] = True
            
    def listen(self, event):
        L = []
        for l, v in self.listener.items():
            if v:
                tmp = l.action(self,event)
                if tmp:
                    L.append(tmp)
        return L
        
    def assignRandomTarget(self):
        #Set one target the main target to hit
        new_target_id = random.randint(0,self.nb_target - 1)
        target = None
        i = 0
        for obj in self.listener.keys():
            if isinstance(obj, Cible):
                obj.isTarget = False
                if i == new_target_id:
                    obj.isTarget = True
                    self.active_target = obj
                    target = obj
                i += 1
        if target == None:
            raise Exception("Internal error, no target found...")
        
        
    def menu(self, menu_title, current_mode = 'play'):
        if menu_title == "play":
            if current_mode != "pause":
                self.barTime.maxtime = 5
                self.barTime.timer = 5
            self.play()
        if menu_title == "pause":
            self.hideAllDrawable()
            self.hideAllListener()
            self.pauseMenu(current_mode)
        if menu_title == "endGame":
            self.hideAllDrawable()
            self.hideAllListener()
            self.endGame()
        if menu_title == "chooseMode":
            self.hideAllDrawable()
            self.hideAllListener()
            self.chooseMode() 
        if menu_title == "quick":
            if current_mode != "pause":
                self.barTime.maxtime = 10
                self.barTime.timer = 10
            self.quickMode()
            
    def write_screen(self, mot,color, pos, booleen=True ):
        text = self.font.render(mot, booleen, color)
        text_rect = text.get_rect(center=pos)
        self.screen.blit(text, text_rect)
   
    def save_data_in_file(self, filename):
        f = open(filename, 'w')
        f.write("NB_TARGET " + str(self.nb_target) + "\n")
        f.write(str(self.cursor_position_list))
        f.close()
    
    def quitApp(self):
        self.save_data_in_file("resultat.txt")
        self.running = False
        
    def pauseMenu(self, current_mode):
        self.refreshScreen()
        self.write_screen("PAUSE", BLACK, (self.width/2, self.height/2 - 30))
        self.write_screen("Press ESCAPE to continue", BLACK, (self.width/2, self.height/2 + 30))
        self.running = True
        while(self.running):
            pygame.display.update()
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.QUIT:
                        self.quitApp()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.showAllDrawable()
                        self.showAllListener()
                        self.menu(current_mode,"pause")
                        
    

            
    def endGame(self):
        self.refreshScreen()
        self.write_screen("GAME OVER", BLACK, (self.width/2, self.height/2 - 50))
        self.write_screen("Your score : " + str(self.score), BLACK, (self.width/2, self.height/2))
        self.write_screen("Press ESCAPE to play again", BLACK, (self.width/2, self.height/2 + 50))
        self.running = True
        while(self.running):
            pygame.display.update()
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.QUIT:
                    self.quitApp()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.score = 0
                        self.barTime.setTime(5)
                        self.running = False
                        self.showAllDrawable()
                        self.showAllListener()
                        self.menu("chooseMode")
    
    def play(self):
        self.running = True
        self.assignRandomTarget()
        self.addDrawable(self.barTime)
        pygame.time.set_timer(pygame.USEREVENT, 10) #Active pygame.USEREVENT toute les 10ms 
        
        self.cursor_position = []
        self.cursor_position.append(("target_pos :",(self.active_target.x,self.active_target.y)))
        while (self.running):
            self.refreshScreen(False)
            
            #Display Timer
            self.write_screen("Time : " + "{:.1f}".format(self.barTime.timer), BLACK, self.barTime.posText, True)
            pygame.display.update()

            ev = pygame.event.get()
            
            
            for event in ev:
                L = self.listen(event)
                if event.type == pygame.QUIT:
                    self.quitApp()
                #Update Timer and collect mouse position
                if event.type == pygame.USEREVENT:
                    #Tracking mouse position
                    self.cursor_position.append(pygame.mouse.get_pos())
                    #Decrementing timer
                    self.barTime.addSubTime(-0.01)
                    if self.barTime.timer <= 0:
                        self.running = False
                        self.menu("endGame")
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.menu("pause")
                if ("cible",True) in L:#On a cliqué sur une cible
                    self.barTime.timer += 1
                    #Saving the tracking of mouse
                    self.cursor_position_list.append(self.cursor_position)
                    self.cursor_position = []
                    self.cursor_position.append(("target_pos :",(self.active_target.x,self.active_target.y)))
                    
    def quickMode(self):
        self.running = True
        self.assignRandomTarget()
        self.addDrawable(self.barTime)
        pygame.time.set_timer(pygame.USEREVENT, 10) #Active pygame.USEREVENT toute les 10ms 
        
        self.cursor_position = []
        self.cursor_position.append(("target_pos :",(self.active_target.x,self.active_target.y)))
        while (self.running):
            self.refreshScreen(False)
            
            #Display Timer
            self.write_screen("Time : " + "{:.1f}".format(self.barTime.timer), BLACK, self.barTime.posText, True)
            pygame.display.update()

            ev = pygame.event.get()
            #Tracking mouse position
            self.cursor_position.append(pygame.mouse.get_pos())
            for event in ev:
                L = self.listen(event)
                if event.type == pygame.QUIT:
                    self.quitApp()
                    
                #Update Timer
                if event.type == pygame.USEREVENT:
                    self.barTime.addSubTime(-0.01)
                    if self.barTime.timer <= 0:
                        self.running = False
                        self.menu("endGame")
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.menu("pause", 'quick')
                if ("cible",True) in L:#On a cliqué sur une cible
                    #Saving the tracking of mouse
                    self.cursor_position_list.append(self.cursor_position)
                    self.cursor_position = []
                    self.cursor_position.append(("target_pos :",(self.active_target.x,self.active_target.y)))
                if ("cible", False) in L:
                    self.barTime.timer -= 1

    def chooseMode(self):
        button1 = Button((int(self.width/2 - 250),int(self.height/2 + 30)), 1, 200, 60 , (200, 50, 50), RED, "Survival mode")
        button2 = Button((int(self.width/2 + 50),int(self.height /2+ 30)), 2, 200, 60 , (200, 50, 50), RED, "Speed mode") 
        self.addListenerDrawable([button1,button2])
        self.refreshScreen()
        self.write_screen("Choose Your Mode", BLACK, (self.width/2, self.height/2 - 30))
        self.running = True
        while(self.running):
            pygame.display.update()
            self.draw()
            ev = pygame.event.get()
            for event in ev:
                L = self.listen(event)
                #self.listenMode(event)
                if event.type == pygame.QUIT:
                    self.quitApp()
                if ("button",1) in L:
                    self.removeListenerDrawable([button1, button2])
                    self.score = 0
                    self.running = False
                    self.showAllDrawable()
                    self.showAllListener()
                    self.menu("play","main")
                    
                if ("button",2) in L:
                    self.removeListenerDrawable([button1, button2])
                    self.score = 0
                    self.running = False
                    self.showAllDrawable()
                    self.showAllListener()
                    self.menu("quick","main")
