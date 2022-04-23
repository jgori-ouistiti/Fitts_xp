
from game import *
from cibleRect import *
import sys
sys.path.append('../tools')
import colors as Colors
import random
import time

class Experiment :
    def __init__(self, targets, exp_name, exp_id, maxTrials = 20):
        self.targets  = targets
        
        self.data = dict() #contains all user's data ,for this one experiment, about mouse tracking, time, etc...
        self.data['exp_name'] = exp_name
        self.data['exp_id']   = exp_id
        self.data['number_of_targets'] = len(targets)
        self.data['trials'] = dict()
        
        self.maxTrials = maxTrials
        
        self.startOfTrial = 0
        
        if self.maxTrials < 0:
            raise Exception("maxTrials must be positive")
        
        self.trial    = 0
        
    def iterateData(self, game):
        '''do one iteration each click and add mouth tracks and time to self.trials'''
        
        trialTime = time.time() - self.startOfTrial
        target = game.active_target
        cursor_tracks = game.cursor_position
        
        
        self.data['trials'][self.trial] = dict()
        
        self.data['trials'][self.trial]['pos_target'] = (target.x , target.y)
        if isinstance(target, CibleRect):
            self.data['trials'][self.trial]['target_type'] = 'rectangle'
            self.data['trials'][self.trial]['dimension']   = (target.width, target.height)
        else:
            self.data['trials'][self.trial]['target_type'] = 'circle'
            self.data['trials'][self.trial]['radius']      = target.r
            
        self.data['trials'][self.trial]['time'] = trialTime
        self.data['trials'][self.trial]['mouse_tracks'] = cursor_tracks
        

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
        
        self.startOfTrial = time.time()
        
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
                    
                    self.iterateData(game)
                
                    self.trial += 1
                
                    game.score += 1
                        
                    #Saving the tracking of mouse
                    game.cursor_position_list.append(game.cursor_position)
                    game.cursor_position = []
                
                elif ("not cible",False) in L: #On n'a pas cliqué sur la bonne cible
                    game.score += -1
                    
        #End of the experiment
        game.running = False
        game.removeListenerDrawable(targets)
        game.menu("endExperiment", data = self.data)
        

