import sys
import json
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
import re
from pvplib.chi20_lib import *

import argparse

from PyQt5.QtWidgets import (
                        QWidget,
                        QApplication,
                        QMainWindow,
                        QVBoxLayout,
                        QScrollArea,
                    )

from matplotlib.backends.backend_qt5agg import (
                        FigureCanvasQTAgg as FigCanvas,
                        NavigationToolbar2QT as NabToolbar,
                    )

matplotlib.use('Qt5Agg')

def readJsonData(filename):
    f = open(filename,'r')
    res = json.load(f)
    f.close()
    return res
    
def readDirectory(directory, fusion = False):
    res = []
    filenames = next(os.walk(directory), (None, None, []))[2]  # [] if no file
    for file in filenames:
        file = directory+file
        if fusion:
            if file[-12:] == '_fusion.json':
                try:
                    res.append(readJsonData(file))
                except Exception:
                    print('Could not read file \"'+file+'\"')
        else:
            if file[-5:] == '.json':
                try:
                    res.append(readJsonData(file))
                except Exception:
                    print('Could not read file \"'+file+'\"')
    return res
    
def getTrajectories(data):
    trajectories = []
    clicks = []
    if 'experiments' in data:
        for exp_id in data['experiments']:
            trajectory = []
            click = []
            trials = data['experiments'][exp_id]['trials']
            for trial_id in trials.keys():
                try:
                    trajectory += trials[trial_id]['mouse_tracks']
                    click.append(trials[trial_id]['mouse_tracks'][-1])
                except KeyError:
                    print("No mouse tracks for trial ID : "+trial_id)
                    continue
            clicks.append(click)
            trajectories.append(trajectory)
    elif 'trials' in data:
        trials = data['trials']
        for trial_id in trials.keys():
            try:
                trajectory = trials[trial_id]['mouse_tracks']
                trajectories += trajectory
                clicks.append(trials[trial_id]['mouse_tracks'][-1])
            except KeyError:
                print("No mouse tracks for trial ID : "+trial_id)
                continue
    return trajectories, clicks
    
def plotTrajectory(trajectories,click = None, labels = [], xmin = 0, ymin = -1080, xmax = 1920, ymax = 0):
    isOneTrajectory = False
    try :
        tmp = len(trajectories[0][0])
    except TypeError:
        isOneTrajectory = True
    except IndexError:
        return
    tmp = trajectories
    if isOneTrajectory:
        tmp = [tmp]
    for i in range(len(tmp)):
        X = list(map(lambda x: x[0], tmp[i]))
        Y = list(map(lambda x: -x[1], tmp[i]))
        plt.plot(X,Y)
        if click != None and click[i] != None:
            X_click = list(map(lambda x: x[0], click[i]))
            Y_click = list(map(lambda x: -x[1], click[i]))
            plt.scatter(X_click, Y_click)
        
    plt.title("Trajectory for experiment")
    print("LEGENDS : ",labels)
    plt.legend(labels)
    plt.xlim(xmin, xmax)
    plt.ylim(ymin,ymax)
    plt.show()
    
def plotData(data,xmin = 0, ymin = -1080, xmax = 1920, ymax = 0):
    trajectories, clicks = getTrajectories(data)
    labels = []
    for id_ in data['experiments'].keys():
        labels.append("Trajectory for "+data['experiments'][id_]['exp_name'])
        labels.append("  Clicks   for   "+data['experiments'][id_]['exp_name'])
    plotTrajectory(trajectories, click = clicks, labels = labels, xmin = xmin, xmax = xmax, ymin = ymin, ymax = ymax)

def getDistancesByName(data):
    RES = dict()
    for exp in data:
        for id_ in exp['experiments'].keys():
            exp_name = exp['experiments'][id_]['exp_name']
            if not exp_name in RES:
                RES[exp_name] = dict()
                RES[exp_name]['occurrence'] = 1
                RES[exp_name]['distances'] = []
            else:
                RES[exp_name]['occurrence'] += 1
            id_of_exp = RES[exp_name]['occurrence'] - 1
            #Collecting data on movements, first click defined the starting point
            source_pos = exp['experiments'][id_]['trials']['0']['pos_target']
            for i in range(1, len(exp['experiments'][id_]['trials'])):
                movement = exp['experiments'][id_]['trials'][str(i)]
                distance = []
                for tick in range(0,len(movement['mouse_tracks'])):
                    cursor_pos = movement['mouse_tracks'][tick]
                    distXY = list(map(lambda x1, x2 : abs(x1 - x2), source_pos, cursor_pos))
                    distance.append(math.sqrt(math.pow(distXY[0],2) + math.pow(distXY[1],2) ))
                source_pos = movement['pos_target']
                RES[exp_name]['distances'].append(distance)
    return RES
    
def plotDistancesByName(data):

    DIST = getDistancesByName(data)

    X = np.arange(0., 1.5, 0.01)
    cpt = 0
    for exp_name in DIST:
        plt.figure()
        plt.title(exp_name)
        for distances in DIST[exp_name]['distances']:
            len_ = min(100,len(distances))
            Y = distances[:len_]
            last_y = Y[-1] #setting a constant function after 1 seconds
            Y += [last_y]*(len(X)-len(Y))
            plt.plot(X, Y)
        cpt = (cpt+1) % 5
        if cpt == 0:
            plt.show()
    plt.show()

