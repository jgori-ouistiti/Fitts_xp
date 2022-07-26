from os import walk
import sys
import json
import matplotlib.pyplot as plt

def readJsonData(filename):
    f = open(filename,'r')
    res = json.load(f)
    f.close()
    return res
    
def readDirectory(directory):
    res = []
    filenames = next(walk(directory), (None, None, []))[2]  # [] if no file
    for file in filenames:
        file = directory+file
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

def main():
    data = readDirectory('../users_data/saved/')
    for exp in data:
        try:
            resolution = exp["display_screen"]
            xmax = resolution[0]
            ymin = -resolution[1]
            print(xmax, ymin)
            plotData(exp, xmin = 0, ymin = ymin, xmax = xmax, ymax = 0)
        except:
            print("Could not find one experiment for user_id :",exp['user_id'])
    #print("Trajectories for user_id :",data[0]["user_id"]," are :",getTrajectories(data[0]))
if __name__ =='__main__':
    main()
