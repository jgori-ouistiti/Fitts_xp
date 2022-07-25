import sys
import random
import math
sys.path.append('./tools')
sys.path.append('./class')
from drawable import *
from game import *
from cible import *
from target_disposition import *
from healthBar import *
from experiment import *
import colors as Colors
import pickle

#-------------------------RANDOM TARGETS WITH SAME DISTANCE EVERY HIT CLASS
class CircleRandomExp(Experiment):
    '''One target at a time on screen.
       When clicking on a target, a new one appear on a constant distance from the previous one.
    '''
    def __init__(self, width, height, exp_name, exp_id = 0, maxTrials = 20, target_radius = 20, distance = 300,dx_sens = 1, dy_sens = 1, target_color = Colors.RED, buffer = 30, cursor = None, noPause = False):
        super().__init__([], exp_name, exp_id, maxTrials = maxTrials, dx_sens = dx_sens, dy_sens = dy_sens, cursor = cursor, noPause = noPause)
        
        #init target_info
        self.target_info = {"radius" : target_radius, "distance": distance, "isRadiusList" : False, "isDistanceList": False}
        #Radius
        if isinstance(target_radius, list):
            self.target_info["isRadiusList"]=True #Boolean = is it a list ? (True),
            self.target_info["indexRadius"] = 0 #index of the radius of next target
            if len(self.target_info["radius"]) <= 1:
                raise Exception("Error: Radius for targets is set as a list but there isn't 2 or more elements in the list. "\
                +"If you want to use one generic value, use just an int an not a list.")
        #Distance
        if isinstance(distance, list):
            self.target_info["isDistanceList"]=True #Boolean = is it a list ? (True),
            self.target_info["indexDistance"] = 0 #index of the radius of next target
            if len(self.target_info["distance"]) <= 1:
                raise Exception("Error: Distance for targets is set as a list but there isn't 2 or more elements in the list. "\
                +"If you want to use one generic value, use just an int an not a list.")        
        #---------
        self.target_color  = target_color
        self.distance = distance
        self.buffer = buffer # add marges on the edges of the screen for targets
        self.width = width
        self.height = height
        
        #Initializing first target
        if self.target_info["isRadiusList"]:
            self.targets =  [Cible( (int(width/2),int(height/2)), self.target_info["radius"][0], target_color, isTarget = True)]
        else:  
            self.targets =  [Cible( (int(width/2),int(height/2)), self.target_info["radius"], target_color, isTarget = True)]
        self.data['number_of_targets at each time'] = 1
        self.data['distance of next target'] = distance
        self.data["width"] = width
        self.data["height"] = height
        
    def correct_clic(self, game):
        #Overide super method correct_clic. Called when clicking on the target
        
        #Collecting info on actual target
        x = self.targets[0].x
        y = self.targets[0].y
        r = self.targets[0].r
        
        #Creating a new target based on position of actual target
        theta = random.uniform(0,2*math.pi)
        if self.target_info["isDistanceList"]:
            new_x = int(x + self.target_info["distance"][self.target_info["indexDistance"]] * math.cos(theta))
            new_y = int(y + self.target_info["distance"][self.target_info["indexDistance"]] * math.sin(theta))
        else:
            new_x = int(x + self.distance * math.cos(theta))
            new_y = int(y + self.distance * math.sin(theta))
        #Checking is new target will be outside of screen, and in a safe area (not in the edges)
        if self.target_info["isRadiusList"]:
            marge = self.buffer + self.target_info["radius"][self.target_info["indexRadius"]]
        else:
            marge = self.buffer + self.target_info["radius"]
        cpt = 0
        while(new_x < marge or new_x > self.width - marge or new_y < marge or new_y > self.height - marge):
            theta += math.pi/5 #moving in a math.pi/5 degree angle
            if self.target_info["isDistanceList"]:
                new_x = int(x + self.target_info["distance"][self.target_info["indexDistance"]] * math.cos(theta))
                new_y = int(y + self.target_info["distance"][self.target_info["indexDistance"]] * math.sin(theta))
            else:
                new_x = int(x + self.distance * math.cos(theta))
                new_y = int(y + self.distance * math.sin(theta))
            cpt += 1
            if cpt > 20:
                raise Exception("Error , could not place the next target as it's always out of the screen. Check width, height and distance.")
                
        #Assigning next target
        radius = None
        
        #Incrementing index of radius list
        if self.target_info["isRadiusList"]:
            self.target_info["indexRadius"] += 1
            if self.target_info["indexRadius"] == len(self.target_info["radius"]): #looping index back to zero
                self.target_info["indexRadius"] = 0
        
        #using new variable to get the actual next radius 
        if self.target_info["isRadiusList"]:
            radius = self.target_info["radius"][self.target_info["indexRadius"]]
        else:
            radius = self.target_info["radius"]
            
        #Incrementing index of distance list
        if self.target_info["isDistanceList"]:
            self.target_info["indexDistance"] += 1
            if self.target_info["indexDistance"] == len(self.target_info["distance"]): #looping index back to zero
                self.target_info["indexDistance"] = 0
            
        target = Cible((new_x, new_y), radius, self.target_color, isTarget = True)
        
        game.removeListenerDrawable(self.targets[0])
        game.addListenerDrawable(target)
        game.active_target = target
        game.listTarget = [target]
        self.targets = [target]
        
    def last_call(self,game):
        #Remove the last target remaining at the end of the experiment
        game.removeListenerDrawable(self.targets[0])
        

#-------------------------TWO TARGETS EXPERIMENT CLASS  
class TwoTargetsExp(Experiment):
    '''Only two constant targets on screen
       Use a rad given in parameters to set the line where the two targets will be placed
       Use a distance in pixels to separate the two targets
    ''' 
    def __init__(self, width, height, exp_name, rad, distance, exp_id = 0, maxTrials = 20, target_radius = 20,dx_sens = 1, dy_sens = 1, target_color = Colors.GRAY, cursor = None, noPause = False):
        super().__init__([], exp_name, exp_id, maxTrials = maxTrials, dx_sens = dx_sens, dy_sens = dy_sens, cursor = cursor, noPause = noPause)
        
        #init target_info
        self.target_info = {"radius" : target_radius, "distance": distance, "isRadiusList" : False, "isDistanceList": False}
        #Radius
        if isinstance(target_radius, list):
            self.target_info["isRadiusList"]=True #Boolean = is it a list ? (True),
            self.target_info["indexRadius"] = 1 #index of the radius of next target
            if len(self.target_info["radius"]) <= 1:
                raise Exception("Error: Radius for targets is set as a list but there isn't 2 or more elements in the list. "\
                +"If you want to use one generic value, use just an int an not a list.")
        #Distance
        if isinstance(distance, list):
            self.target_info["isDistanceList"]=True #Boolean = is it a list ? (True),
            self.target_info["indexDistance"] = 1 #index of the radius of next target
            if len(self.target_info["distance"]) <= 1:
                raise Exception("Error: Distance for targets is set as a list but there isn't 2 or more elements in the list. "\
                +"If you want to use one generic value, use just an int an not a list.")        
        #---------f.target_info = {"isRadiusList" : False, "radius":target_radius} #Boolean = is it a list ? (False), target_radius = int, no index because target_radius isn't a list
        
        self.data['number_of_targets'] = 2
        self.data['distance of the two targets'] = distance
        self.data['radian of axe'] = rad
        self.data["width"] = width
        self.data["height"] = height
        
        #Initializing targets
        if self.target_info["isDistanceList"]:
            #target 1
            x1 = int(width/2 - (self.target_info["distance"][self.target_info["indexDistance"]]/2) * math.cos(rad))
            y1 = int(height/2 - (self.target_info["distance"][self.target_info["indexDistance"]]/2) * math.sin(rad))
            #target 2
            x2 = int(width/2 + (self.target_info["distance"][self.target_info["indexDistance"]]/2) * math.cos(rad))
            y2 = int(height/2 + (self.target_info["distance"][self.target_info["indexDistance"]]/2) * math.sin(rad))
        else :
            #target 1
            x1 = int(width/2 - (distance/2) * math.cos(rad))
            y1 = int(height/2 - (distance/2) * math.sin(rad))
            #target 2
            x2 = int(width/2 + (distance/2) * math.cos(rad))
            y2 = int(height/2 + (distance/2) * math.sin(rad))
        self.targets = []
        if self.target_info["isRadiusList"]:
            #creating targets with target_radius["radius"] as a list of radius
            self.targets.append(Cible((x1,y1), self.target_info["radius"][0], target_color, isTarget = True))
            self.targets.append(Cible((x2,y2), self.target_info["radius"][1], target_color, isTarget = False))
        else:
            #creating targets with target_radius[1] as one generic radius
            self.targets.append(Cible((x1,y1), self.target_info["radius"], target_color, isTarget = True))
            self.targets.append(Cible((x2,y2), self.target_info["radius"], target_color, isTarget = False))
            
        self.actual_target = self.targets[0]
        
    def swap_target(self, game):
    
        #Incrementing index of radius list
        if self.target_info["isRadiusList"]:
            self.target_info["indexRadius"] += 1
            if self.target_info["indexRadius"] == len(self.target_info["radius"]): #looping index back to zero
                self.target_info["indexRadius"] = 0
                
        if self.target_info["isDistanceList"]:
            #Incrementing index of distance list
            self.target_info["indexDistance"] += 1
            if self.target_info["indexDistance"] == len(self.target_info["distance"]): #looping index back to zero
                self.target_info["indexDistance"] = 0
            #target 1
            self.targets[0].x = int(self.data["width"]/2 - (self.target_info["distance"][self.target_info["indexDistance"]]/2) * math.cos(self.data["radian of axe"]))
            self.targets[0].y = int(self.data["height"]/2 - (self.target_info["distance"][self.target_info["indexDistance"]]/2) * math.sin(self.data["radian of axe"]))
            #target 2
            self.targets[1].x = int(self.data["width"]/2 + (self.target_info["distance"][self.target_info["indexDistance"]]/2) * math.cos(self.data["radian of axe"]))
            self.targets[1].y = int(self.data["height"]/2 + (self.target_info["distance"][self.target_info["indexDistance"]]/2) * math.sin(self.data["radian of axe"]))
            
        if self.targets[0] is self.actual_target :
            self.targets[0].isTarget = False
            if self.target_info["isRadiusList"]:
                self.targets[0].r = self.target_info["radius"][self.target_info["indexRadius"]]
            self.targets[1].isTarget = True
            self.actual_target = self.targets[1]
            game.active_target = self.targets[1]
        else:
            self.targets[0].isTarget = True
            self.targets[1].isTarget = False
            if self.target_info["isRadiusList"]:
                self.targets[1].r = self.target_info["radius"][self.target_info["indexRadius"]]
            self.actual_target = self.targets[0]
            game.active_target = self.targets[0]
            
        
    def begin(self, game):         
        '''Start the experience
        WARNING : we can pause the experience so we can exit this method at any time
        We must use trial variable to know where we are on the experiment
        
        Overide for custom assignRandomTarget
        '''
        
        if self.targets == None or self.targets == []:
            raise Exception("Experiment has no target initialized")
        
        self.data['cursor_x_sensibility'] = self.dx_sens
        self.data['cursor_y_sensibility'] = self.dy_sens
        
        running = True
        
        cursor_save = game.cursor
        game.cursor = self.cursor
        if game.cursor != None:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
        
        game.listTarget = targets = self.targets
        game.addListenerDrawable(self.targets)
        
        game.cursor_position = []
        
        self.startOfTrial = time.time()
        self.previous_time = self.startOfTrial
        
        game.active_target = self.targets[0]
        
        while (running and self.trial_id < self.maxTrials):
            
            pygame.mouse.set_pos = (game.width/2, game.height/2)
            
            game.refreshScreen(True)
            if self.cursor != None:
                self.cursor.draw(game)

            ev = pygame.event.get()
            for event in ev:
            
                L = game.listen(event)
                
                if event.type == pygame.QUIT:
                    game.menu("quit", data = self.data)
                    return game.quitApp()
                    
                #collect mouse position
                if event.type == pygame.USEREVENT:
                    #Tracking mouse position
                    game.cursor_position.append(game.getCursorPos())
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mouse.set_visible(True)
                        game.removeListenerDrawable(targets)
                        if game.menu("pause") == -1: #quitting app because user closed game during pause menu
                            print("QUITTING GAME")
                            game.menu("quit", data = self.data)
                            return game.quitApp()
                        game.addListenerDrawable(targets)
                if event.type == pygame.MOUSEMOTION:
                    game.cursorMove()
        
                if ("cible",True) in L:#On a cliqué sur une cible
                    self.swap_target(game)
                
                    self.correct_clic(game)
                    
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
        game.cursor = cursor_save
        game.removeListenerDrawable(targets)
        
        game.menu("endExperiment", data = self.data, noPause = self.noPause)

#-------------------------CIRCLE EXPERIMENT CLASS
class CircleExp(Experiment):
    '''Targets are displayed on an invisible circle centered in the middle of the screen.
    The target's order is specified and not random.
    Every time a target is hit, the next one is at the most opposite of the circle.'''
    
    def __init__(self, width, height, exp_name, nb_target, rad_circle, exp_id = 0, way_H = True, maxTrials = 20, target_radius = 20,dx_sens = 1, dy_sens = 1, target_color = Colors.GRAY, cursor = None, noPause = False):
        super().__init__([], exp_name, exp_id, maxTrials = maxTrials, dx_sens = dx_sens, dy_sens = dy_sens, cursor = cursor, noPause = noPause)
        self.data['number_of_targets'] = nb_target
        self.data['radius of the circle'] = rad_circle
        self.data["width"] = width
        self.data["height"] = height
        
        #Generation of the targets on a list. Next target is the next one in the list
        self.targets = []
        if way_H :
            delta_theta = math.pi / nb_target
        else: 
            delta_theta = - (math.pi / nb_target)
        theta = 0
        for i in range(nb_target):
            x,y = (0,0)
            if i%2 == 0:
                x = int(width/2  + rad_circle*math.cos(theta))
                y = int(height/2 + rad_circle*math.sin(theta))
            else:
                x = int(width/2  + rad_circle*math.cos(math.pi + theta ))
                y = int(height/2 + rad_circle*math.sin(math.pi + theta ))
            if i == 0:
                self.targets.append(Cible((x,y), target_radius, target_color, isTarget = True))
            else:
                self.targets.append(Cible((x,y), target_radius, target_color, isTarget = False))
            theta += delta_theta
        self.actual_target = (self.targets[0],0) #target object + id of the object in the list
        
    def swap_target(self, game):
        self.actual_target[0].isTarget = False
        if self.actual_target[1] + 1 == len(self.targets):
            self.actual_target = (self.targets[0], 0)
        else:
            index = self.actual_target[1] + 1
            self.actual_target = (self.targets[index], index)
        self.actual_target[0].isTarget = True
        game.active_target = self.actual_target[0]
    
    def begin(self, game):         
        '''Start the experience
        WARNING : we can pause the experience so we can exit this method at any time
        We must use trial variable to know where we are on the experiment
        
        Overide for custom assignRandomTarget
        '''
        
        if self.targets == None or self.targets == []:
            raise Exception("Experiment has no target initialized")
        
        self.data['cursor_x_sensibility'] = self.dx_sens
        self.data['cursor_y_sensibility'] = self.dy_sens
        
        running = True
        
        game.listTarget = targets = self.targets
        game.addListenerDrawable(self.targets)
        
        cursor_save = game.cursor
        game.cursor = self.cursor
        if game.cursor != None:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
        
        game.cursor_position = []
        
        self.startOfTrial = time.time()
        self.previous_time = self.startOfTrial
        
        game.active_target = self.targets[0]
        
        while (running and self.trial_id < self.maxTrials):
            
            pygame.mouse.set_pos = (game.width/2, game.height/2)
            
            game.refreshScreen(True)
            if self.cursor != None:
                self.cursor.draw(game)

            ev = pygame.event.get()
            for event in ev:
            
                L = game.listen(event)
                
                if event.type == pygame.QUIT:
                    game.menu("quit", data = self.data)
                    game.cursor = cursor_save
                    return game.quitApp()
                    
                #collect mouse position
                if event.type == pygame.USEREVENT:
                    #Tracking mouse position
                    game.cursor_position.append(game.getCursorPos())
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mouse.set_visible(True)
                        game.removeListenerDrawable(targets)
                        if game.menu("pause") == -1: #quitting app because user closed game during pause menu
                            print("QUITTING GAME")
                            game.menu("quit", data = self.data)
                            return game.quitApp()
                        game.addListenerDrawable(self.targets)
                if event.type == pygame.MOUSEMOTION:
                    game.cursorMove()
        
                if ("cible",True) in L:#On a cliqué sur une cible
                    self.swap_target(game)
                
                    self.correct_clic(game)
                    
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
        game.cursor = cursor_save
        game.removeListenerDrawable(targets)
        game.menu("endExperiment", data = self.data, noPause = self.noPause)
        
class DistractorExp(Experiment):
    def __init__(self, width, height, exp_name, nb_target, rad_circle, exp_id = 0, way_H = True, maxTrials = 20, target_radius = 20,dx_sens = 1, dy_sens = 1, target_color = Colors.GRAY, cursor = None, noPause = False):
        super().__init__([], exp_name, exp_id, maxTrials = maxTrials, dx_sens = dx_sens, dy_sens = dy_sens, cursor = cursor)
        self.data['number_of_targets'] = nb_target
        self.data['radius of the circle'] = rad_circle
        
def saveExperiment(exp, filename = ''):
    if not isinstance(exp, Experiment):
        raise Exception("exp must be an experiment")
        
    if filename == '':
        filename = type(exp).__name__ + '.pkl'
    
    with open(filename, 'ab') as f:
        pickle.dump(exp, f)
        
def loadExperiment(filename):
    f = open(filename, 'rb')
    experiment = pickle.load(f)
    f.close()
    if not isinstance(experiment, Experiment):
        raise Exception("file "+filename+" is not an Experiment file")
    return experiment
