import matplotlib.pyplot as plt
import os
from pvplib.chi20_lib import *
import numpy
from make_tex import *
import sys

import argparse



plt.style.use(["latex"])

SHOW_FLAG = 1

WIDTH_SCREEN = 1920
HEIGHT_SCREEN = 1080

data_path = "/home/jgori/Documents/Python/CHI_20_py/experiment/experiment_three/scripts/data/"

try:
    parser = argparse.ArgumentParser()
    parser.add_argument("PNumber", help="Participant Number",type=int)
    args = parser.parse_args()
    p_number = args.PNumber
    _file = "XP_3_P" + str(p_number) + ".csv"
    _files = [_file]
except IndexError:
    os.chdir(data_path)
    _files = os.listdir()


for _file in _files:
    containers = []
    cmpt = 0
    conditions = []
    with open(data_path + _file, 'r') as tmp_f:
        for i,_line in enumerate(tmp_f):
            _words = _line.split(',')
            if i == 0:
                _part = int(float(str(_words[1]).split(' ')[-1]))
                print("Working on Participant {}".format(_part))
            else:
                if _words[0] == 'Condition':
                    cmpt += 1
                    _D, _ID, _W = _words[1:-1]
                    conditions.append([_D, _ID, _W])
                    container = PVP_Gauss([_part, _D, _ID, _W])


                else:
                    if _words[0] == 'x=':
                        u = [float(u) for u in _words[1:]]
                    elif _words[0] == 'y=':
                        v = [float(u) for u in _words[1:]]
                    elif _words[0] == 't=':
                        w = [float(u) for u in _words[1:]]
                        container.add_2D_traj_raw(u,v,w, 3, WIDTH_SCREEN/2, HEIGHT_SCREEN/2, correct_start = "yes")


    container.pvp_routine(3, 10)
    print('removed {}'.format(container.removed))

    # for i in range(1,7):
    #     exec("print(container" + str(i)+".tau)")






    pvp = PVP_container(_part, [container])


    fig = plt.figure()
    ax1 = fig.add_subplot(231)
    container.plot_traj_extend(ax1)
    plt.tight_layout()

    if SHOW_FLAG:
        plt.show()
    plt.close()

    fig = plt.figure()
    ax1 = fig.add_subplot(231)

    container.plot_stdprofiles(ax1)

    plt.tight_layout()


    if SHOW_FLAG:
        plt.show()
    plt.close()
