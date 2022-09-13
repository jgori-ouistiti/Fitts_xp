import sys
import json
import pandas
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
import re
import pickle as pkl
from pvplib.chi20_lib import *
from pvplib.data_parser import *
from fusion import *

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

matplotlib.use("Qt5Agg")


def parse_with_pvp_class(class_="PVP_Project"):
    # plt.style.use(["latex"])

    pvp_class = None
    if class_ == "PVP_Project":
        pvp_class = PVP_Project
    if class_ == "PVP_det":
        pvp_class = PVP_det
    if class_ == "PVP_Centroid":
        pvp_class = PVP_Centroid
    if pvp_class == None:
        raise Exception("class " + class_ + " is not recognized")

    TESTFLAG = 0
    if TESTFLAG:
        data_folder = "test"
    else:
        data_folder = "data_fusion"

    FUSION = 0
    OUTLIERS = 4.2

    JULIEN_FLAG = 1
    if JULIEN_FLAG:
        root_path = "/home/juliengori/Documents/VC/ANDROIDE_Project_HCI_Fitts2.0"
    else:
        root_path = "/home/quentin/Cours/ANDROIDE_Project_HCI_Fitts2.0"

    data_path = "/".join([root_path, f"users_data/{data_folder}/"])
    if FUSION:
        fusion_user()
    datas = readDirectory(
        data_path, fusion=True
    )  # Read only files with _fusion.json in the name

    SHOW_ALL_FLAG = 0
    SHOW_FLAG = 0
    EXPORT_FLAG = 1
    WRITE_FLAG = 1

    # pix to mm
    DISTANCE_CONVERSION_CONDITIONS = 9.5 / 100
    # DISTANCE_CONVERSION = 9.5/1000
    # DISTANCE_CONVERSION_CONDITIONS = 1

    W = [14.0, 18.0, 26.0, 36.0, 38.0, 66.0, 90.0, 124.0]

    def neg(x):
        return [-u for u in x]

    nb_data = len(datas)
    ndata = 1

    fitts_stats = {
        "Participant": [],
        "protocol": [],
        "device": [],
        "D": [],
        "ID": [],
        "W": [],
        "MT": [],
        "xT": [],
        "yT": [],
        "x_end": [],
        "y_end": [],
        "x0": [],
        "y0": [],
    }

    for data in datas:
        print("\nOperating data : " + str(ndata) + "/" + str(nb_data) + " ...")
        # plotTrajectory(getTrajectories(data)[0])
        nb_files = len(data["experiments"])
        nfile = 1
        containers = []
        cmpt = 0
        conditions = []
        exp_names = []
        npart = data["user_id"]
        WIDTH_SCREEN, HEIGHT_SCREEN = data["display_screen"]

        for num_exp, experiment in enumerate(data["experiments"].values()):
            exp_name = experiment["exp_name"]
            exp_names.append(exp_name + " with " + experiment["input_device"])
            exp_id = experiment["exp_id"]
            print("\nexperiment " + str(nfile) + "/" + str(nb_files))
            print(exp_name)

            _W = None
            _D = None

            for s in exp_name.split(","):
                tmp = list(map(int, re.findall("\d+", s)))
                if "W =" in s:
                    _W = tmp[0]
                if "distance" in s:
                    _D = tmp[0]

            if _W == None:
                raise Exception("Failed to parse W in experiment :" + exp_name)
            if _D == None:
                raise Exception("Failed to parse D in experiment :" + exp_name)

            ncond = W.index(_W) + 1

            print("ncond :", ncond)
            _W = DISTANCE_CONVERSION_CONDITIONS * _W
            _D = DISTANCE_CONVERSION_CONDITIONS * _D
            _ID = math.log(_D / _W + 1, 2)
            print("conditions (D, ID, W)")
            print(_D, _ID, _W)
            conditions.append([_D, _ID, _W])
            container = pvp_class([npart, _D, _ID, _W])

            traj_x = []
            traj_y = []

            for n, trial in enumerate(experiment["trials"].values()):
                if n == 0:
                    continue
                if len(trial["mouse_tracks"]) < 30:
                    print(
                        "Skipped trial : len(mouse_tracks) = ",
                        len(trial["mouse_tracks"]),
                    )
                    continue
                # x = [
                #     v[0] * DISTANCE_CONVERSION_CONDITIONS
                #     for v in trial["mouse_tracks"][1:]
                # ]  # We suppress the first movement because it is used to position the mouse
                # y = [
                #     v[1] * DISTANCE_CONVERSION_CONDITIONS
                #     for v in trial["mouse_tracks"][1:]
                # ]

                x = [
                    v[0] * DISTANCE_CONVERSION_CONDITIONS for v in trial["mouse_tracks"]
                ]  # We suppress the first movement because it is used to position the mouse
                y = [
                    v[1] * DISTANCE_CONVERSION_CONDITIONS for v in trial["mouse_tracks"]
                ]

                # print('x:',x)
                # print('y:',y)
                t = np.arange(0, len(x) * 0.01 + 0.01, 0.01)[
                    : len(x)
                ]  # (... + 0.01, ...) and [:len(x)] used to prevent wrong size caused by numpy

                tx, ty = [
                    k * DISTANCE_CONVERSION_CONDITIONS for k in trial["pos_target"]
                ]

                if WRITE_FLAG:

                    fitts_stats["Participant"].append(npart)
                    if "fitts" in exp_id:
                        fitts_stats["protocol"].append("fitts")
                    if "pvp" in exp_id:
                        fitts_stats["protocol"].append("pvp")
                    fitts_stats["device"].append(experiment["input_device"])
                    fitts_stats["D"].append(_D)
                    fitts_stats["ID"].append(_ID)
                    fitts_stats["W"].append(_W)
                    fitts_stats["MT"].append(trial["time from previous clic"])
                    fitts_stats["xT"].append(tx)
                    fitts_stats["yT"].append(ty)
                    fitts_stats["x_end"].append(x[-1])
                    fitts_stats["y_end"].append(y[-1])
                    fitts_stats["x0"].append(x[0])
                    fitts_stats["y0"].append(y[0])

                try:
                    if class_ == "PVP_Project":
                        container.add_2D_traj_raw_x(
                            x, y, t, 3, tx, ty, correct_start="no"
                        )
                    else:
                        container.add_2D_traj_raw(
                            x, y, t, 3, tx, ty, correct_start="no"
                        )
                        container.add_2D_traj_raw(
                            x, y, t, 3, tx, ty, correct_start="no"
                        )
                except:
                    print("Can't add 2D traj with :")
                    print("len(x) : ", len(x))
                    print("len(y) : ", len(y))
                    print("len(t) : ", len(t))
                    print("tx :", tx, "| ty:", ty)
                    # plt.plot(x, y)
                    # plt.show()
                    # traj_x += x
                    # traj_y += y

            # if 'Random' in exp_name:
            #    plt.plot(traj_x, traj_y)
            #    plt.show()

            container.removed = 0
            if class_ == "PVP_Project":
                container.pvp_routine(OUTLIERS)
            else:
                container.pvp_routine(OUTLIERS)
            container._print_pvp_params()
            print("removed {}".format(container.removed))
            fig = plt.figure()
            ax1 = fig.add_subplot(111)
            if class_ == "PVP_Project":
                container.plot_traj_extend(ax1)
            else:
                container.plot_traj_extend_x(ax1)
            plt.tight_layout()

            if SHOW_ALL_FLAG:
                plt.legend()
                plt.title(exp_name)
                plt.show()

            # container.plot_stdprofiles(ax1)

            plt.tight_layout()

            if EXPORT_FLAG:
                # Creating user folder
                export_path = root_path + "/data_extractor/DATA/users/" + str(npart)
                if not os.path.exists(export_path):
                    os.makedirs(export_path)
                # Creating class folder
                export_path += "/" + class_ + "/"
                if not os.path.exists(export_path):
                    os.makedirs(export_path)
                # Creating trajectories folder
                export_path += "/trajectories/"
                if not os.path.exists(export_path):
                    os.makedirs(export_path)
                file_name = export_path + "/traj_" + str(num_exp)
                plt.title(exp_name)
                plt.tight_layout()
                plt.savefig(file_name)
                plt.close()

                # Creating std_profile folder
                export_path = (
                    root_path
                    + "/data_extractor/DATA/users/"
                    + str(npart)
                    + "/"
                    + class_
                    + "/std_profiles/"
                )

                if not os.path.exists(export_path):
                    os.makedirs(export_path)

                file_name = export_path + "profile_" + str(num_exp)
                fig = plt.figure()
                ax1 = fig.add_subplot(111)
                container.plot_stdprofiles(ax1)
                plt.title(exp_name)
                plt.tight_layout()
                print("============")
                print(file_name)
                print("================")
                plt.savefig(file_name)
                plt.close()

            if SHOW_ALL_FLAG:
                plt.show()
            plt.close()

            containers.append(container)
            nfile += 1

        if WRITE_FLAG:
            # Creating user folder (double check)
            export_path = root_path + "/data_extractor/DATA/users/" + str(npart) + "/"
            if not os.path.exists(export_path):
                os.makedirs(export_path)
            # Creating class folder
            export_path += class_ + "/"
            if not os.path.exists(export_path):
                os.makedirs(export_path)
            # Creating pvps folder
            export_path += "/pvps/"
            if not os.path.exists(export_path):
                os.makedirs(export_path)
            pvp_container = PVP_container(npart, [containers[0]])
            rows_stats = pvp_container.dataframe.copy()
            pvp_profile = {
                "Participant": [npart],
                "protocol": [None],
                "device": [None],
                "D": [containers[0].condition[1]],
                "ID": [containers[0].condition[2]],
                "W": [containers[0].condition[3]],
                "timestamps": [containers[0].timestamps],
                "std_prof": [containers[0].std_prof],
                "pvp_x": [containers[0].pvp_x],
                "pvp_y": [containers[0].pvp_y],
            }
            if "Random" in exp_names[0]:
                rows_stats.insert(1, "protocol", ["pvp"], True)
                pvp_profile["protocol"] = ["pvp"]
            if "Circle" in exp_names[0]:
                rows_stats.insert(1, "protocol", ["fitts"], True)
                pvp_profile["protocol"] = ["fitts"]
            if "mouse" in exp_names[0]:
                rows_stats.insert(2, "device", ["mouse"], True)
                pvp_profile["device"] = ["mouse"]
            if "touchpad" in exp_names[0]:
                rows_stats.insert(2, "device", ["touchpad"], True)
                pvp_profile["device"] = ["touchpad"]
            if "controller" in exp_names[0]:
                rows_stats.insert(2, "device", ["controller"], True)
                pvp_profile["device"] = ["controller"]

            for i, c in enumerate(containers):

                file_name = export_path + "/" + str(i)
                pvp_container = PVP_container(npart, [c])

                # Dataframes (PVP_stats)
                data_f = pvp_container.dataframe
                protocol = ""
                device = ""
                if "Random" in exp_names[i]:
                    protocol = "pvp"
                if "Circle" in exp_names[i]:
                    protocol = "fitts"
                if "mouse" in exp_names[i]:
                    device = "mouse"
                if "touchpad" in exp_names[i]:
                    device = "touchpad"
                if "controller" in exp_names[i]:
                    device = "controller"
                data_f.insert(1, "protocol", [protocol], True)
                data_f.insert(2, "device", [device], True)
                if i != 0:
                    _d, _id, _w = [float(u) for u in containers[i].condition[1:]]
                    rows_stats = pandas.concat([rows_stats, data_f], ignore_index=True)
                    # Adding pvp_profiles rows
                    pvp_profile["Participant"].append(npart)
                    pvp_profile["protocol"].append(protocol)
                    pvp_profile["device"].append(device)
                    pvp_profile["D"].append(_d)
                    pvp_profile["ID"].append(_id)
                    pvp_profile["W"].append(_w)
                    pvp_profile["timestamps"].append(containers[i].timestamps)
                    pvp_profile["std_prof"].append(containers[i].std_prof)
                    pvp_profile["pvp_x"].append(containers[i].pvp_x)
                    pvp_profile["pvp_y"].append(containers[i].pvp_y)

                print(pvp_container.dataframe)

                # Dataframes (PVP_profile)

                # Plotting pvps
                fig = plt.figure()
                ax = fig.add_subplot(111)
                pvp_container.plot_all_pvps(ax, [""])
                plt.title(exp_names[i])
                plt.tight_layout()
                plt.savefig(file_name)
                plt.close()

                # Saving PVP in pickle file
                pickle_path = (
                    root_path
                    + "/data_extractor/DATA/users/"
                    + str(npart)
                    + "/"
                    + class_
                    + "/pvp_pickle/"
                )
                if not os.path.exists(pickle_path):
                    os.makedirs(pickle_path)
                with open(pickle_path + "PVP_" + str(i) + ".pickle", "wb") as f:
                    pkl.dump(containers[i], f)

            export_path = (
                root_path
                + "/data_extractor/DATA/users/"
                + str(npart)
                + "/"
                + class_
                + "/data/"
            )
            if not os.path.exists(export_path):
                os.makedirs(export_path)

            rows_stats.to_csv(export_path + "pvp_stats.csv")
            rows_profile = pandas.DataFrame(pvp_profile)
            rows_profile.to_csv(export_path + "pvp_profile.csv")

        if SHOW_FLAG or EXPORT_FLAG:
            print("Plotting all pvps")
            print("exp_id\tdevice\texp_name")

            fitts_controller_container = []
            fitts_mouse_container = []
            fitts_touchpad_container = []

            pvp_controller_container = []
            pvp_mouse_container = []
            pvp_touchpad_container = []

            for i, name in enumerate(exp_names):
                print(str(i) + "\t" + name)
                if "Random" in name:
                    if data["experiments"][str(i)]["input_device"] == "controller":
                        pvp_controller_container.append((containers[i], name))
                    elif data["experiments"][str(i)]["input_device"] == "touchpad":
                        pvp_touchpad_container.append((containers[i], name))
                    elif data["experiments"][str(i)]["input_device"] == "mouse":
                        pvp_mouse_container.append((containers[i], name))

                elif "Circle" in name:
                    if data["experiments"][str(i)]["input_device"] == "controller":
                        fitts_controller_container.append((containers[i], name))
                    elif data["experiments"][str(i)]["input_device"] == "touchpad":
                        fitts_touchpad_container.append((containers[i], name))
                    elif data["experiments"][str(i)]["input_device"] == "mouse":
                        fitts_mouse_container.append((containers[i], name))

            fig, axs = plt.subplots(2, 3, figsize=(16, 12))
            print("fitts_controller_container :", len(fitts_controller_container))
            print("fitts_mouse_container :", len(fitts_mouse_container))
            print("fitts_touchpad_container :", len(fitts_touchpad_container))
            print("pvp_controller_container :", len(pvp_controller_container))
            print("pvp_mouse_container :", len(pvp_mouse_container))
            print("pvp_touchpad_container :", len(pvp_touchpad_container))

            pvp_container = PVP_container(
                npart, [k[0] for k in fitts_controller_container]
            )
            pvp_container.plot_all_pvps(
                axs[0, 0], [k[1] for k in fitts_controller_container]
            )
            axs[0, 0].title.set_text("fitts controller")

            pvp_container = PVP_container(npart, [k[0] for k in fitts_mouse_container])
            pvp_container.plot_all_pvps(
                axs[0, 1], [k[1] for k in fitts_mouse_container]
            )
            axs[0, 1].title.set_text("fitts mouse")

            pvp_container = PVP_container(
                npart, [k[0] for k in fitts_touchpad_container]
            )
            pvp_container.plot_all_pvps(
                axs[0, 2], [k[1] for k in fitts_touchpad_container]
            )
            axs[0, 2].title.set_text("fitts touchpad")

            pvp_container = PVP_container(
                npart, [k[0] for k in pvp_controller_container]
            )
            pvp_container.plot_all_pvps(
                axs[1, 0], [k[1] for k in pvp_controller_container]
            )
            axs[1, 0].title.set_text("pvp controller")

            pvp_container = PVP_container(npart, [k[0] for k in pvp_mouse_container])
            pvp_container.plot_all_pvps(axs[1, 1], [k[1] for k in pvp_mouse_container])
            axs[1, 1].title.set_text("pvp mouse")

            pvp_container = PVP_container(npart, [k[0] for k in pvp_touchpad_container])
            pvp_container.plot_all_pvps(
                axs[1, 2], [k[1] for k in pvp_touchpad_container]
            )
            axs[1, 2].title.set_text("pvp touchpad")
            plt.tight_layout()

            ###### scale
            fig_scaled, axs = plt.subplots(2, 3, figsize=(16, 12))
            print("fitts_controller_container :", len(fitts_controller_container))
            print("fitts_mouse_container :", len(fitts_mouse_container))
            print("fitts_touchpad_container :", len(fitts_touchpad_container))
            print("pvp_controller_container :", len(pvp_controller_container))
            print("pvp_mouse_container :", len(pvp_mouse_container))
            print("pvp_touchpad_container :", len(pvp_touchpad_container))

            pvp_container = PVP_container(
                npart, [k[0] for k in fitts_controller_container]
            )
            pvp_container.plot_all_pvps(
                axs[0, 0], [k[1] for k in fitts_controller_container]
            )
            axs[0, 0].title.set_text("fitts controller")

            pvp_container = PVP_container(npart, [k[0] for k in fitts_mouse_container])
            pvp_container.plot_all_pvps(
                axs[0, 1], [k[1] for k in fitts_mouse_container]
            )
            axs[0, 1].title.set_text("fitts mouse")

            pvp_container = PVP_container(
                npart, [k[0] for k in fitts_touchpad_container]
            )
            pvp_container.plot_all_pvps(
                axs[0, 2], [k[1] for k in fitts_touchpad_container]
            )
            axs[0, 2].title.set_text("fitts touchpad")

            pvp_container = PVP_container(
                npart, [k[0] for k in pvp_controller_container]
            )
            pvp_container.plot_all_pvps(
                axs[1, 0], [k[1] for k in pvp_controller_container]
            )
            axs[1, 0].title.set_text("pvp controller")

            pvp_container = PVP_container(npart, [k[0] for k in pvp_mouse_container])
            pvp_container.plot_all_pvps(axs[1, 1], [k[1] for k in pvp_mouse_container])
            axs[1, 1].title.set_text("pvp mouse")

            pvp_container = PVP_container(npart, [k[0] for k in pvp_touchpad_container])
            pvp_container.plot_all_pvps(
                axs[1, 2], [k[1] for k in pvp_touchpad_container]
            )
            axs[1, 2].title.set_text("pvp touchpad")

            axs[0, 0].set_xlim([0, 4])
            axs[0, 0].set_ylim([0.1, 100])
            axs[0, 1].set_xlim([0, 4])
            axs[0, 1].set_ylim([0.1, 100])
            axs[0, 2].set_xlim([0, 4])
            axs[0, 2].set_ylim([0.1, 100])
            axs[1, 0].set_xlim([0, 4])
            axs[1, 0].set_ylim([0.1, 100])
            axs[1, 1].set_xlim([0, 4])
            axs[1, 1].set_ylim([0.1, 100])
            axs[1, 2].set_xlim([0, 4])
            axs[1, 2].set_ylim([0.1, 100])

            plt.tight_layout()

        ndata += 1
        if EXPORT_FLAG:
            export_path = (
                root_path
                + "/data_extractor/DATA/users/"
                + str(npart)
                + "/"
                + class_
                + "/"
            )
            if not os.path.exists(export_path):
                os.makedirs(export_path)
            export_path += "all_pvps/"
            if not os.path.exists(export_path):
                os.makedirs(export_path)
            file_name = export_path + "pvps"
            plt.tight_layout()
            fig.savefig(file_name + ".pdf")
            fig_scaled.savefig(file_name + "_scaled.pdf")
        if SHOW_FLAG:
            plt.show()

    if WRITE_FLAG:
        export_path = root_path + "/data_extractor/DATA/export/"
        print('##################################""')
        print(export_path + "fitts_stats.csv")
        print('##################################""')

        if not os.path.exists(export_path):
            os.makedirs(export_path)
        data_f = pandas.DataFrame(fitts_stats)
        data_f.to_csv(export_path + "fitts_stats.csv")

    ######################################################################################
    return 0


def main():
    args = sys.argv[1:]
    if len(args) == 0:
        parse_with_pvp_class()
    else:
        parse_with_pvp_class(args[0])
    fusion_dataframe()
    return 0


if __name__ == "__main__":
    sys.exit(main())
