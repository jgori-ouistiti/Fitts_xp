
from game import *
from cibleRect import *
import sys
sys.path.append('../tools')
import colors as Colors
import random
import time

class Experiment :
    def __init__(self, targets, exp_name, exp_id, maxTrials = 20, dx_sens = 1, dy_sens = 1):
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
        
        self.trial_id    = 0
        
        #Cursor sensitibility for the experiment
        self.dx_sens = 1
        self.dy_sens = 1
        
    def set_x_sensibility(self, dx_sens):
        self.dx_sens = dx_sens
        
    def set_y_sensibility(self, dy_sens):
        self.dy_sens = dy_sens
        
    def iterateData(self, game):
        '''do one iteration each click and add mouth tracks and time to self.trials'''
        
        trialTime = time.time() - self.startOfTrial
        target = game.active_target
        cursor_tracks = game.cursor_position
        
        
        self.data['trials'][self.trial_id] = dict()
        
        self.data['trials'][self.trial_id]['pos_target'] = (target.x , target.y)
        if isinstance(target, CibleRect):
            self.data['trials'][self.trial_id]['target_type'] = 'rectangle'
            self.data['trials'][self.trial_id]['dimension']   = (target.width, target.height)
        else:
            self.data['trials'][self.trial_id]['target_type'] = 'circle'
            self.data['trials'][self.trial_id]['radius']      = target.r
        self.data['trials'][self.trial_id]['time'] = trialTime
        self.data['trials'][self.trial_id]['mouse_tracks'] = cursor_tracks
        

    def begin(self, game):         
        '''Start the experience
        WARNING : we can pause the experience so we can exit this method at any time
        We must use trial variable to know where we are on the experiment
        '''
        
        if self.targets == None or self.targets == []:
            raise Exception("Experiment has no target initialized")
        
        self.data['cursor_x_sensibility'] = self.dx_sens
        self.data['cursor_y_sensibility'] = self.dy_sens
        
        game.running = True
        
        game.listTarget = targets = self.targets
        print("================", game.listTarget)
        game.addListenerDrawable(self.targets)
        
        game.assignRandomTarget()
        
        game.cursor_position = []
        
        #Save the cursor settings (sensibility)
        dx_cursor, dy_cursor = game.cursor.getSensibility()
        #Set the cursor sensibility to the experiment sensibility settings
        game.cursor.set_x_sensibility(self.dx_sens)
        game.cursor.set_y_sensibility(self.dy_sens)
        
        self.startOfTrial = time.time()
        
        while (game.running and self.trial_id < self.maxTrials):
            
            pygame.mouse.set_pos = (game.width/2, game.height/2)
            
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
                    game.cursor_position.append((game.cursor.x, game.cursor.y))
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        #Reset the cursor sensibility back to previous settings
                        game.cursor.set_x_sensibility(dx_cursor)
                        game.cursor.set_y_sensibility(dy_cursor)
                        pygame.mouse.set_visible(True)
                        game.running = False
                        game.removeListenerDrawable(targets)
                        game.menu("pause")
                        return
                if event.type == pygame.MOUSEMOTION:
                    game.cursorMove(event.rel)
        
                if ("cible",True) in L:#On a cliqué sur une cible
                    
                    self.iterateData(game)
                
                    self.trial_id += 1
                
                    game.score += 1
                        
                    #Saving the tracking of mouse
                    game.cursor_position_list.append(game.cursor_position)
                    game.cursor_position = []
                
                elif ("not cible",False) in L: #On n'a pas cliqué sur la bonne cible
                    game.score += -1
                    
        #End of the experiment
        #Reset the cursor sensibility back to previous settings
        game.cursor.set_x_sensibility(dx_cursor)
        game.cursor.set_y_sensibility(dy_cursor)
        game.running = False
        game.removeListenerDrawable(targets)
        game.menu("endExperiment", data = self.data)
        

