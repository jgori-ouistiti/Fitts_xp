from game import *

class GameExperiment(Game):
    
    def __init__(self, width, height, bg_color = Colors.WHITE):
        super().__init__(width, height, bg_color)
        self.infiniteTime = True
        
    ###--------------------------- Menu avec les differents fonctions (play, pause, etc) ---------------------------###       
    def menu(self, menu_title, current_mode = 'play'):
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
        elif menu_title == "experience":
            pygame.time.set_timer(pygame.USEREVENT, 10) #Active pygame.USEREVENT toute les 10ms 
            self.experimentMode()

        elif menu_title == 'experienceMulti':
            pygame.time.set_timer(pygame.USEREVENT, 10) #Active pygame.USEREVENT toute les 10ms 
            self.experimentMultiTarget()
            
        else:
            raise Exception("Error of menu_title")
            
    def distractorMode(self, ID = 3, A = 40, p = 0.25, color = Colors.BLACK, nb_trials = 10):
        print("DISTRACTOR MODE")
        print("Avant ajout :",len(self.listener))
        L_targets = make_2D_distractor_target_list((self.width,self.height), (int(self.width/2),int(self.height/2)), ID, A, p, color)
        self.addListenerDrawable(L_targets)
        self.running = True
        self.nb_target = len(L_targets)
        self.assignRandomTarget()
        print(self.active_target, self.active_target.x, self.active_target.y, self.width, self.height) 
        print("Apres ajout :",len(self.listener))
        
        self.addDrawable(self.barTime)

        cursor_position = []
        cursor_position_list = []
        cursor_position.append(("target_pos :",(self.active_target.x,self.active_target.y)))
        
        cpt = 0
        #while (self.running and cpt < nb_trials):
        while (self.running):
            self.refreshScreen(False)
            
            #Display Timer
            self.write_screen("Time : " + "{:.1f}".format(self.barTime.timer), Colors.BLACK, self.barTime.posText, True)
            pygame.display.update()

            ev = pygame.event.get()
            #Tracking mouse position
            cursor_position.append(pygame.mouse.get_pos())
            for event in ev:
                L = self.listen(event)
                if event.type == pygame.QUIT:
                    self.quitApp()
                    
                #Update Timer
                if event.type == pygame.USEREVENT:
                    self.barTime.addSubTime(-0.01)
                    if self.barTime.timer <= 0:
                        self.running = False
                        self.removeListenerDrawable(L_targets)
                        self.menu("endGame")
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.menu("pause", 'experience')

                if ("cible",True) in L:#On a cliqué sur une cible
                    self.barTime.timer += 1

                    #Saving the tracking of mouse
                    cursor_position_list.append(cursor_position)
                    cursor_position = []
                    cursor_position.append(("target_pos :",(self.active_target.x,self.active_target.y)))
                    #Repositioning targets with mouse position
                    
                    #Removing ancient targets
                    self.removeListenerDrawable(L_targets)
                    
                    #Creating new targets with mouse position
                    L_targets = make_2D_distractor_target_list((self.width,self.height), pygame.mouse.get_pos() , ID, A, p, color)
                    self.addListenerDrawable(L_targets)
                    self.nb_target = len(L_targets)
                    self.refreshScreen(True)
                    pygame.display.update()
                    self.assignRandomTarget()
                    cpt += 1
                
                if ("cible", False) in L:
                    self.barTime.timer -= 1

        self.removeListenerDrawable(L_targets)
        #return info parametres, positions de la souris
        return {"ID" : ID, "A" : A, "p" : p}, cursor_position_list
        
    def chooseMode(self):
        '''MAIN MENU
        This menu is the first menu that the user sees
        In GameExperience, we use only one button to start the experiment'''
        button1 = Button((int(self.width/2 - 150),int(self.height/2 + 30)), 1, 300, 60 , (200, 50, 50), RED, "BEGIN")
        self.addListenerDrawable([button1])
        self.refreshScreen()
        
        text =  "Welcome to our experiment.\n\n"+\
                "You will encounter multiple experiments. You will have to click as fast as possible "+\
                "on the red targets.\n\n"+\
                "Thank you for your participation, click on BEGIN to start."
        
        self.write_screen(text, Colors.BLACK, (self.width/2 - 360, self.height/2 - 500), maxSize=(720, 300))
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
                    self.removeListenerDrawable([button1])
                    self.score = 0
                    self.running = False
                    self.showAllDrawable()
                    self.showAllListener()
                    self.menu("play","main")

            
    def experimentMode(self, userid = 0):
        print("experimentMode()")
        self.distractorMode()

    def experimentMultiTarget(self):
        quitGame = False
       
        while(self.nbTestTotal > 0):  
            
            ## Choose random a type of disposition of target 
            key = random.choice(list(self.listTest))
            value = self.listTest[key]
            print("---- key(typeTarget) =", key, "||", "nombre =", value[0])

            if value[0] > 0 :
                if value[0] == 1 : 
                    # it is the last test of this type of target, 
                    # with 'pop', we delete it of the dictionary 
                    listTarget = self.listTest.pop(key)[1] 
                else : 
                    value[0] -= 1
                    listTarget = value[1]

            self.running = True
            while (self.running):
                self.refreshScreen(True)
                self.write_screen("When you are ready, touch SPACE ", Colors.BLACK, (self.width/2, self.height/2 - 30))
                pygame.display.update()

                ev = pygame.event.get()
                for event in ev:
                    if event.type == pygame.QUIT:
                        quitGame = True
                        self.running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:     
                            ## User do the test
                            self.play('experienceMulti', listTarget, showTime=False)
                            self.nbTestTotal -= 1
                            self.running = False
            
            if self.nbTestTotal == 0:
                break 
            if quitGame :
                break

        if quitGame:
            self.quitApp()
        if self.nbTestTotal == 0:
            print("FIN DE EXPERIENCE") 
