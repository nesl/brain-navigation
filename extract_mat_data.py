import numpy as np
import scipy.io
import datetime
from datetime import timezone
import matplotlib.pyplot as plt
import os
import shutil
import pandas as pd
import re
from pathlib import Path

# # Specify the folder path
# folder_path = '../RWNApp_Output_Jan2024/'

# # List all filenames in the folder
# filenames = os.listdir(folder_path)

# # Display the filenames
# for filename in filenames:
#     print(filename)

subject = 1
walk = 4

save_ori_dirname_map = {
    "chest_phone": "ChestPhone",
    "pupil_phone": "PupilPhone",
    "gopro": "GoPro",
    "pupil": "Pupil"
}

def move_files(subject, walk):
    save_folder = f"../../RW{subject}/RW{subject}-Walk{walk}-extracted/"

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # -------------------------------
    # move chest phone videos
    acc = r'^accelData.*csv$'
    ambient = r'^ambient.*csv$'
    gps = r'^gps.*csv$'
    gyro = r'^gyro.*csv$'
    mag = r'^mag.*csv$'

    data_type = "chest_phone"

    chest_directory = f"E:/BrainNavigationData/RW{subject}/Original/Walk{walk}/{save_ori_dirname_map[data_type]}"

    for root, dirs, files in os.walk(chest_directory):
        for name in files:
            filename = os.path.join(root, name)
            # print(filename)
            match = re.match(acc, name)
            if match:
                new_file = save_folder + f"data_{data_type}_acc.csv"
                print(f"Copying {filename} to {new_file}...")
                # input("Press Enter to continue")
                shutil.copy(filename, new_file)

            match = re.match(ambient, name)
            if match:
                new_file = save_folder + f"data_{data_type}_light.csv"
                print(f"Copying {filename} to {new_file}...")
                # input("Press Enter to continue")
                shutil.copy(filename, new_file)
            
            match = re.match(gps, name)
            if match:
                new_file = save_folder + f"data_{data_type}_gps.csv"
                print(f"Copying {filename} to {new_file}...")
                # input("Press Enter to continue")
                shutil.copy(filename, new_file)

            match = re.match(gyro, name)
            if match:
                new_file = save_folder + f"data_{data_type}_gyro.csv"
                print(f"Copying {filename} to {new_file}...")
                # input("Press Enter to continue")
                shutil.copy(filename, new_file)

            match = re.match(mag, name)
            if match:
                new_file = save_folder + f"data_{data_type}_mag.csv"
                print(f"Copying {filename} to {new_file}...")
                # input("Press Enter to continue")
                shutil.copy(filename, new_file)

    print("Done moving chest phone")

    # -------------------------------
    # move pupil phone
    # acc = r'^accelData.*csv$'
    # ambient = r'^ambient.*csv$'
    # gps = r'^gps.*csv$'
    # gyro = r'^gyro.*csv$'
    data_type = "pupil_phone"

    pupil_directory = f"E:/BrainNavigationData/RW{subject}/Original/Walk{walk}/{save_ori_dirname_map[data_type]}"

    for root, dirs, files in os.walk(pupil_directory):
        for name in files:
            filename = os.path.join(root, name)
            # print(filename)
            match = re.match(acc, name)
            if match:
                new_file = save_folder + f"data_{data_type}_acc.csv"
                print(f"Copying {filename} to {new_file}...")
                # input("Press Enter to continue")
                shutil.copy(filename, new_file)

            match = re.match(gps, name)
            if match:
                new_file = save_folder + f"data_{data_type}_gps.csv"
                print(f"Copying {filename} to {new_file}...")
                # input("Press Enter to continue")
                shutil.copy(filename, new_file)

            match = re.match(gyro, name)
            if match:
                new_file = save_folder + f"data_{data_type}_gyro.csv"
                print(f"Copying {filename} to {new_file}...")
                # input("Press Enter to continue")
                shutil.copy(filename, new_file)

            match = re.match(mag, name)
            if match:
                new_file = save_folder + f"data_{data_type}_mag.csv"
                print(f"Copying {filename} to {new_file}...")
                # input("Press Enter to continue")
                shutil.copy(filename, new_file)

    print("Done moving pupil phone")
        

    # -------------------------------
    # move gopro
    # gopro = r'.*'
    # gopro = r".*CleanedAudio.mp4$"
    data_type = "gopro"

    ## gopro video is in Synced directory
    original_dir = f"E:/BrainNavigationData/RW{subject}/Synced/Walk{walk}_complete/{save_ori_dirname_map[data_type]}"
    original_files = list(Path(original_dir).rglob('*CleanedAudio.mp4'))
    print("original_dir:", original_dir, "; original_files:", original_files)
    if len(original_files) > 1:
        raise ValueError("Multiple CleanedAudio.mp4 files")
    
    new_file = save_folder + f"data_video_{data_type}.mp4"
    print(f"Copying {original_files[0]} to {new_file}...")
    # input("Press Enter to continue")
    shutil.copy(original_files[0], new_file)

    print(f"Done moving gopro\nsub: {subject}, walk: {walk}")

    # -------------------------------
    # move pupil video
    # pv = r".*\.mp4$"
    data_type = "pupil"

    ## pupil video is in Synced directory
    original_dir = f"E:/BrainNavigationData/RW{subject}/Synced/Walk{walk}_complete/{save_ori_dirname_map[data_type]}"
    original_files = list(Path(original_dir).rglob('*.mp4'))
    if len(original_files) > 1:
        raise ValueError("Multiple .mp4 files in Pupil (vedio) directory")
    
    new_file = save_folder + f"data_video_{data_type}.mp4"
    print(f"Copying {original_files[0]} to {new_file}...")
    # input("Press Enter to continue")
    shutil.copy(original_files[0], new_file)

    print(f"Done moving xsense\nsub: {subject}, walk: {walk}")


def extract_mat(subject, walk):
    mat = scipy.io.loadmat(f'../../mat_RWNApp_Output_Jan2024/RWNApp_RW{subject}_Walk{walk}.mat')
    print(mat.keys())

    data_np = mat['d_np']
    data_xs = mat['d_xs']
    time_np = mat['ntp_np']
    time_xs = mat['ntp_xs']
    time_gopro = mat['ntp_gp']
    time_pupil = mat['ntp_pupil']
    print(f'subject: {subject}, walk: {walk}')
    print(data_np.shape)
    print(data_xs.shape)
    print(time_np.shape)
    print(time_xs.shape)

    source_folder = f"E:/BrainNavigationData/RW{subject}/Original/Walk{walk}"
    save_folder = f"E:/BrainNavigationData/RW{subject}/RW{subject}-Walk{walk}-extracted/"

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    np.save(save_folder + "data_np", data_np)
    np.save(save_folder + "data_xs", data_xs)

    # Extract xsense
    df = pd.read_excel(os.path.join(source_folder, f'Xsens/RW_{subject}_w{walk}.xlsx'), sheet_name='Center of Mass')
    df.to_csv(save_folder + 'data_xs_Center-of-Mass.csv', index=False)


    def matlab_datenum_to_formatted_string(matlab_datenum):

        # Convert MATLAB datenum to Python datenum by subtracting the MATLAB epoch
        python_datenum = matlab_datenum  # Adjust for MATLAB epoch

        # Convert Python datenum to datetime
        python_datetime = datetime.datetime.fromordinal(int(python_datenum)) + datetime.timedelta(days=python_datenum % 1) - datetime.timedelta(days=366)

        # Format datetime string
        formatted_string = python_datetime.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]

        return formatted_string


    # convert matlab NTP time to datetime timestamp
    if time_np.shape[1] > 0:
        np_formatted_strings = [matlab_datenum_to_formatted_string(md) for md in time_np[:, 0]/60/60/24]
        np.save(save_folder + "time_np", np_formatted_strings)
    else:
        print("time_np missing")

    if time_xs.shape[1] > 0:
        xs_formatted_strings = [matlab_datenum_to_formatted_string(md) for md in time_xs[:, 0]/60/60/24]
        np.save(save_folder + "time_xs", xs_formatted_strings)
    else:
        print("time_xs missing")

    if time_gopro.shape[1] > 0:
        gopro_formatted_strings = [matlab_datenum_to_formatted_string(md) for md in time_gopro[:, 0]/60/60/24]
        np.save(save_folder + "time_gopro", gopro_formatted_strings)
    else:
        print("time_gopro missing")

    if time_pupil.shape[1] > 0:
        pupil_formatted_strings = [matlab_datenum_to_formatted_string(md) for md in time_pupil[:, 0]/60/60/24]
        np.save(save_folder + "time_pupil", pupil_formatted_strings)
    else:
        print("time_pupil missing")



if __name__ == "__main__":
    move_files(subject, walk)
    extract_mat(subject, walk)
