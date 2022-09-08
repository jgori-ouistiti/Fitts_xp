import sys
import json
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
import re
from pvplib.chi20_lib import *
from pvplib.data_parser import *

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

def main():
    #plt.style.use(["latex"])

    data_path = "/home/quentin/Cours/ANDROIDE_Project_HCI_Fitts2.0/users_data/saved/"
    datas = readDirectory(data_path)
   
    SHOW_ALL_FLAG = 0
    SHOW_FLAG = 0
    EXPORT_FLAG = 1
    WRITE_FLAG = 1
    
    # pix to mm
    #DISTANCE_CONVERSION_CONDITIONS = 9.5/1000
    #DISTANCE_CONVERSION = 9.5/1000
    DISTANCE_CONVERSION_CONDITIONS = 1
    
    W = [7.0, 9.0,13.0, 18.0, 33.0, 45.0, 62.0]
    
    def neg(x):
        return [-u for u in x]

    nb_data = len(datas)
    ndata   = 1
    
    for data in datas:
        print("\nOperating data : "+str(ndata)+'/'+str(nb_data)+' ...')
        #plotTrajectory(getTrajectories(data)[0])
        nb_files = len(data['experiments'])
        nfile = 1
        containers = []
        cmpt = 0
        conditions = []
        exp_names = []
        npart = data['user_id']
        WIDTH_SCREEN, HEIGHT_SCREEN = data['display_screen']
        
        for experiment in data['experiments'].values():
            exp_name = experiment['exp_name']
            exp_names.append(exp_name + ' with '+experiment['input_device'])
            exp_id = experiment['exp_id']
            print("\nexperiment "+str(nfile)+'/'+str(nb_files))
            print(exp_name)
            
            _W = None
            _D = None
            
            for s in exp_name.split(','):
                tmp = list(map(int, re.findall('\d+', s)))
                if 'r =' in s:
                    _W = tmp[0]
                if 'distance' in s:
                    _D = tmp[0]
                   
            if _W == None:
                raise Exception("Failed to parse W in experiment :"+exp_name)
            if _D == None:
                raise Exception("Failed to parse D in experiment :"+exp_name)
                    
            ncond = W.index(_W) + 1
            _ID = math.log(_D/_W + 1,2)
            
            print("conditions (D, ID, W)")
            print(_D, _ID, _W)
            print("ncond :",ncond)
            conditions.append([_D, _ID, _W])
            container = PVP_Project([npart, _D, _ID, _W])
            
            traj_x = []
            traj_y = []
            
            for trial in experiment['trials'].values():
                x = [v[0]*DISTANCE_CONVERSION_CONDITIONS for v in trial['mouse_tracks'][1:]] # We suppress the first movement because it is used to position the mouse
                y = [v[1]*DISTANCE_CONVERSION_CONDITIONS for v in trial['mouse_tracks'][1:]]
                #print('x:',x)
                #print('y:',y)
                t = np.arange(0, len(x)*0.01 + 0.01, 0.01)[:len(x)] # (... + 0.01, ...) and [:len(x)] used to prevent wrong size caused by numpy 
                
                tx, ty = [k * DISTANCE_CONVERSION_CONDITIONS for k in trial['pos_target']]
                
                container.add_2D_traj_raw_x(x, y, t,3,tx,ty)
                #plt.plot(x,y)
                #plt.show()
                traj_x += x
                traj_y += y
            
            #if 'Random' in exp_name:
            #    plt.plot(traj_x, traj_y)
            #    plt.show()
                
            
            container.pvp_routine(3)
            container._print_pvp_params()
            print('removed {}'.format(container.removed))
            fig = plt.figure()
            ax1 = fig.add_subplot(231)
            container.plot_traj_extend(ax1)
            plt.tight_layout()

            if SHOW_ALL_FLAG:
                plt.legend()
                plt.title(exp_name)
                plt.show()
                
            container.plot_stdprofiles(ax1)

            plt.tight_layout()


            if SHOW_ALL_FLAG:
                plt.show()
            plt.close()
            
            containers.append(container)
            nfile += 1
            
        if (EXPORT_FLAG):
            export_path = "/home/quentin/Cours/ANDROIDE_Project_HCI_Fitts2.0/data_extractor/"+str(npart)
            if not os.path.exists(export_path):
                os.makedirs(export_path)
            for i, c in enumerate(containers):
            
                file_name = export_path+'/'+str(i)
                
                if os.path.exists(file_name+'.png'):
                    file_name = export_path+'/'+str(i+20)
                pvp_container = PVP_container(npart, [c])
                fig = plt.figure()
                ax = fig.add_subplot(111)
                pvp_container.plot_all_pvps(ax,[''])
                plt.title(exp_names[i])
                plt.tight_layout()
                plt.savefig(file_name)
                plt.close()
            
        if (SHOW_FLAG) :
            print("Plotting all pvps")
            print("exp_id\tdevice\texp_name")
            for i , name in enumerate(exp_names):
                print(str(i)+'\t'+name)
            pvp_container = PVP_container(npart, containers)
            
            fig = plt.figure()
            ax1 = fig.add_subplot(111)
            
            pvp_container.plot_all_pvps(ax1,['exp_id' + str(i) for i in range(len(containers))])
            plt.tight_layout()
            plt.legend()
            plt.title("PVPs for participant "+str(npart))
        ndata += 1
    if (SHOW_FLAG):
        plt.show()
    ######################################################################################

        
if __name__ == '__main__':
    sys.exit(main())


