import json
import pandas
from pvplib.data_parser import *


JULIEN_FLAG = 1
if JULIEN_FLAG:
    root_path = "/home/juliengori/Documents/VC/ANDROIDE_Project_HCI_Fitts2.0"
else:
    root_path = "/home/quentin/Cours/ANDROIDE_Project_HCI_Fitts2.0"


def fusion_dataframe(
    data_path=root_path + "/data_extractor/DATA/users/",
    export_path=root_path + "/data_extractor/DATA/export/",
):
    dataframes_stats = None
    dataframes_profile = None
    is_empty_stats = True
    is_empty_profile = True

    print(data_path)
    for user_id in next(os.walk(data_path))[1]:
        print(data_path)
        print(user_id)
        # PVP_STATS
        for class_ in next(os.walk(data_path + user_id + "/"))[1]:
            path = data_path + user_id + "/" + class_
            if is_empty_stats:
                try:
                    dataframes_stats = pandas.read_csv(
                        path + "/data/pvp_stats.csv", index_col=0
                    )
                    is_empty_stats = False
                except:
                    print("Cannot read :" + path + "/data/pvp_stats.csv")
            else:
                try:
                    user_df = pandas.read_csv(path + "/data/pvp_stats.csv", index_col=0)
                    dataframes_stats = pandas.concat(
                        [dataframes_stats, user_df], ignore_index=True
                    )
                except:
                    print("Cannot read :" + path + "/data/pvp_stats.csv")

            # PVP_PROFILE
            if is_empty_profile:
                try:
                    dataframes_profile = pandas.read_csv(
                        path + "/data/pvp_profile.csv", index_col=0
                    )
                    is_empty_profile = False
                except:
                    print("Cannot read :" + path + "/data/pvp_profile.csv")
            else:
                try:
                    user_df = pandas.read_csv(
                        path + "/data/pvp_profile.csv", index_col=0
                    )
                    dataframes_profile = pandas.concat(
                        [dataframes_profile, user_df], ignore_index=True
                    )
                except:
                    print("Cannot read :" + path + "/data/pvp_stats.csv")
    dataframes_stats.to_csv(export_path + "pvp_stats.csv")
    dataframes_profile.to_csv(export_path + "pvp_profile.csv")


def fusion_user(
    data_path=root_path + "/users_data/saved/",
    export_path=root_path + "/users_data/data_fusion/",
):
    datas = readDirectory(data_path)

    for i, d1 in enumerate(datas):
        for j, d2 in enumerate(datas[i + 1 :]):
            if d1 == d2:
                continue
            if d1["user_id"] != d2["user_id"]:
                continue
            d_max = d1["experiments"]
            d_min = d2["experiments"]
            if len(d1["experiments"]) < len(d2["experiments"]):
                d_min = d1["experiments"]
                d_max = d2["experiments"]

            last_key = max([int(k) for k in d_max.keys()]) + 1
            for k, v in d_min.items():
                d_max[str(int(k) + last_key)] = v
            d1["experiments"] = d_max

            with open(export_path + str(d1["user_id"]) + "_fusion.json", "w") as file_:
                json.dump(d1, file_)
    return 1


def main():
    return fusion()


if __name__ == "__main__":
    sys.exit(main())
