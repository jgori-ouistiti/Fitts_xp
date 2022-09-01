import pickle as pkl

FILE = 'complete_experiment_design.pickle'
nb_of_movements = 21

def makeExperiments(data):
    for P, exps in data.items():
        experiment_file = ''
        id_fitts = 0
        id_pvp = 0
        for id_exp, exp in exps.items():
            for name in exp:
                for D, W in exp[name]:
                    D = int(D)
                    W = int(W)
                    
                    if name[-1] == 'A':
                        experiment_file += 'device mouse\n'
                    if name[-1] == 'B':
                        experiment_file += 'device touchpad\n'
                    if name[-1] == 'C':
                        experiment_file += 'device controller\n'
                        
                    if name[:5] == 'Fitts':
                        if id_fitts %2 == 0:
                            sens = ' AH'
                        else:
                            sens = ' H'
                        experiment_file += 'fitts_exp'+str(id_fitts)+' circle '+str(D) +' '+str(W)+' ' + str(nb_of_movements)+sens+'\n'
                        id_fitts += 1
                    elif name[:3] == 'PVP':
                        experiment_file += 'pvp_exp'+str(id_pvp)+' random '+str(D) +' 3 ' + str(nb_of_movements)+'\n'
                        id_pvp += 1
        file = open((P+'.txt'), 'w')
        file.write(experiment_file)
        file.close()
                    

def main():
    file = open(FILE,'rb')
    data = pkl.load(file)
    makeExperiments(data)
    file.close()
    return 0
    
if __name__ == '__main__':
    main()
