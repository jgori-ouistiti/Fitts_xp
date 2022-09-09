
from game import *
from cibleRect import *
import sys
sys.path.append('../tools')
import colors as Colors
import random
import time

class Experiment :
    def __init__(self, targets, exp_name, exp_id, maxTrials = 20, dx_sens = 1, dy_sens = 1, cursor = None, noPause = False, default_cursor = True, input_device = None):
        print("Creating experiment \""+ exp_name+ "\" with cursor =",cursor)
        self.targets  = targets
        
        self.data = dict() #contains all user's data ,for this one experiment, about mouse tracking, time, etc...
        self.data['exp_name'] = exp_name
        self.data['exp_id']   = exp_id
        self.input_device = input_device
        
        if input_device != None:
            self.data['input_device'] = input_device
        if targets == None:
            self.data['number_of_targets'] = 0
        else:
            self.data['number_of_targets'] = len(targets)
        self.data['trials'] = dict()
        
        self.maxTrials = maxTrials
        self.noPause = noPause #At the end of the experiment, skip the pause and directly begin next experiment if set to True
        
        tmp = time.time()
        
        self.startOfTrial = tmp
        self.previous_time = tmp
        
        if self.maxTrials < 0:
            raise Exception("maxTrials must be positive")
        
        self.trial_id    = 0
        
        #Cursor sensitibility for the experiment
        self.cursor = cursor
        
        self.default_cursor = default_cursor
        
        self.dx_sens = dx_sens
        self.dy_sens = dy_sens
        
    def set_x_sensibility(self, dx_sens):
        self.dx_sens = dx_sens
        
    def set_y_sensibility(self, dy_sens):
        self.dy_sens = dy_sens
        
    def iterateData(self, game):
        '''do one iteration each click and add mouth tracks and time to self.trials'''
        actual_time = time.time()
        
        trialTime = actual_time - self.startOfTrial
        timeFromPrev = actual_time - self.previous_time
        self.previous_time = actual_time
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
        self.data['trials'][self.trial_id]['time from start'] = trialTime
        self.data['trials'][self.trial_id]['time from previous clic'] = timeFromPrev
        self.data['trials'][self.trial_id]['mouse_tracks'] = cursor_tracks
        
    def assignRandomTarget(self, game):
        game.assignRandomTarget()
        
    def correct_clic(self, game):
        #Nothing here, used for child of Experiment
        return
        
    def last_call(self, game):
        #Nothing here, used for child of Experiment
        #It is called when ending the experiment
        return
        
    def init_begin(self, game):
        #Nothing here, used for child of Experiment
        #It is called when ending the experiment
        return

    def begin(self, game):         
        '''Start the experience
        WARNING : we can pause the experience so we can exit this method at any time
        We must use trial variable to know where we are on the experiment
        '''
        
        self.init_begin(game)
        
        if not self.default_cursor :
            cursor_save = game.cursor
            game.cursor = self.cursor
        
        if game.cursor != None:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
        
        if self.targets == None or self.targets == []:
            raise Exception("Experiment has no target initialized")
        
        self.data['cursor_x_sensibility'] = self.dx_sens
        self.data['cursor_y_sensibility'] = self.dy_sens
        
        running = True
        
        game.listTarget = targets = self.targets
        game.addListenerDrawable(self.targets)
        
        self.assignRandomTarget(game)
        
        game.cursor_position = []
        
        self.startOfTrial = time.time()
        self.previous_time = self.startOfTrial
        
        while (running and self.trial_id < self.maxTrials):
            
            pygame.mouse.set_pos = (game.width/2, game.height/2)
            
            game.cursorMove()
            game.refreshScreen(True)
            if game.cursor != None:
                game.cursor.draw(game)

            ev = pygame.event.get()
            for event in ev:
            
                L = game.listen(event)
                
                if event.type == pygame.QUIT:
                    self.last_call(game)
                    if not self.default_cursor :
                        game.cursor = cursor_save
                    game.menu("quit", data = self.data)
                    return game.quitApp()
                    
                #collect mouse position
                if event.type == pygame.USEREVENT:
                    #Tracking mouse position
                    game.cursor_position.append(game.getCursorPos())
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        #Reset the cursor sensibility back to previous settings
                        pygame.mouse.set_visible(True)
                        game.removeListenerDrawable(targets)
                        if game.menu("pause") == -1: #quitting app because user closed game during pause menu
                            print("QUITTING APP")
                            game.menu("quit", data = self.data)
                            return game.quitApp()
                        game.addListenerDrawable(self.targets)
        
                if ("cible",True) in L:#On a cliqué sur une cible
                
                    self.iterateData(game)
                
                    self.correct_clic(game)
                    
                    game.assignRandomTarget()
                
                    self.trial_id += 1
                
                    game.score += 1
                        
                    #Saving the tracking of mouse
                    game.cursor_position_list.append(game.cursor_position)
                    game.cursor_position = []
                
                elif ("not cible",False) in L: #On n'a pas cliqué sur la bonne cible
                    game.score += -1
                    
        #End of the experiment
        #Reset the cursor sensibility back to previous settings
        game.removeListenerDrawable(targets)
        self.last_call(game)
        if not self.default_cursor :
            game.cursor = cursor_save
        game.menu("endExperiment", data = self.data, noPause = self.noPause)
        

