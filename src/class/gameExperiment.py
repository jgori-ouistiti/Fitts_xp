from game import *
from experiment import *
import json

class GameExperiment(Game):
    
    def __init__(self, width, height, experiments, bg_color = Colors.WHITE):
        super().__init__(width, height, bg_color)
        
        self.infiniteTime = True
        self.activeExperiment = 0 #correspond exp_id or index of the active experiment in the experiments list
        self.experiments_data = dict() #User's data collected after ends of each experiments
        self.experiments_data['user_id'] = random.randint(0,1000000)
        self.experiments_data['experiments'] = dict()
        
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
            self.play(mode="", listTarget=self.listTarget)
            
        elif menu_title == "pause":
            pygame.time.set_timer(pygame.USEREVENT, 0) #Desactive pygame.USEREVENT
            self.hideAllDrawable()
            self.hideAllListener()
            self.pauseMenu(current_mode)
        elif menu_title == "chooseMode":
            pygame.time.set_timer(pygame.USEREVENT, 0) #Desactive pygame.USEREVENT
            self.hideAllDrawable()
            self.hideAllListener()
            self.chooseMode() 
            print("======", self.listTarget)
        elif menu_title == "endExperiment":
            pygame.time.set_timer(pygame.USEREVENT, 0) #Desactive pygame.USEREVENT
            self.dumpExperiment(data)
            self.activeExperiment += 1
            if self.activeExperiment == len(self.experiments):
                #end of experiments, no more experiments
                self.hideAllDrawable()
                self.hideAllListener()
                self.endOfExperiment()
            else:
                #There is still some experiments
                self.hideAllDrawable()
                self.hideAllListener()
                self.endExperimentScreen()
        
            
        else:
            raise Exception("Error of menu_title")
            
    def play(self, mode="", listTarget=[], displayConsolNbOfTarget = True):
        '''Method called when user press BEGIN button
        
        Each experiments calls menu("endExperiment") at the end
        No need to quit app here because endOfExperiment is called at the final end in menu() by the last experiment'''
        (self.experiments[self.activeExperiment]).begin(self)
        
    
        
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

            
    def endExperimentScreen(self):
        '''This screen is shown between 2 experiments
        It makes a pause for the user'''
        self.refreshScreen()
        self.write_box("End of experiment "+str((self.activeExperiment)) , Colors.BLACK, (self.width/2, self.height/2 - 30))
        self.write_box("Press SPACE to begin next experiment", Colors.BLACK, (self.width/2, self.height/2 + 30))
        self.running = True
        while(self.running):
            pygame.display.update()
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.QUIT:
                    self.quitApp()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.running = False
                        self.menu("play","pause")
                        
    def endOfExperiment(self):
        '''This screen is shown at the final end'''
        self.refreshScreen()
        self.write_box("END OF THE EXPERIMENT", Colors.BLACK, (self.width/2, self.height/2 - 60))
        self.write_box("Thanks for helping us participating at this experiment !", Colors.BLACK, (self.width/2, self.height/2))
        self.write_box("You can now close this window or press ESCAPE.", Colors.BLACK, (self.width/2, self.height/2 + 60))
        group = pygame.sprite.Group(self.inputBoxAvis) 
        self.running = True
        while(self.running):
            pygame.display.update()
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:    
                    if (self.inputBoxAvis.button_ok.isInside(pygame.mouse.get_pos())):
                        self.avis = self.inputBoxAvis.text #recupere avis
                        print("AVIS :", self.avis)
                        self.running = False
            group.update(self, ev, "Let us a comment")
            if self.inputBoxAvis.image!=None:
                group.draw(self.screen)
            pygame.display.flip()

        self.quitApp()
        
    def dumpExperiment(self,data):
        '''Dump one iteration in variable self.experiment
        It is one iteration called after each end of experiments'''
        self.experiments_data['experiments'][self.activeExperiment] = data
        
    def save_data_in_file(self, filename):
        '''Overide super method because we now use more complex json files''' 
        f = open(filename, 'w')
        json.dump(self.experiments_data, f, indent=4)
        f.close()
        
    def quitApp(self):
        '''Save user's data before quitting'''
        self.save_data_in_file("user_"+str(self.experiments_data['user_id'])+".json")
        self.running = False

    
