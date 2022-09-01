from game import *
from experiment import *
from sensitiveCursor import *
import json

"""
    This class represent a mini experience without pause's time
"""

class GameExperiment(Game):
    
    def __init__(self, width, height, experiments, listTimerPause=dict(), cursor = None, bg_color = Colors.WHITE, cursorImage = 'class/cursor/cursor1.png', title='TEST CIBLES', fullscreen = True):
        super().__init__(width, height, bg_color, title=title, fullscreen = fullscreen)
        
        self.infiniteTime = True
        self.listTimerPause = listTimerPause
        self.activeExperiment = 0 #correspond exp_id or index of the active experiment in the experiments list
        self.experiments_data = dict() #User's data collected after ends of each experiments
        self.experiments_data['user_id'] = random.randint(0,1000000)
        self.experiments_data['display_screen'] = [width,height]
        self.experiments_data['input_device'] = 'mouse'
        self.experiments_data['experiments'] = dict()
        
        self.joy_is_init = False #boolean used to know if pygame.joystick has been initiated or not
        self.language = 'en' #default = en, can be changed with chooseLanguage() screen
        self.cursor = cursor
        self.joystick = None
        self.x_dead_zone = 0.1 #10% of deadzone on X axis
        self.y_dead_zone = 0.1 #10% of deadzone on Y axis
        #if cursor == None:
        #    self.cursor = SensitiveCursor(width, height, cursorImage = cursorImage) 
        #else:
        #    self.cursor = cursor 
        #self.addListenerDrawable(self.cursor)
        
        if hasattr(experiments, '__len__'):
            for experiment in experiments:
                if not isinstance(experiment, Experiment):
                    raise Exception("excepted Experiment but got "+experiment.__class__.__name__)
            self.experiments  = experiments # list of experiments objects
        else:
            if not isinstance(experiments, Experiment):
                raise Exception("excepted Experiment or list(Experiment) but got "+experiments.__class__.__name__)
            self.experiments = [experiments] # list of experiments objects

    ###--------------------------- Menu avec les differents fonctions (play, pause, etc) ---------------------------###       
    def menu(self, menu_title, current_mode = 'play', data = None, noPause = False):
        if menu_title == "play":
        
            pygame.time.set_timer(pygame.USEREVENT, 10) #Active pygame.USEREVENT toute les 10ms 
            return self.play(mode="", listTarget=self.listTarget)
        
        elif menu_title == 'chooseLanguage':
            pygame.time.set_timer(pygame.USEREVENT, 0) #Desactive pygame.USEREVENT
            self.hideAllDrawable()
            self.hideAllListener()
            self.chooseLanguage()
            return
        elif menu_title == 'chooseDevice':
            pygame.time.set_timer(pygame.USEREVENT, 0) #Desactive pygame.USEREVENT
            self.hideAllDrawable()
            self.hideAllListener()
            self.chooseDevice()
            return
        elif menu_title == "pause":
            pygame.time.set_timer(pygame.USEREVENT, 0) #Desactive pygame.USEREVENT
            self.hideAllDrawable()
            self.hideAllListener()
            res = self.pauseMenu(current_mode)
            self.showAllDrawable()
            self.showAllListener()
            pygame.time.set_timer(pygame.USEREVENT, 10)
            return res
        elif menu_title == "chooseMode":
            pygame.time.set_timer(pygame.USEREVENT, 0) #Desactive pygame.USEREVENT
            self.hideAllDrawable()
            self.hideAllListener()
            self.chooseMode()
            return
        elif menu_title == "endExperiment":
            pygame.time.set_timer(pygame.USEREVENT, 0) #Desactive pygame.USEREVENT
            self.dumpExperiment(data)
            self.activeExperiment += 1
            if self.activeExperiment == len(self.experiments):
                #end of experiments, no more experiments
                self.hideAllDrawable()
                self.hideAllListener()
                self.endOfExperiment()
                return
            else:
                #There is still some experiments
                self.hideAllDrawable()
                self.hideAllListener()
                self.checkPause()
                self.endExperimentScreen(noPause = noPause)
                return
        elif menu_title == "quit":
            if data != None:
                self.dumpExperiment(data)
            return self.quitApp()

            
        else:
            raise Exception("Error of menu_title")
            
    def play(self, mode="", listTarget=[], displayConsolNbOfTarget = True):
        '''Method called when user press BEGIN button
        
        Each experiments calls menu("endExperiment") at the end
        No need to quit app here because endOfExperiment is called at the final end in menu() by the last experiment'''
        return (self.experiments[self.activeExperiment]).begin(self)
        try:
            return (self.experiments[self.activeExperiment]).begin(self)
        except:
            print("Error in experiment : "+self.experiments[self.activeExperiment].data['exp_name']+"\nError during experiment, cought a pygame parachute, skipping to next experiment.")
            self.removeListenerDrawable(self.listTarget)
            return self.menu("endExperiment", self.experiments[self.activeExperiment].data, self.experiments[self.activeExperiment].noPause)
        
    def chooseLanguage(self):
        '''This menu is the first menu that the user sees
        This menu will display all languages available (french and english)
        After the language is selected, the chooseDevice screen is displayed'''
        
        space_between_flags  = 100
        
        flags = [] #Putting flags in an array list to add more languages in the future
        buttons = []
        
        #ENGLISH
        flags.append(('en', 'images/flag_en.png'))
        #FRENCH
        flags.append(('fr', 'images/flag_fr.png'))
        
        flag_y = int(self.height/2 - (self.height/(len(flags)+1)))
        height_flag = int(self.height - 2*flag_y)
        width_flag = int( (self.width / len(flags)) - (space_between_flags*2)) 
        
        for i in range(len(flags)):
            flag_x = int(i * self.width/len(flags) + space_between_flags) 
            buttons.append(Button((flag_x, flag_y), i, width_flag, height_flag, (0,0,0), (0,0,0), image=flags[i][1]))
            
        self.addListenerDrawable(buttons)
        self.refreshScreen()
        
        choosingLanguage = True
        
        if self.cursor != None:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
        else:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
        
        
        
        while(choosingLanguage):
            self.cursorMove()
            self.refreshScreen(False)
            pygame.display.update()
            ev = pygame.event.get()
            for event in ev:
                L = self.listen(event)
                #self.listenMode(event)
                if event.type == pygame.QUIT:
                    return self.quitApp()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return
                if len(L) >= 1 and len(L[0]) == 2:
                    print("L :", L)
                    print("flags :",flags)
                    self.language = flags[L[0][1]][0]
                    self.removeListenerDrawable(buttons)
                    self.showAllDrawable()
                    self.showAllListener()
                    choosingLanguage = False
                    
        print("Language :",self.language)
        
    def chooseDevice(self):
        '''This menu is the second menu that the user sees
        This menu will display three type of device (mouse, trackpad and stylus)
        After the device is selected, the chooseMode screen is displayed'''
        
        space_between_images  = 100
        
        devices = [] #Putting devices in an array list to add more languages in the future
        buttons = []
        
        #MOUSE
        devices.append(('mouse', 'images/device_mouse.png'))
        #TRACKPAD
        devices.append(('touchpad', 'images/device_touchpad.png'))
        #STYLUS
        devices.append(('stylus', 'images/device_stylus.png'))
        #CONTROLLER
        devices.append(('controller', 'images/device_controller.png'))
        
        device_y = int(self.height/2 - (self.height/(len(devices)+2)))
        height_device = int(self.height - 2*device_y)
        width_device = int( (self.width / len(devices)) - (space_between_images*2)) 
        
        for i in range(len(devices)):
            device_x = int(i * self.width/len(devices) + space_between_images) 
            buttons.append(Button((device_x, device_y), i, width_device, height_device, (0,0,0), (0,0,0), image=devices[i][1]))
            
        self.addListenerDrawable(buttons)
        self.refreshScreen()
        
        choosingDevice = True
        
        if self.cursor != None:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
        else:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
        
        
        
        while(choosingDevice):
            self.cursorMove()
            self.refreshScreen(False)
            pygame.display.update()
            ev = pygame.event.get()
            for event in ev:
                L = self.listen(event)
                #self.listenMode(event)
                if event.type == pygame.QUIT:
                    return self.quitApp()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return
                if len(L) >= 1 and len(L[0]) == 2:
                    print("L :", L)
                    print("devices :",devices)
                    self.experiments_data['input_device'] = devices[L[0][1]][0]
                    self.removeListenerDrawable(buttons)
                    self.showAllDrawable()
                    self.showAllListener()
                    choosingDevice = False
                    
        print("Device :",self.experiments_data['input_device'])
        
        

    def chooseMode(self):
        '''MAIN MENU
        This menu is the third menu that the user sees
        In GameExperience, we use only one button to start the experiment'''
        
        #Adding picture of next device used
        buttons = None
        if self.experiments[self.activeExperiment].input_device != None:
            buttons = []
            self.experiments_data['input_device'] = self.experiments[self.activeExperiment].input_device
            device_name = self.experiments[self.activeExperiment].input_device
            device = None
            if device_name == 'mouse':
                device = ('mouse', 'images/device_mouse.png')
            if device_name == 'touchpad':
                device = ('touchpad', 'images/device_touchpad.png')
            if device_name == 'stylus':
                device = ('stylus', 'images/device_stylus.png')
            if device_name == 'controller':
                device = ('controller', 'images/device_controller.png')
            if device == None:
                raise Exception("Device \""+device_name+"\"not recognized")
            device_y = int(self.height/1.5)
            height_device = int(self.height/10)
            width_device = int(self.width/15)
            buttons.append(Button((int(self.width/2), device_y), 0, width_device, height_device, (0,0,0), (0,0,0), image=device[1]))
            self.addListenerDrawable(buttons)
            
        if self.experiments[self.activeExperiment].input_device == 'controller':
            self.cursor = self.experiments[self.activeExperiment].cursor
            pygame.joystick.init()
            self.joy_is_init = True
            joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
            if len(joysticks) == 0:
                raise Exception("ERROR : NO JOYSTICK FOUND")
            else:
                self.joystick = joysticks[0]
                
        
        
        button1 = None
        if self.language == 'en':
            button1 = Button((int(self.width/2 + 160),int(self.height/2 - 30)), 1, 300, 60 , (200, 50, 50), RED, "BEGIN")
        elif self.language =='fr':
            button1 = Button((int(self.width/2 + 150),int(self.height/2 - 30)), 1, 340, 60 , (200, 50, 50), RED, "COMMENCER")
        self.addListenerDrawable([button1])
        self.refreshScreen()
        text = ''
        if self.language == 'en':
            if self.experiments[self.activeExperiment].input_device != None:
                text =  "Welcome to our experiment.\n\n"+\
                    "You will encounter multiple experiments. You will have to click as fast as possible "+\
                    "on the red targets.\n\n"+\
                    "WARNING : The first experiment require a "+self.experiments[self.activeExperiment].input_device+'\n\n'+\
                    "Thank you for your participation, click on BEGIN to start."
            else:
                text =  "Welcome to our experiment.\n\n"+\
                    "You will encounter multiple experiments. You will have to click as fast as possible "+\
                    "on the red targets.\n\n"+\
                    "Thank you for your participation, click on BEGIN to start."
        elif self.language =='fr':
            if self.experiments[self.activeExperiment].input_device != None:
                text =  "Bienvenue dans cette expérience.\n\n"+\
                    "Vous allez avoir plusieurs petites expériences. Il vous faudra cliquer le plus vite possible "+\
                    "sur les cibles rouges.\n\n"+\
                    "ATTENTION : La première expérience utilisera un(e) "+self.experiments[self.activeExperiment].input_device+'\n\n'\
                    "Merci de votre participation, appuyez sur COMMENCER pour démarrer."
            else:
                text =  "Bienvenue dans cette expérience.\n\n"+\
                    "Vous allez avoir plusieurs petites expériences. Il vous faudra cliquer le plus vite possible "+\
                    "sur les cibles rouges.\n\n"+\
                    "Merci de votre participation, appuyez sur COMMENCER pour démarrer."
        self.write_screen(text, Colors.BLACK, (self.width/8, self.height/2 - self.height/4), maxSize=(720, 300))
        running = True
        
        if self.cursor != None:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
        else:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
        
        while(running):
            self.cursorMove()
            self.refreshScreen(False)
            self.write_screen(text, Colors.BLACK, (self.width/8, self.height/2 - self.height/4), maxSize=(720, 300))
            pygame.display.update()
            ev = pygame.event.get()
            for event in ev:
                L = self.listen(event)
                #self.listenMode(event)
                if event.type == pygame.QUIT:
                    return self.quitApp()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if buttons != None:
                            self.removeListenerDrawable(buttons)
                        self.running = False
                        return
                if ("button",1) in L:
                    if buttons != None:
                            self.removeListenerDrawable(buttons)
                    self.removeListenerDrawable([button1])
                    self.score = 0
                    running = False
                    self.showAllDrawable()
                    self.showAllListener()
                    self.menu("play","main")

    def checkPause(self):
        '''This screen is shown between 2 experiments
                It makes a pause for the user with timer '''
                
        print("ACTIVE EXPERIMENT : ",self.activeExperiment,"\nLIST TIMER PAUSE :",self.listTimerPause,'\n')

        if self.activeExperiment in self.listTimerPause.keys() :
            running = True
            timer = self.listTimerPause[self.activeExperiment]
            pygame.time.set_timer(pygame.USEREVENT, 10) #Active pygame.USEREVENT toute les 10ms 
            while (running and timer >= 0):
                self.cursorMove()
                self.refreshScreen(False)
                if self.language == 'en':
                    self.write_box(" Pause time ! ", Colors.BLACK, (self.width / 2, self.height / 2 - 30))
                    self.write_box(" Continuing in " + "{:.1f}".format(timer) + " seconds", Colors.BLACK, (self.width / 2, self.height / 2 + 30))
                elif self.language == 'fr':
                    self.write_box(" Expérience temporairement en pause ! ", Colors.BLACK, (self.width / 2, self.height / 2 - 30))
                    self.write_box(" L'expérience reprend dans " + "{:.1f}".format(timer)+ " secondes", Colors.BLACK, (self.width / 2, self.height / 2 + 30))
                pygame.display.update()
                ev = pygame.event.get()
                for event in ev:
                    if event.type == pygame.QUIT:
                        return self.quitApp()
                    if event.type == pygame.USEREVENT: 
                        timer -= 0.01
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                            running = False
        pygame.time.set_timer(pygame.USEREVENT, 0) #Desactive    

    def endExperimentScreen(self, noPause = False):
        '''This screen is shown between 2 experiments
        It makes a pause for the user'''
        
        #Adding picture of next device used
        buttons = None
        if self.experiments[self.activeExperiment].input_device != None:
            buttons = []
            self.experiments_data['input_device'] = self.experiments[self.activeExperiment].input_device
            device_name = self.experiments[self.activeExperiment].input_device
            device = None
            if device_name == 'mouse':
                device = ('mouse', 'images/device_mouse.png')
            if device_name == 'touchpad':
                device = ('touchpad', 'images/device_touchpad.png')
            if device_name == 'stylus':
                device = ('stylus', 'images/device_stylus.png')
            if device_name == 'controller':
                device = ('controller', 'images/device_controller.png')
            if device == None:
                raise Exception("Device \""+device_name+"\"not recognized")
            #Setting coords for the image of the device
            #It uses a button to display the image 
            device_y = int(self.height/1.5)
            height_device = int(self.height/10)
            width_device = int(self.width/15)
            buttons.append(Button((int(self.width/2), device_y), 0, width_device, height_device, (0,0,0), (0,0,0), image=device[1]))
            self.addListenerDrawable(buttons)
            
        if self.experiments[self.activeExperiment].input_device == 'controller':
            self.cursor = self.experiments[self.activeExperiment].cursor
            pygame.joystick.init()
            self.joy_is_init = True
            joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
            if len(joysticks) == 0:
                raise Exception("ERROR : NO JOYSTICK FOUND")
            else:
                self.joystick = joysticks[0]
                
        elif self.experiments_data['input_device'] != 'controller' and self.joy_is_init:
            pygame.joystick.quit()
            self.cursor = None
            self.joy_is_init = False
        
        
        self.refreshScreen()
        
        if self.cursor != None:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
        else:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
        
        running = True
        
        while(running and not noPause):
            self.cursorMove()
            self.refreshScreen(False)
            #self.write_box("End of experiment "+str((self.activeExperiment)) , Colors.BLACK, (self.width/2, self.height/2 - 30))
            if self.language == 'en':
                if self.experiments[self.activeExperiment].input_device != None:
                    self.write_box(" WARNING : Next experiment uses a"+self.experiments[self.activeExperiment].input_device, Colors.BLACK, (self.width/2, self.height/2 - 30))
                else:
                    self.write_box(" Ready ? ", Colors.BLACK, (self.width/2, self.height/2 - 30))
                self.write_box("Press SPACE (or a key of the controller) to continue.", Colors.BLACK, (self.width/2, self.height/2 + 30))
            elif self.language == 'fr':
                if self.experiments[self.activeExperiment].input_device != None:
                    self.write_box(" ATTENTION : La prochaine expérience utilise un(e)"+self.experiments[self.activeExperiment].input_device, Colors.BLACK, (self.width/2, self.height/2 - 30))
                else:
                    self.write_box(" Prêt ? ", Colors.BLACK, (self.width/2, self.height/2 - 30))
                self.write_box("Appuyez sur ESPACE (ou une touche de la manette) pour continuer.", Colors.BLACK, (self.width/2, self.height/2 + 30))
            pygame.display.update()
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.QUIT:
                    return self.quitApp()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if buttons != None:
                            self.removeListenerDrawable(buttons)
                        running = False
                        return
                if event.type == pygame.JOYBUTTONDOWN:
                    if buttons != None:
                        self.removeListenerDrawable(buttons)
                    running = False
                    return
                        
    def endOfExperiment(self):
        '''This screen is shown at the final end'''
        self.cursorMove()
        self.refreshScreen()
        
        if self.cursor != None:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
        else:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
        
        group = pygame.sprite.Group(self.inputBoxAvis) 
        running = True
        while(running):
            self.refreshScreen(False)
            if self.language == 'en':
                self.write_box("END OF THE EXPERIMENT", Colors.BLACK, (self.width/2, self.height/2 - 60))
                self.write_box("Thanks for helping us participating at this experiment !", Colors.BLACK, (self.width/2, self.height/2))
                self.write_box("You can now close this window or press ESCAPE.", Colors.BLACK, (self.width/2, self.height/2 + 60))
            elif self.language == 'fr':
                self.write_box("FIN DE L'EXPÉRIENCE", Colors.BLACK, (self.width/2, self.height/2 - 60))
                self.write_box("Merci d'avoir participé !", Colors.BLACK, (self.width/2, self.height/2))
                self.write_box("Vous pouvez maintenant fermer cette fenêtre en appuyant sur ECHAP.", Colors.BLACK, (self.width/2, self.height/2 + 60))
            ev = pygame.event.get()
            
            group.update(self, ev, "Let us a comment")
            if self.inputBoxAvis.image!=None:
                group.draw(self.screen)
                
            self.draw()
            pygame.display.update()
            
            for event in ev:
                if event.type == pygame.QUIT:
                    self.running = False
                    return self.quitApp()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return self.quitApp()
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.JOYBUTTONDOWN:    
                    if (self.inputBoxAvis.button_ok.isInside(self.getCursorPos())):
                        self.avis = self.inputBoxAvis.text #recupere avis
                        print("AVIS :", self.avis)
                        self.experiments_data['user_review'] = self.avis
                        self.running = False
                        return self.quitApp()
            pygame.display.flip()

        return self.quitApp()
        
    def dumpExperiment(self,data):
        '''Dump one iteration in variable self.experiment
        It is one iteration called after each end of experiments'''
        self.experiments_data['experiments'][self.activeExperiment] = data
        
    def save_data_in_file(self, filename):
        '''Overide super method because we now use more complex json files''' 
        f = open(filename, 'w', encoding="utf-8")
        json.dump(self.experiments_data, f, indent=4,ensure_ascii=False)
        f.close()
        
    def quitApp(self):
        '''Save user's data before quitting'''
        self.save_data_in_file("../users_data/user_"+str(self.experiments_data['user_id'])+".json")
        self.running = False
        return -1
        
    def pauseMenu(self, current_mode):
        '''Pause menu'''
        self.refreshScreen()
        if self.language == 'en':
            self.write_box("PAUSE", Colors.BLACK, (self.width/2, self.height/2 - 30))
            self.write_box("Press ESCAPE or SPACE to continue", Colors.BLACK, (self.width/2, self.height/2 + 30))
        elif self.language =='fr':
            self.write_box("PAUSE", Colors.BLACK, (self.width/2, self.height/2 - 30))
            self.write_box("Appuyez sur ECHAP ou ESPACE pour continuer", Colors.BLACK, (self.width/2, self.height/2 + 30))
        
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        
        while(True):
            pygame.display.update()
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.QUIT:
                        self.running = False
                        return self.quitApp()
                if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                        if self.cursor != None:
                            pygame.mouse.set_visible(False)
                            pygame.event.set_grab(True)
                        else:
                            pygame.mouse.set_visible(True)
                            pygame.event.set_grab(False)
                        self.showAllDrawable()
                        self.showAllListener()
                        return
            
    def cursorMove(self):
        if self.cursor != None:
            # print("device :",self.experiments_data['input_device'])
            if self.experiments_data['input_device'] == 'controller':
                axis_X = self.joystick.get_axis(0)
                axis_Y = self.joystick.get_axis(1)
                if abs(axis_X) > self.x_dead_zone and abs(axis_Y) > self.y_dead_zone:
                    self.cursor.move(axis_X, axis_Y)
                elif abs(axis_X) > self.x_dead_zone:
                    self.cursor.move(axis_X, 0)
                elif abs(axis_Y) > self.x_dead_zone:
                    self.cursor.move(0, axis_Y)
            else:
                pos = pygame.mouse.get_rel()
                self.cursor.move(pos[0], pos[1])
        
    def draw(self):
        '''always draw the cursor at the end'''
        for d, v in self.drawables.items():
            if v == True:
                d.draw(self)
        if self.cursor != None:
            self.cursor.draw(self)
        
    def getCursorPos(self):
        if self.cursor == None:
            return pygame.mouse.get_pos()
        else:
            return (self.cursor.x, self.cursor.y)

    def start(self):
        self.running = True
        self.menu("chooseLanguage")
        if self.running:
            self.menu("chooseDevice")
        # if self.experiments_data['input_device'] == 'controller':
            # width, height = self.experiments_data['display_screen']
            # self.cursor = SensitiveCursor(width, height, cursorImage = 'class/cursor/cursor1.png', dx_sens = 3, dy_sens = 3, sens_type = 'adaptive')
            # pygame.joystick.init()
            # joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
            # if len(joysticks) == 0:
                # raise Exception("ERROR : NO JOYSTICK FOUND")
            # else:
                # self.joystick = joysticks[0]
            # print(joysticks)
        if self.running:
            self.menu("chooseMode")
        while(self.running):
            self.menu("play")
