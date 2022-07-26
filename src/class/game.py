import sys
sys.path.append('../tools')
from target_disposition import *
from turtle import pos
import pygame
import random
from drawable import *
from listener import *
from healthBar import *
from button import *
import colors as Colors
import textInputBox 

class Game :
    def __init__(self, width, height, bg_color = Colors.WHITE, title = 'TEST_CIBLES'):
        self.font = pygame.font.SysFont("aerial", 60)
        self.screen    = pygame.display.set_mode((width, height),0)
        pygame.display.set_caption(title)
        self.width     = width
        self.height    = height
        self.listener  = dict() #Key = Listener object, value = boolean (True if listening, False if not listening) 
        self.drawables = dict() #Key = Drawable object, value = boolean (True if is on screen, False if not )
        self.bg_color  = bg_color #background color
        self.running   = False
        self.barTime = HealthBar(5, posText=(30,70), posRect=(30,30))
        self.time = 100
        self.score = 0
        self.nb_target = 0
        self.target_radius = 0
        self.cursor_position = []
        self.cursor_position_list = []
        self.active_target = None

        self.nbTestTotal = 0 #For experienceMulti

        # typeTarget : int (pour savoir quel disposition des targets on utilise)
        # nombreExp : int (pour savoir on repete combien de fois ce disposition des targets)
        # listTarget : list (c'est une liste des positions des targets)
        self.listTarget = []
        ## self.list : dict( typeTarget : [nombreExp, listTarget] )
        self.listTest = dict() #For experienceMulti
        
        self.infiniteTime = False #Cheat for developpers
        
        self.inputBoxAvis = textInputBox.TextInputBox((self.width/2-200,self.height*2/3+100), self.width,self.height, width_texte=400, height_texte=100, bg_color_text = Colors.LIGHT_BLUE)
        
    def draw(self):
        for d, v in self.drawables.items():
            if v == True:
                d.draw(self)

    def refreshScreen(self, update = True):
        self.screen.fill(self.bg_color)
        self.draw()
        if update:
            pygame.display.update()
            
    def write_box(self, mot, color, pos, booleen=True):
        '''Write one line on screen on an invisible box
        The text is centered on the position pos. So it starts before and ends after.
        It doesn't break lines and so, can't read things as \n'''
        text = self.font.render(mot, booleen, color)
        text_rect = text.get_rect(center=pos)
        self.screen.blit(text, text_rect)

    def write_screen(self, text, color, pos, maxSize = None):
        '''Write a full text on screen
        The text starts on the position pos and can break lines.
        maxSize is for closing the text in a box
        This methods do not center the text'''
        words = [mot.split(' ') for mot in text.splitlines()]  # 2D array where each row is a list of words.
        space = self.font.size(' ')[0]  # The width of a space.
        x, y = pos
        if maxSize == None:
            max_width, max_height = self.screen.get_size()
        else:
            max_width, max_height = maxSize
            max_width += x
            max_height += y
        for line in words:
            for word in line:
                word_surface = self.font.render(word, 0, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                self.screen.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row.
        #text = self.font.render(mot, booleen, color)
        #text_rect = text.get_rect(center=pos)
        #self.screen.blit(text, text_rect)
            
    def addDrawable(self, d):
        '''Add a Drawable d in the list of drawables.
        Every draw() methods in the items present in the list are automatically called during the screen drawing'''
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
        '''Add a Listener l in the list of listeners.
        When an event is triggered, elements in the list are called 
        and their action() method is triggered if the event corresponds to them'''
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
        '''remove the drawable d from the list.
        It will desapear on the next screen refreshing'''
        if (hasattr(d, "__len__")):
            for d_item in d:
                if d_item in self.drawables.keys():
                    del self.drawables[d_item]
        elif d in self.drawables.keys():
            del self.drawables[d]
            
    def removeListener(self, l):
        '''remove the listener l from the list.
        It won't be triggered anymore'''
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
        '''Add a Listener that is also a Drawable (that can be see on screen)'''
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
            raise Exception("ld is not a listener and not drawable, but is a " + ld.__class__.__name__)
        if (not isinstance(ld, Listener)):
            raise Exception("ld is not a listener, but is a "+ ld.__class__.__name__)
        if (not isinstance(ld, Drawable)):
            raise Exception("ld is not drawable , but is a " + ld.__class__.__name__)
        if isinstance(ld, Cible):
            self.nb_target += 1
        self.drawables[ld] = True
        self.listener[ld] = True
        
    def removeListenerDrawable(self, ld):
        '''Remove the Listener and Drawable ld'''
        if (hasattr(ld, "__len__")):
            for item in ld:
                if item in self.drawables.keys() and item in self.listener.keys():
                    del self.drawables[item]
                    del self.listener[item]
                    if isinstance(item, Cible):
                        self.nb_target -= 1

        elif ld in self.drawables.keys() and ld in self.listener.keys():
            del self.drawables[ld]
            del self.listener[ld]
            if isinstance(ld, Cible):
                self.nb_target -= 1
        else:
            raise Exception("ld not in listener drawable")

    def hideDrawable(self, d):
        '''Hide the drawable d from screen but don't remove it. It is used
        if you want to keep the drawable d without having it on screen for one moment'''
        self.drawables[d] = False
    
    def hideListener(self, l):
        '''Deactivate the listener l until showListener(l) is called'''
        self.listener[l] = False
        
    def hideListenerDrawable(self, ld):
        '''Deactivate the listener and drawable l. It won't be triggered nor drawed until show methods are called'''
        self.hideDrawable(ld)
        self.hideListener(ld)
        
    def hideAllDrawable(self):
        '''Deactivate all drawables in the list'''
        for d in self.drawables.keys():
            self.drawables[d] = False
            
    def hideAllListener(self):
        '''Deactivate all listener in the list'''
        for l in self.listener.keys():
            self.listener[l] = False

    def showAllDrawable(self):
        '''Show all drawables in the list'''
        for d in self.drawables.keys():
            self.drawables[d] = True
            
    def showAllListener(self):
        '''Activate all listener in the list'''
        for l in self.listener.keys():
            self.listener[l] = True
            
    def listen(self, event):
        '''Call the action(event) method on every activated listener'''
        L = []
        for l, v in self.listener.items():
            if v:
                tmp = l.action(self,event)
                if tmp:
                    L.append(tmp)
        return L
        
    def assignRandomTarget(self, printTarget = True):
        '''Assign every active targets to False on pick one randomly to assign it to the actual target'''
        #Set one target the main target to hit
        if len(self.listTarget) <= 1:
            return
        new_target_id = random.randint(0,self.nb_target - 1)

        target = None
        i = 0
        for obj in self.listTarget:
            obj.isTarget = False
            if i == new_target_id:  
                obj.isTarget = True
                self.active_target = obj
                target = obj
                if printTarget :
                    if isinstance(target, CibleRect):
                        print('target info : x:',target.x, '|y:',target.y,'|width:',target.width,'|height:',target.height)
                    else:
                        print('target info : x:',target.x, '|y:',target.y,'|r:',target.r)
            i += 1
        if target == None:
            raise Exception("Internal error, no target found...")
   
    def save_data_in_file(self, filename):
        f = open(filename, 'w')
        f.write("NB_TARGET " + str(self.nb_target) + "\n")
        f.write(str(self.cursor_position_list))
        f.close()
        
    def addTest(self, nombre, typeTarget, listTarget): 
        """
            Permet d'ajouter/augmenter de nombre d'experience selon typeTarget (correspondant au type de disposition des cibles)
        """
        if nombre > 0 : 
            self.nbTestTotal += nombre
            if typeTarget in self.listTest : #si il existe, alors on augmente le nombre
                self.listTest[typeTarget][0] += nombre
            else : #sinon on va la creer, en la rajoutant dans le dictionnaire
                self.listTest[typeTarget] = [nombre, listTarget] 
            
    

 ###--------------------------- Menu avec les differents fonctions (play, pause, etc) ---------------------------###       
    def menu(self, menu_title, current_mode = 'play'):
        '''This method is called when changing the scene.
        It resets timer if needed'''
        if menu_title == "play":
            if current_mode != "pause":
                self.barTime.maxtime = 5
                self.barTime.timer = 5
            pygame.time.set_timer(pygame.USEREVENT, 10) #Active pygame.USEREVENT toute les 10ms 
            if self.infiniteTime:
                self.play(mode="", listTarget=self.listTarget, showTime=False,)
            else: 
                self.play(mode="", listTarget=self.listTarget)
        elif menu_title == "pause":
            pygame.time.set_timer(pygame.USEREVENT, 0) #Active pygame.USEREVENT toute les 10ms 
            self.hideAllDrawable()
            self.hideAllListener()
            self.pauseMenu(current_mode)
        elif menu_title == "endGame":
            pygame.time.set_timer(pygame.USEREVENT, 0) #Active pygame.USEREVENT toute les 10ms 
            self.hideAllDrawable()
            self.hideAllListener()
            self.endGame()
        elif menu_title == "chooseMode":
            pygame.time.set_timer(pygame.USEREVENT, 0) #Active pygame.USEREVENT toute les 10ms 
            self.hideAllDrawable()
            self.hideAllListener()
            self.chooseMode() 
        elif menu_title == "quick":
            if current_mode != "pause":
                self.barTime.maxtime = 10
                self.barTime.timer = 10
            pygame.time.set_timer(pygame.USEREVENT, 10) #Active pygame.USEREVENT toute les 10ms 
            if self.infiniteTime:
                self.quickMode(mode="", listTarget=self.listTarget, showTime=False,)
            else: 
                self.quickMode(mode="", listTarget=self.listTarget)
        elif menu_title == "reactive":
            pygame.time.set_timer(pygame.USEREVENT, 10) #Active pygame.USEREVENT toute les 10ms
            self.reactiveMode()
        else:
            raise Exception("Error of menu_title")
      
    
    def quitApp(self):
        '''Save user's data before quitting'''
        self.save_data_in_file("resultat.txt")
        self.running = False
        
    def pauseMenu(self, current_mode):
        '''Pause menu'''
        self.refreshScreen()
        self.write_box("PAUSE", Colors.BLACK, (self.width/2, self.height/2 - 30))
        self.write_box("Press ESCAPE to continue", Colors.BLACK, (self.width/2, self.height/2 + 30))
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
        '''End screen showed at user when the game is over
        It displays the score of the user'''
        self.refreshScreen()
        self.write_box("GAME OVER", Colors.BLACK, (self.width/2, self.height/3 - 50))
        self.write_box("Your score : " + str(self.score), Colors.BLACK, (self.width/2, self.height/3))
        self.write_box("Press ESCAPE to play again", Colors.BLACK, (self.width/2, self.height/3 + 50))
        self.running = True
        group = pygame.sprite.Group(self.inputBoxAvis) 
        self.avis = ""
        while(self.running):
            #pygame.display.update()
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
                if event.type == pygame.MOUSEBUTTONDOWN:    
                    if (self.inputBoxAvis.button_ok.isInside(pygame.mouse.get_pos())):
                        self.avis = self.inputBoxAvis.text #recupere avis
                        print("AVIS :", self.avis)
                        running = False
            group.update(self, ev, "Let us a comment")
            if self.inputBoxAvis.image!=None:
                group.draw(self.screen)
            pygame.display.flip()
    
    def play(self, mode="", listTarget=[], showTime=True, displayConsolNbOfTarget = True) :
        '''Normal mode
        The user have a certain amount of time to hit the maximum of targets without clicking on the wrong ones.
        If success, the user get a little amount of time and get +1 in score
        if not, the user lose a little amount of time and get -1 in score.
        
        The game is over when the timer gets to 0'''
    
        self.running = True
        
        targets = listTarget
        
        if targets == None or targets == []:
            targets = make_2D_distractor_target_list((self.width, self.height), (int(self.width/2), int(self.height/2) ), 3, 40, 0.25, Colors.BLACK)
            self.listTarget = targets
            self.addListenerDrawable(targets)
        else :
            self.addListenerDrawable(targets)
        
        if displayConsolNbOfTarget :
            print("number of target stored :", self.nb_target)
        
        self.assignRandomTarget()
        
        if showTime and mode!="experienceMulti": 
            self.addDrawable(self.barTime)
        
        self.cursor_position = []
        self.cursor_position.append(("target_pos :",(self.active_target.x,self.active_target.y)))
        while (self.running):
            self.refreshScreen(True)
            
            if showTime and mode!="experienceMulti":
                #Display Timer
                self.write_screen("Time : " + "{:.1f}".format(self.barTime.timer), Colors.BLACK, self.barTime.posText)
                pygame.display.update()

            ev = pygame.event.get()
            for event in ev:
                L = self.listen(event)
                if event.type == pygame.QUIT:
                    if mode=="experienceMulti":
                        self.removeListenerDrawable(targets)
                    self.quitApp()
                    
                #Update Timer and collect mouse position
                if self.infiniteTime == False and event.type == pygame.USEREVENT:
                    #Tracking mouse position
                    self.cursor_position.append(pygame.mouse.get_pos())
                    #Decrementing timer
                    self.barTime.addSubTime(-0.01)
                    if showTime and self.barTime.timer <= 0:
                        self.running = False
                        self.removeListenerDrawable(targets)
                        self.menu("endGame")
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.removeListenerDrawable(targets)
                        self.menu("pause")
        
                if ("cible",True) in L:#On a cliqué sur une cible
                    if not self.infiniteTime:
                        self.barTime.timer += 1
                        self.score += 1
                    #Saving the tracking of mouse
                    self.cursor_position_list.append(self.cursor_position)
                    self.cursor_position = []
                    self.cursor_position.append(("target_pos :",(self.active_target.x,self.active_target.y)))
                
                    if mode=="experienceMulti":
                        self.removeListenerDrawable(targets)
                        return 1
                elif ("not cible",False) in L: #On n'a pas cliqué sur la bonne cible
                    if not self.infiniteTime:
                        self.barTime.timer += -1
                        self.score += -1

    def chooseMode(self):
    
        '''It is the first menu that appears
        in this class, we have 2 modes, so the user can click on 2 buttons to play these
        different modes
        
        This menu appears again when the user gets a game over (endGame)'''
        
        button1 = Button((int(self.width/2 - 500),int(self.height/2 + 30)), 1, 300, 60 , (200, 50, 50), RED, "Survival mode")
        button2 = Button((int(self.width/2 - 150), int(self.height /2+ 30)), 2, 300, 60 , (200, 50, 50), RED, "Speed mode")
        button3 = Button((int(self.width / 2 + 200), int(self.height / 2 + 30)), 3, 300, 60, (200, 50, 50), RED, "Reactive mode")
        listButton = [button1,button2, button3]
        self.addListenerDrawable(listButton)
        self.refreshScreen()
        self.write_screen("Choose Your Mode", Colors.BLACK, (self.width/2 - 180, self.height/2 - 30))
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
                    print("Boutton 1")
                    self.removeListenerDrawable(listButton)
                    self.score = 0
                    self.running = False
                    self.showAllDrawable()
                    self.showAllListener()
                    self.menu("play","main")
                    
                if ("button",2) in L:
                    print("Boutton 2")
                    self.removeListenerDrawable(listButton)
                    self.score = 0
                    self.running = False
                    self.showAllDrawable()
                    self.showAllListener()
                    self.menu("quick","main")

                if ("button",3) in L:
                    print("Boutton 3")
                    self.removeListenerDrawable(listButton)
                    self.score = 0
                    self.running = False
                    self.showAllDrawable()
                    self.showAllListener()
                    self.menu("reactive","main")

    def quickMode(self, mode="", listTarget=[], showTime=True, displayConsolNbOfTarget = True):
        
        '''Secundary mode (Speed mode)
        In this mode, the user will have a certain amount of time to hit a maximum of targets.
        
        He will get +1 in score if he hits the good target
        he will get -1 if it is a wrong one.
        
        No time are given nor debited.
        '''
    
        self.running = True
        
        targets = listTarget
        
        if targets == []:
            if self.listTarget != []:
                targets = self.listTarget
            else:
                targets = make_2D_distractor_target_list(\
                    (self.width, self.height), \
                    (int(self.width/2), int(self.height/2) ),\
                    3, 40, 0.25, Colors.BLACK)
                self.listTarget = targets
            self.addListenerDrawable(targets)
        else :
            self.addListenerDrawable(targets)
        
        if displayConsolNbOfTarget :
            print("number of target stored :", self.nb_target)
        
        self.assignRandomTarget()
        self.addDrawable(self.barTime)
        
        self.cursor_position = []
        self.cursor_position.append(("target_pos :",(self.active_target.x,self.active_target.y)))
        while (self.running):
            self.refreshScreen(False)
            
            #Display Timer
            self.write_screen("Time : " + "{:.1f}".format(self.barTime.timer), Colors.BLACK, self.barTime.posText)
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
                        self.removeListenerDrawable(targets)
                        self.menu("endGame")
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.menu("pause", 'quick')
                if ("cible",True) in L:#On a cliqué sur une cible
                    if not self.infiniteTime:
                        self.score += 1
                    #Saving the tracking of mouse
                    self.cursor_position_list.append(self.cursor_position)
                    self.cursor_position = []
                    self.cursor_position.append(("target_pos :",(self.active_target.x,self.active_target.y)))
                elif ("not cible", False) in L: #On n'a pas cliqué sur la bonne cible
                    self.barTime.timer += -1 
                    self.score += -1

    def reactiveMode(self, ID=3, A=40, p=0.25, color=Colors.BLACK, nb_trials=10):
        print("Reactive MODE")
        print("Avant ajout :", len(self.listener))
        L_targets = make_2D_distractor_target_list((self.width, self.height),
                                                   (int(self.width / 2), int(self.height / 2)), ID, A, p, color)
        self.addListenerDrawable(L_targets)
        self.running = True
        self.nb_target = len(L_targets)
        self.listTarget = L_targets
        self.assignRandomTarget()

        print(self.active_target, self.active_target.x, self.active_target.y, self.width, self.height)

        print("Apres ajout :", len(self.listener))

        cursor_position = []
        cursor_position_list = []
        cursor_position.append(("target_pos :", (self.active_target.x, self.active_target.y)))

        cpt = 0
        while (self.running and cpt < nb_trials):
            self.refreshScreen(True)

            # Display Timer
            #self.write_screen("Time : " + "{:.1f}".format(self.barTime.timer), Colors.BLACK, self.barTime.posText, True)
            #pygame.display.update()

            ev = pygame.event.get()
            # Tracking mouse position
            cursor_position.append(pygame.mouse.get_pos())
            for event in ev:
                L = self.listen(event)
                if event.type == pygame.QUIT:
                    self.quitApp()

                # Update Timer
                if event.type == pygame.USEREVENT:
                    self.barTime.addSubTime(0.01)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.menu("pause", 'experience')
                if ("cible", True) in L:  # On a cliqué sur une cible
                    # Saving the tracking of mouse
                    cursor_position_list.append(cursor_position)
                    cursor_position = []
                    cursor_position.append(("target_pos :", (self.active_target.x, self.active_target.y)))
                    # Repositioning targets with mouse position

                    # Removing ancient targets
                    self.removeListenerDrawable(L_targets)

                    # Creating new targets with mouse position
                    L_targets = make_2D_distractor_target_list((self.width, self.height), pygame.mouse.get_pos(), ID, A,
                                                               p, color)
                    self.addListenerDrawable(L_targets)
                    self.nb_target = len(L_targets)
                    self.listTarget = L_targets
                    self.refreshScreen(True)
                    pygame.display.update()
                    self.assignRandomTarget()
                    cpt += 1
                if ("cible", False) in L:
                    self.barTime.timer -= 1
        self.removeListenerDrawable(L_targets)
        # return info parametres, positions de la souris
        self.menu("chooseMode")
        return {"ID": ID, "A": A, "p": p}, cursor_position_list

