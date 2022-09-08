import matplotlib.pyplot as plt
import os
from pvplib.chi20_lib import *
import numpy
from make_tex import *
import sys
import argparse
import parsmovelib

plt.style.use(["latex"])

SHOW_FLAG = 0
EXPORT_FLAG = 1
WRITE_FLAG = 1

def neg(x):
    return [-u for u in x]

W = ['3.', '5.', '12.', '20.', '51.', '85.', '255.', '425.']

os.chdir("/home/jgori/Documents/Python/DataSets/PointingDynamicsDataset/data/")
_folders = os.listdir()

# pix to mm
DISTANCE_CONVERSION_CONDITIONS = 0.277/1000
DISTANCE_CONVERSION = 0.264583333/1000

containers = []
cmpt = 0
conditions = []


for _folder in _folders:
    npart = int(float(_folder[1:]))

    # if npart != 1:
    #     continue

    print("working on participant "+str(npart))

    os.chdir("/home/jgori/Documents/Python/DataSets/PointingDynamicsDataset/data/" + _folder + "/")
    _files = os.listdir()
    for _file in _files:
        for w in W:
            if w in _file:
                ncond = W.index(w)+1

        _words = _file.split(',')

        w_trial = float(_words[3][:-4])*DISTANCE_CONVERSION_CONDITIONS
        d_trial = float(_words[2])*DISTANCE_CONVERSION_CONDITIONS


        _D, _ID, _W = d_trial, math.log(1 + d_trial/w_trial,2), w_trial
        print("conditions")
        print(_D, _ID, _W)
        conditions.append([_D, _ID, _W])
        exec('container'+str(ncond)+' = PVP([npart, _D, _ID, _W])')
        with open("/home/jgori/Documents/Python/DataSets/PointingDynamicsDataset/data/" + _folder + "/" + _file,'r') as tmp_f:
            _words = tmp_f.readline().split(',')

            # print(_words[15],_words[16],_words[24], _words[28],_words[29], _words[30], _words[31], _words[32], _words[33])
            # exit()
            timestamps = []
            _width = []
            _dist = []
            _pos = []
            _spd = []
            _acc = []
            _button = []
            for _line in tmp_f:
                _words = _line.split(',')
                timestamps.append(float(_words[24]))
                _width.append(float(_words[29]))
                _dist.append(float(_words[30]))
                _pos.append(float(_words[15])*DISTANCE_CONVERSION)
                _spd.append(float(_words[32]))
                _acc.append(float(_words[33]))
                _button.append(float(_words[16]))

        _mean = numpy.mean(_pos)
        _abs = [min(timestamps),max(timestamps)]


        timestamps = numpy.array(timestamps)
        _pos = numpy.array(_pos)
        _spd = numpy.array(_spd)

        ## Skip first and last movements


        _normalize = lambda x: numpy.divide(x-numpy.mean(x),numpy.std(x))

        normpos = _normalize(_pos)
        normspeed = _normalize(_spd)
        normacc = _normalize(_acc)



        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        # ax.plot(timestamps, _pos, '-')
        # plt.show()
        # exit()
        # ax.plot(timestamps, normpos, '-')
        # ax.plot(timestamps, normspeed, '-')
        #
        # ax.plot(timestamps, normacc, '-')



        _movs = multitraj_get_movs(_pos, trim = [1,-1])
        # ax.plot(timestamps[_movs], normpos[_movs], '*')

        starts_both = multitraj_get_starts(timestamps, _pos, _spd, threshold = 5e-2, multitraj_type = 'both')
        # ax.plot(timestamps[starts_both], _pos[starts_both], 'D')
        # plt.show()
        # plt.exit()
        # if npart == 11:
        #     print(starts_both)


        starts_both = starts_both[1:]
        for i,v in enumerate(starts_both[:-1]):
            _time = timestamps[v:starts_both[i+1]]
            if len(_time) < 5:
                print("movement too short, dropping")
                continue
            # if _time[-1]-_time[0] > 5 or _time[-1]-_time[0] < 0.1:
            #     print(starts_both)
            #     print(v)
            #     print(starts_both[i+1])
            #     fig = plt.figure()
            #     ax = fig.add_subplot(111)
            #     ax.plot(timestamps, normpos, '-')
            #     ax.plot(timestamps, normspeed, '-')
            #     ax.plot(timestamps[v], normpos[v], '*')
            #     ax.plot(timestamps[starts_both[i+1]], normpos[starts_both[i+1]], '*')
            #     exit()

            pos = normpos[v:starts_both[i+1]]
            speed = normspeed[v:starts_both[i+1]]

            # try:
            first_zero, last_dwell_begin, last_dwell_mid, last_dwell_end, first_dwell_mid, mid_longest_dwell, plateaux = get_stop(_time, pos, speed, _thresh = 1e-2)
            # except IndexError:
            #     print(starts_both)
            #     exit()

            first_zero, last_dwell_begin, last_dwell_mid, last_dwell_end, first_dwell_mid, mid_longest_dwell, plateaux = first_zero + v, last_dwell_begin + v, last_dwell_mid + v, last_dwell_end + v, first_dwell_mid + v, mid_longest_dwell + v, plateaux

            u = _pos[v:last_dwell_begin].tolist()
            w = timestamps[v:last_dwell_begin].tolist()

            # fig = plt.figure()
            # ax = fig.add_subplot(111)
            # ax.plot(w, u, '-')
            # plt.show()
            # exit()
            try:
                if abs((1920/2)*DISTANCE_CONVERSION+_D/2 - u[-1]) > abs((1920/2)*DISTANCE_CONVERSION-_D/2 - u[-1]):
                    _target = (1920/2 )*DISTANCE_CONVERSION - _D/2
                else:
                    _target = (1920/2 )*DISTANCE_CONVERSION + _D/2
            except IndexError:
                fig = plt.figure()
                ax = fig.add_subplot(111)
                ax.plot(timestamps, normpos, '-')
                ax.plot(timestamps, normspeed, '-')
                ax.plot(timestamps[v], normpos[v], '*')
                plt.show()
                plt.close()
            try:
                exec('container'+ str(ncond) +'.add_1D_traj_raw(u,w, 3,_target, correct_start = "yes")')
            except IndexError:
                print("warning indexError when adding trajectory ")
            except ValueError:
                print("warning valueError when adding trajectory ")






            # ax.plot(timestamps[first_zero], normpos[first_zero], '*')
            # ax.plot(timestamps[last_dwell_begin], normpos[last_dwell_begin], '*')
            # ax.plot(timestamps[last_dwell_mid], normpos[last_dwell_mid], '*')
            # ax.plot(timestamps[last_dwell_end], normpos[last_dwell_end], '*')
            # ax.plot(timestamps[first_dwell_mid], normpos[first_dwell_mid], '*')
            # ax.plot(timestamps[mid_longest_dwell], normpos[mid_longest_dwell], '*')

        # plt.show()
        # plt.close()


        #
        #
        # first_zero, last_dwelling, score_based, final, mid, first_dwell_mid, plat = parsmovelib.find_stop(timestamps, _pos, norm(_spd), _movs, _thresh = 1e-2, index = True)
        # print(_movs)
        # print(starts)
        # print(final)
        #
        #
        #
        # neg_movs = parsmovelib.find_movs(timestamps, neg(_pos), trim = [1,-1])
        # negstarts = parsmovelib.find_start(timestamps, neg(_pos), norm(neg(_spd)), neg_movs, thresh = 1e-2, index = True)
        # neg_first_zero, neg_start_last_dwell, neg_mid_longest_dwell, neg_end_last_dwell, neg_mid_last_dwell, neg_first_dwell_mid, neg_plateaux = parsmovelib.find_stop(timestamps, neg(_pos), norm(neg(_spd)), neg_movs, _thresh = 1e-3, index = True, plateau = True)


#         for i,v in enumerate(starts):
#             u = _pos[v:final[i]].tolist()
#             w = timestamps[v:final[i]].tolist()
#             try:
#                 exec('container'+ str(ncond) +'.add_1D_traj_raw(u,w, 3,1920/2+_D/2, correct_start = "yes")')
#             except IndexError:
#                 print(u,w)
#         for i,v in enumerate(negstarts):
#             u = _pos[v:neg_end_last_dwell[i]].tolist()
#             w = timestamps[v:neg_end_last_dwell[i]].tolist()
#             exec('container'+ str(ncond) +'.add_1D_traj_raw(u,w, 3,1920/2 -_D/2, correct_start = "yes")')
#
#
#
#
#
#
        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        # container7.plot_traj_raw(ax)
        # plt.show()
        # exit()


    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # container1.plot_traj_extend(ax)
    # plt.show()
    # exit()

    for i in range(1,9):
        # print(i)
        exec("container" + str(i)+".pvp_routine(4,10)")
        # exec("print(container" + str(i)+".pvp_params[1])")
    # exec("print('removed {}'.format(container"+str(i)+".removed))")
    # for i in range(1,9):
    #     exec("print(container" + str(i)+".tau)")
#
#
#
    ## Setting Up Latex file
    if WRITE_FLAG:
        latex_path = "/home/jgori/Documents/Python/CHI_20_py/pvps_in_hci/mueller_pddataset/latex/P" + str(npart) + ".tex"
        tex_file_init(latex_path)

#
#
    # for i in range(1,9):
    #     fig = plt.figure()
    #     ax = fig.add_subplot(121)
    #     ax2 = fig.add_subplot(122)
    #     exec("container"+str(i)+".plot_traj_raw(ax)")
    #     exec("container"+str(i)+".plot_traj_extend(ax2)")
    #     plt.show()
    #     plt.close()

    print("Entering Fitts")
    fitts = FITTS_single(npart, [container1, container2, container3, container4, container5, container6, container7, container8])

    print(fitts.conditions)


    if WRITE_FLAG:
        fitts.make_table_summary(latex_path)

#
    fig = plt.figure()
    ax = fig.add_subplot(111)
    fitts.plot_fitts(ax)
    fig_str = "/home/jgori/Documents/Python/CHI_20_py/pvps_in_hci/mueller_pddataset/latex/fig/fitts_p{}.pdf".format(npart)
    plt.savefig(fig_str)
    if WRITE_FLAG:
        tex_add_fig(latex_path, "fitts_p{}.pdf".format(npart), caption = 'Fitts plot for Participant {}'.format(npart))
    if SHOW_FLAG:
        plt.show()
    plt.close()
#
#
    pvp = PVP_container(npart, [container1, container2, container3, container4, container5, container6, container7, container8])
#
    if EXPORT_FLAG:
        EXPORT_PATH = "/home/jgori/Documents/Python/CHI_20_py/pvps_in_hci/mueller_pddataset/analysis/dataframes/P" + str(npart) + ".pkl"
        df = pvp.dataframe
        df.to_pickle(EXPORT_PATH)
#
    fig = plt.figure()
    ax1 = fig.add_subplot(241)
    ax2 = fig.add_subplot(242)
    ax3 = fig.add_subplot(243)
    ax4 = fig.add_subplot(244)
    ax5 = fig.add_subplot(245)
    ax6 = fig.add_subplot(246)
    ax7 = fig.add_subplot(247)
    ax8 = fig.add_subplot(248)
    container1.plot_traj_extend(ax1)
    container2.plot_traj_extend(ax2)
    container3.plot_traj_extend(ax3)
    container4.plot_traj_extend(ax4)
    container5.plot_traj_extend(ax5)
    container6.plot_traj_extend(ax6)
    container7.plot_traj_extend(ax7)
    container8.plot_traj_extend(ax8)
    plt.tight_layout()
#
    fig_str = "/home/jgori/Documents/Python/CHI_20_py/pvps_in_hci/mueller_pddataset/latex/fig/traj_p{}.pdf".format(npart)
    plt.savefig(fig_str)
    if WRITE_FLAG:
        tex_add_fig(latex_path, "traj_p{}.pdf".format(npart), caption = 'Mean Trajectories plot for Participant {}'.format(npart))
    if SHOW_FLAG:
        plt.show()
    plt.close()

    fig = plt.figure()
    ax1 = fig.add_subplot(241)
    ax2 = fig.add_subplot(242)
    ax3 = fig.add_subplot(243)
    ax4 = fig.add_subplot(244)
    ax5 = fig.add_subplot(245)
    ax6 = fig.add_subplot(246)
    ax7 = fig.add_subplot(247)
    ax8 = fig.add_subplot(248)
    container1.plot_stdprofiles(ax1)
    container2.plot_stdprofiles(ax2)
    container3.plot_stdprofiles(ax3)
    container4.plot_stdprofiles(ax4)
    container5.plot_stdprofiles(ax5)
    container6.plot_stdprofiles(ax6)
    container7.plot_stdprofiles(ax7)
    container8.plot_stdprofiles(ax8)
    plt.tight_layout()

    fig_str = "/home/jgori/Documents/Python/CHI_20_py/pvps_in_hci/mueller_pddataset/latex/fig/pvp_p{}.pdf".format(npart)
    plt.savefig(fig_str)
    if WRITE_FLAG:
        tex_add_fig(latex_path, "pvp_p{}.pdf".format(npart), caption = 'PVP plot for Participant {}'.format(npart))
    if SHOW_FLAG:
        plt.show()
    plt.close()
#
#
#
    if WRITE_FLAG:
        pvp.dataframe_to_latex(latex_path)
        ## Closing latex file
        tex_file_end(latex_path)
