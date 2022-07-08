from game import *
from experiment import *
from sensitiveCursor import *
import json

"""
    This class represent a mini experience without pause's time
"""

class GameExperiment(Game):
    
    def __init__(self, width, height, experiments, listTimerPause=[], cursor = None, bg_color = Colors.WHITE, cursorImage = 'class/cursor/cursor1.png', title='TEST CIBLES'):
        super().__init__(width, height, bg_color, title=title)
        
        self.infiniteTime = True
        self.listTimerPause = listTimerPause
        self.activeExperiment = 0 #correspond exp_id or index of the active experiment in the experiments list
        self.experiments_data = dict() #User's data collected after ends of each experiments
        self.experiments_data['user_id'] = random.randint(0,1000000)
        self.experiments_data['experiments'] = dict()
        self.language = 'en' #default = en, can be changed with chooseLanguage() screen
        if cursor == None:
            self.cursor = SensitiveCursor(width, height, cursorImage = cursorImage) 
        else:
            self.cursor = cursor 
        self.addListenerDrawable(self.cursor)
        
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
    def menu(self, menu_title, current_mode = 'play', data = None):
        if menu_title == "play":
        
            pygame.time.set_timer(pygame.USEREVENT, 10) #Active pygame.USEREVENT toute les 10ms 
            return self.play(mode="", listTarget=self.listTarget)
        
        elif menu_title == 'chooseLanguage':
            pygame.time.set_timer(pygame.USEREVENT, 0) #Desactive pygame.USEREVENT
            self.hideAllDrawable()
            self.hideAllListener()
            self.chooseLanguage()
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
                self.endExperimentScreen()
                return

            
        else:
            raise Exception("Error of menu_title")
            
    def play(self, mode="", listTarget=[], displayConsolNbOfTarget = True):
        '''Method called when user press BEGIN button
        
        Each experiments calls menu("endExperiment") at the end
        No need to quit app here because endOfExperiment is called at the final end in menu() by the last experiment'''
        return (self.experiments[self.activeExperiment]).begin(self)
        
    def chooseLanguage(self):
        '''This menu is the first menu that the user sees
        This menu will display all languages available (french and english)
        After the language is selected, the chooseMode screen is displayed'''
        
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
            flag_x = int(i * self.width/2 + space_between_flags) 
            buttons.append(Button((flag_x, flag_y), i, width_flag, height_flag, (0,0,0), (0,0,0), image=flags[i][1]))
            
        self.addListenerDrawable(buttons)
        self.refreshScreen()
        
        self.running = True
        
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        while(self.running):
            self.refreshScreen(False)
            pygame.display.update()
            ev = pygame.event.get()
            for event in ev:
                L = self.listen(event)
                #self.listenMode(event)
                if event.type == pygame.QUIT:
                    self.quitApp()
                if event.type == pygame.MOUSEMOTION:
                    self.cursorMove()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                if len(L) >= 1:
                    self.language = flags[L[0][1]][0]
                    self.removeListenerDrawable(buttons)
                    self.running = False
                    self.showAllDrawable()
                    self.showAllListener()
                    return self.menu("chooseMode","main")
        
        

    def chooseMode(self):
        '''MAIN MENU
        This menu is the second menu that the user sees
        In GameExperience, we use only one button to start the experiment'''
        button1 = None
        if self.language == 'en':
            button1 = Button((int(self.width/2 - 150),int(self.height/2 + 30)), 1, 300, 60 , (200, 50, 50), RED, "BEGIN")
        elif self.language =='fr':
            button1 = Button((int(self.width/2 - 170),int(self.height/2 + 30)), 1, 340, 60 , (200, 50, 50), RED, "COMMENCER")
        self.addListenerDrawable([button1])
        self.refreshScreen()
        text = ''
        if self.language == 'en':
            text =  "Welcome to our experiment.\n\n"+\
                    "You will encounter multiple experiments. You will have to click as fast as possible "+\
                    "on the red targets.\n\n"+\
                    "Thank you for your participation, click on BEGIN to start."
        elif self.language =='fr':
            text =  "Bienvenue dans cette expérience.\n\n"+\
                    "Vous allez avoir plusieurs petites expériences. Il vous faudra cliquer le plus vite possible "+\
                    "sur les cibles rouges.\n\n"+\
                    "Merci de votre participation, appuyez sur COMMENCER pour démarrer."
        self.write_screen(text, Colors.BLACK, (self.width/2 - 360, self.height/2 - 500), maxSize=(720, 300))
        self.running = True
        
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        while(self.running):
            self.refreshScreen(False)
            self.write_screen(text, Colors.BLACK, (self.width/2 - 360, self.height/2 - 500), maxSize=(720, 300))
            pygame.display.update()
            ev = pygame.event.get()
            for event in ev:
                L = self.listen(event)
                #self.listenMode(event)
                if event.type == pygame.QUIT:
                    self.quitApp()
                if event.type == pygame.MOUSEMOTION:
                    self.cursorMove()
                if ("button",1) in L:
                    self.removeListenerDrawable([button1])
                    self.score = 0
                    self.running = False
                    self.showAllDrawable()
                    self.showAllListener()
                    self.menu("play","main")

    def checkPause(self):
        '''This screen is shown between 2 experiments
                It makes a pause for the user with timer '''

        for (id, timerPause) in self.listTimerPause :
            if (self.activeExperiment-1 == id):
                self.running = True
                timer = 0
                pygame.time.set_timer(pygame.USEREVENT, 10) #Active pygame.USEREVENT toute les 10ms 
                while (self.running and timer <= timerPause*100):
                    self.refreshScreen(False)
                    restTime = (timerPause*1000 - timer)
                    if restTime < 10:
                        break
                    if self.language == 'en':
                        self.write_box(" Pause time ! ", Colors.BLACK, (self.width / 2, self.height / 2 - 30))
                        self.write_box(" Begin in " + str(restTime)[1] + " seconds", Colors.BLACK, (self.width / 2, self.height / 2 + 30))
                    elif self.language == 'fr':
                        self.write_box(" Jeu temporairement en pause ! ", Colors.BLACK, (self.width / 2, self.height / 2 - 30))
                        self.write_box(" Le jeu reprend dans " + str(restTime)[1] + " secondes", Colors.BLACK, (self.width / 2, self.height / 2 + 30))
                    pygame.display.update()
                    ev = pygame.event.get()
                    for event in ev:
                        if event.type == pygame.QUIT:
                            self.quitApp()
                        if event.type == pygame.MOUSEMOTION:
                            self.cursorMove()
                        if event.type == pygame.USEREVENT: 
                            timer += 10
                pygame.time.set_timer(pygame.USEREVENT, 0) #Desactive
                break;

    def endExperimentScreen(self):
        '''This screen is shown between 2 experiments
        It makes a pause for the user'''
        self.refreshScreen()
        
        self.running = True
        while(self.running):
            self.refreshScreen(False)
            #self.write_box("End of experiment "+str((self.activeExperiment)) , Colors.BLACK, (self.width/2, self.height/2 - 30))
            if self.language == 'en':
                self.write_box(" Ready ? ", Colors.BLACK, (self.width/2, self.height/2 - 30))
                self.write_box("Press SPACE to continue.", Colors.BLACK, (self.width/2, self.height/2 + 30))
            elif self.language == 'fr':
                self.write_box(" Prêt ? ", Colors.BLACK, (self.width/2, self.height/2 - 30))
                self.write_box("Appuyez sur ESPACE pour continuer.", Colors.BLACK, (self.width/2, self.height/2 + 30))
            pygame.display.update()
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.QUIT:
                    self.quitApp()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.running = False
                        self.menu("play","pause")
                if event.type == pygame.MOUSEMOTION:
                    self.cursorMove()
                        
    def endOfExperiment(self):
        '''This screen is shown at the final end'''
        self.refreshScreen()
        
        group = pygame.sprite.Group(self.inputBoxAvis) 
        self.running = True
        while(self.running):
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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:    
                    if (self.inputBoxAvis.button_ok.isInside((self.cursor.x, self.cursor.y))):
                        self.avis = self.inputBoxAvis.text #recupere avis
                        print("AVIS :", self.avis)
                        self.experiments_data['user_review'] = self.avis
                        self.running = False
                if event.type == pygame.MOUSEMOTION:
                    self.cursorMove()
            pygame.display.flip()

        self.quitApp()
        
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
        
    def pauseMenu(self, current_mode):
        '''Pause menu'''
        self.refreshScreen()
        if self.language == 'en':
            self.write_box("PAUSE", Colors.BLACK, (self.width/2, self.height/2 - 30))
            self.write_box("Press ESCAPE to continue", Colors.BLACK, (self.width/2, self.height/2 + 30))
        elif self.language =='fr':
            self.write_box("PAUSE", Colors.BLACK, (self.width/2, self.height/2 - 30))
            self.write_box("Appuyez sur ESPACE pour continuer", Colors.BLACK, (self.width/2, self.height/2 + 30))
        self.running = True
        
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        
        while(True):
            pygame.display.update()
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.QUIT:
                        self.quitApp()
                        return -1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                        self.showAllDrawable()
                        self.showAllListener()
                        return
            
    def cursorMove(self):
        pos = pygame.mouse.get_rel()
        self.cursor.move(pos[0], pos[1])
        
    def draw(self):
        '''always draw the cursor at the end'''
        for d, v in self.drawables.items():
            if v == True:
                d.draw(self)
        self.cursor.draw(self)
