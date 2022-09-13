import os
import pandas
import numpy

JULIEN_FLAG = 1
if JULIEN_FLAG:
    root_path = "/home/juliengori/Documents/VC/ANDROIDE_Project_HCI_Fitts2.0"
else:
    root_path = "/home/quentin/Cours/ANDROIDE_Project_HCI_Fitts2.0"


path_to_users = root_path + "/data_extractor/DATA/users"

pvps = ["Project", "Centroid", "det"]

columns_stats = [
    "Participant",
    "protocol",
    "device",
    "D",
    "ID",
    "W",
    "tau",
    "Dtau",
    "sigma0",
    "omega",
    "C",
    "rsq",
    "pvptype",
]

columns_profiles = [
    "Participant",
    "protocol",
    "device",
    "D",
    "ID",
    "W",
    "timestamps",
    "std_prof",
    "pvp_x",
    "pvp_y",
    "pvptype",
]

columns_fitts = [
    "Participant",
    "protocol",
    "device",
    "D",
    "ID",
    "W",
    "MT",
    "xT",
    "yT",
    "x_end",
    "y_end",
    "x_0",
    "y_0",
]

stats = numpy.empty((2048, len(columns_stats)), dtype=object)
profiles = numpy.empty((2048, len(columns_profiles)), dtype=object)


currentpath, folders, files = next(os.walk(path_to_users))
stats_row_counter = 0
profiles_row_counter = 0

# user = folders[0]
# pvp = pvps[0]
# path = "/".join(
#     [
#         currentpath,
#         user,
#         f"PVP_{pvp}",
#         "data/fitts_stats.csv",
#     ]
# )

# _file = open(path, "r")
# exit()

# exit()
for user in folders:
    for pvp in pvps:
        path = "/".join(
            [
                currentpath,
                user,
                f"PVP_{pvp}",
                "data/pvp_stats.csv",
            ]
        )
        with open(path, "r") as _file:
            df = pandas.read_csv(_file)
            nrows = df.shape[0]
            stats[stats_row_counter : stats_row_counter + nrows, :-1] = df.to_numpy(
                dtype=object
            )[:, 1:]
            stats[stats_row_counter : stats_row_counter + nrows, -1] = pvp
            stats_row_counter += nrows

        path = "/".join(
            [
                currentpath,
                user,
                f"PVP_{pvp}",
                "data/pvp_profile.csv",
            ]
        )
        with open(path, "r") as _file:
            df = pandas.read_csv(_file)
            nrows = df.shape[0]
            profiles[
                profiles_row_counter : profiles_row_counter + nrows, :-1
            ] = df.to_numpy(dtype=object)[:, 1:]
            profiles[profiles_row_counter : profiles_row_counter + nrows, -1] = pvp
            profiles_row_counter += nrows

        if pvp != "Project":
            continue


Stats = pandas.DataFrame(stats[stats[:, 0] != None, :], columns=columns_stats)
export_path = "/".join(
    [root_path, "data_extractor", "DATA", "export", "pvp_stats_full.csv"]
)
with open(export_path, "w") as _file:
    Stats.to_csv(export_path)


PVPs = pandas.DataFrame(profiles[profiles[:, 0] != None, :], columns=columns_profiles)

export_path = "/".join(
    [root_path, "data_extractor", "DATA", "export", "pvp_profiles_full.csv"]
)
with open(export_path, "w") as _file:
    PVPs.to_csv(export_path)
