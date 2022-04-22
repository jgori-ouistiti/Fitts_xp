
from game import *
import sys
sys.path.append('../tools')
import colors as Colors
import random

class Experiment :
    def __init__(self, targets, exp_name, exp_id, maxTrials = 20):
        self.targets  = targets
        self.exp_name = exp_name
        self.exp_id   = exp_id
        
        self.maxTrials = maxTrials
        
        if self.maxTrials < 0:
            raise Exception("maxTrials must be positive")
        
        self.trial    = 0

    def begin(self, game):         
        '''Start the experience
        WARNING : we can pause the experience so we can exit this method at any time
        We must use trial variable to know where we are on the experiment
        '''
        
        if self.targets == None or self.targets == []:
            raise Exception("Experiment has no target initialized")
        
        game.running = True
        
        game.listTarget = targets = self.targets
        game.addListenerDrawable(self.targets)
        
        game.assignRandomTarget()
        
        game.cursor_position = []
        game.cursor_position.append(("target_pos :",(game.active_target.x,game.active_target.y)))
        
        while (game.running and self.trial < self.maxTrials):
            game.refreshScreen(True)

            ev = pygame.event.get()
            for event in ev:
            
                L = game.listen(event)
                
                if event.type == pygame.QUIT:
                    game.quitApp()
                    return 0
                    
                #collect mouse position
                if event.type == pygame.USEREVENT:
                    #Tracking mouse position
                    game.cursor_position.append(pygame.mouse.get_pos())
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game.running = False
                        game.removeListenerDrawable(targets)
                        game.menu("pause")
        
                if ("cible",True) in L:#On a cliqué sur une cible
                
                    self.trial += 1
                
                    game.score += 1
                        
                    #Saving the tracking of mouse
                    game.cursor_position_list.append(game.cursor_position)
                    game.cursor_position = []
                    game.cursor_position.append(("target_pos :",(game.active_target.x,game.active_target.y)))
                
                elif ("not cible",False) in L: #On n'a pas cliqué sur la bonne cible
                    game.score += -1
                    
        #End of the experiment
        game.running = False
        game.removeListenerDrawable(targets)
        game.menu("endExperiment")
        

