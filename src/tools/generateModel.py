import pickle
import colors
import webExtractor as webE
import sys
sys.path.append('../class')
from experiment import *

def readModel(filename, maxTrials = 10):
    ''' return a list of experiment from json file'''
    model = dict()
    f = open(filename, 'rb')
    model = pickle.load(f)
    f.close()
        
    experiments = []
    id_ = 0
    for name, targets in model.items():
        experiments.append(Experiment(targets, name, id_, maxTrials = maxTrials))
        id_ += 1
    return experiments

def generateModel(urls, WIDTH, HEIGHT, filename = 'models.pkl', color = colors.BLACK, maxTrials = 10, displayInfo = True):
    '''Because retreiving the targets can take some time,
    the goal is to generate one time the models obtained from a dict with experience name as key and url as value
    return a list of experiment'''
    
    models = dict()
    
    for (exp_name, url) in urls.items():
        if not isinstance(url, str):
            raise Exception("url is not a string but is a "+url.__class__.__name__)
        if not isinstance(exp_name, str):
            raise Exception("experience name is not a string but is a "+exp_name.__class__.__name__)
        models[url] = webE.getTargetsFromUrl(url, WIDTH, HEIGHT, color, displayInfo)
        
    with open(filename, 'ab') as f:
        pickle.dump(models, f)
    
    experiments = []
    id_ = 0
    for name, targets in models.items():
        experiments.append(Experiment(targets, name, id_, maxTrials = maxTrials))
        id_ += 1
    
    return experiments
