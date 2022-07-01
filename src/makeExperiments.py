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

class CircleRandomExp(Experiment):
    def __init__(self, width, height, exp_name, exp_id, maxTrials = 20, target_radius = 20, distance = 300,dx_sens = 1, dy_sens = 1, target_color = Colors.RED, buffer = 30):
        super().__init__(None, exp_name, exp_id, maxTrials = maxTrials, dx_sens = dx_sens, dy_sens = dy_sens)
        self.target_radius = target_radius
        self.target_color  = target_color
        self.distance = distance
        self.buffer = buffer # add marges on the edges of the screen for targets
        self.width = width
        self.height = height
        self.targets =  [Cible( (int(width/2),int(height/2)), self.target_radius, target_color, isTarget = True)]
        self.data['number_of_targets at each time'] = 1
        self.data['distance of next target'] = distance
        
    def correct_clic(self, game):
        #Overide super method correct_clic. Called when clicking on the target
        
        #Collecting info on actual target
        x = self.targets[0].x
        y = self.targets[0].y
        r = self.targets[0].r
        
        #Creating a new target based on position of actual target
        theta = random.uniform(0,2*math.pi)
        new_x = int(x + self.distance * math.cos(theta))
        new_y = int(y + self.distance * math.sin(theta))
        #Checking is new target will be outside of screen, and in a safe area (not in the edges)
        marge = self.buffer + self.target_radius
        cpt = 0
        while(new_x < marge or new_x > self.width - marge or new_y < marge or new_y > self.height - marge):
            theta += math.pi/5 #moving in a math.pi/5 degree angle
            new_x = int(x + self.distance * math.cos(theta))
            new_y = int(y + self.distance * math.sin(theta))
            cpt += 1
            if cpt > 20:
                raise Exception("Error , could not place the next target as it's always out of the screen. Check width, height and distance.")
        #Assigning next target
        target = Cible((new_x, new_y), self.target_radius, self.target_color, isTarget = True)
        game.removeListenerDrawable(self.targets[0])
        game.addListenerDrawable(target)
        game.active_target = target
        game.listTarget = [target]
        self.targets = [target]
        
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
