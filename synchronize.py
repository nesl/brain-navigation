import numpy as np
from numpy.typing import NDArray
import datetime
# from datetime import datetime, timezone, timedelta
import os
import pandas as pd
from moviepy.editor import VideoFileClip
import csv

map_long_sample_freq = {
    'chestphone_gps': 7,
    'chestphone_light': 0.1,
    'pupilphone_gps': 7
} #unit: second

subject = 1
walks = [3]
fps_for_frame = 30
video_sync_modality_frame = 'PupilFrame'
time_window = 2  # Unit: second

def extract_video_noaudio_subset(video_path, start_frame, end_frame, output_path, time_window = None, fps=None):
    """
    Extract a subset of frames from a video file without including audio.

    Parameters:
        video_path (str): Path to the input video file.
        start_frame (int): Starting frame index.
        end_frame (int): Ending frame index.
        output_path (str): Path to save the output video file.
        time_window (int): Time window for downstream task input. If the piece from start_frame to 
            end_frame is longer than time window, do nothing; if shorter, expand it to time window.
            Default is None, and the code won't do anything special.
        fps (int): Frame frequency of video clip (frame per second). Use video_clip.fps if not set.
    """
    # Load video clip
    video_clip = VideoFileClip(video_path)
    if fps is None:
        fps = video_clip.fps

    # print("Extracting video...")
    # Downstream task requires fixed length data for training, so here we directly extract the data with the required length.
    # If the event (label) is longer than required length (i.e, time_window), do normal data extraction;
    # else put the event in the middle, and expand the starting and ending frame to the required length
    if time_window:
        # print("original start_frame:", start_frame, "original end_frame:", end_frame)
        frame_len = end_frame - start_frame
        expand_frame = int(time_window*fps - frame_len)
        if expand_frame > 0:
            total_frames = int(video_clip.duration * fps)
            start_frame = max(0, start_frame - expand_frame // 2)
            end_frame = min(total_frames, start_frame + frame_len + expand_frame)
            # print("expanded start_frame:", start_frame, "expanded end_frame:", end_frame, "frame length: ", end_frame-start_frame)
            # input("Press Enter to continue...")

    # Extract subset of frames
    subset_clip = video_clip.subclip(start_frame / fps, end_frame / fps)

    # Write video file without audio
    subset_clip.write_videofile(output_path, codec="libx264", audio=False, logger=None)

    # Close the video clip
    video_clip.close()

def extract_video_audio_subset(video_path, start_frame, end_frame, output_video_path, 
                               output_audio_path, time_window = None, fps=None):
    """
    Extract a subset of frames from a video file and save the video and audio separately.

    Parameters:
        video_path (str): Path to the input video file.
        start_frame (int): Starting frame index.
        end_frame (int): Ending frame index.
        output_video_path (str): Path to save the output video file.
        output_audio_path (str): Path to save the output audio file.
        time_window (int): Time window for downstream task input. If the piece from start_frame to 
            end_frame is longer than time window, do nothing; if shorter, expand it to time window.
            Default is None, and the code won't do anything special.
        fps (int): Frame frequency of video clip (frame per second). Use video_clip.fps if not set.
    """
    # Validate input parameters
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found at {video_path}")
    if start_frame < 0 or end_frame < 0:
        raise ValueError("Frame indices must be non-negative")
        # return "Frame indices must be non-negative"
    if end_frame <= start_frame:
        raise ValueError("End frame must be greater than start frame")
        # return "End frame must be greater than start frame"

    # Load video clip
    video_clip = VideoFileClip(video_path)
    if fps is None:
        fps = video_clip.fps

    # print("Extracting video...")
    # Downstream task requires fixed length data for training, so here we directly extract the data with the required length.
    # If the event (label) is longer than required length (i.e, time_window), do normal data extraction;
    # else put the event in the middle, and expand the starting and ending frame to the required length
    if time_window:
        # print("original start_frame:", start_frame, "original end_frame:", end_frame)
        frame_len = end_frame - start_frame
        expand_frame = int(time_window*fps - frame_len)
        if expand_frame > 0:
            total_frames = int(video_clip.duration * fps)
            start_frame = max(0, start_frame - expand_frame // 2)
            end_frame = min(total_frames, start_frame + frame_len + expand_frame)
            # print("expanded start_frame:", start_frame, "expanded end_frame:", end_frame, "frame length: ", end_frame-start_frame)
            # input("Press Enter to continue...")

    # Calculate time in seconds for subclipping
    start_time = start_frame / fps
    end_time = end_frame / fps

    # Extract subset of frames
    subset_clip = video_clip.subclip(start_time, end_time)

    # Write video file
    subset_clip.write_videofile(output_video_path, codec="libx264", logger=None)

    # Close the video clip
    subset_clip.close()

    # Extract audio
    audio_clip = video_clip.audio

    # Extract subset of audio
    subset_audio_clip = audio_clip.subclip(start_time, end_time)

    # Write audio file
    subset_audio_clip.write_audiofile(output_audio_path, logger=None)

    # Close the audio clip
    subset_audio_clip.close()

    # Close the video clip
    video_clip.close()


def matlab_datenum_to_formatted_string(matlab_datenum):

    # Convert MATLAB datenum to Python datenum by subtracting the MATLAB epoch
    python_datenum = matlab_datenum

    # Convert Python datenum to datetime
    python_datetime = datetime.datetime.fromordinal(int(python_datenum)) + datetime.timedelta(days=python_datenum % 1) - datetime.timedelta(days=366)

    # Format datetime string
    formatted_string = python_datetime.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]

    return formatted_string


def calculate_duration(datetime_str1, datetime_str2):
    """
    Calculate the duration between two datetime strings.

    Parameters:
        datetime_str1 (str): First datetime string.
        datetime_str2 (str): Second datetime string.

    Returns:
        datetime.timedelta: Duration between the two datetime strings.
    """
    # Convert the datetime strings to datetime objects
    datetime_obj1 = datetime.datetime.strptime(datetime_str1, '%Y-%m-%d_%H-%M-%S-%f')
    datetime_obj2 = datetime.datetime.strptime(datetime_str2, '%Y-%m-%d_%H-%M-%S-%f')

    # Calculate the duration
    duration = datetime_obj2 - datetime_obj1

    # Return the duration
    return duration


def find_close_frame(time_label, time_data_array):

    frame_index_data = 0
    time_label_num = datetime.datetime.strptime(time_label, '%Y-%m-%d_%H-%M-%S-%f')

    for temp_index in range(time_data_array.shape[0]):

        temp_time_data = datetime.datetime.strptime(time_data_array[temp_index], '%Y-%m-%d_%H-%M-%S-%f')

        if temp_time_data >= time_label_num:

            frame_index_data = temp_index
            # print("syncronze frame: ", frame_index_data, time_label, time_data_array[temp_index])
            break

    return frame_index_data

def calculate_time_diff(time_str1, time_str2):
    '''Calculate the difference between time_str1 and time_str2. Both input times are str in format: '%Y-%m-%d_%H-%M-%S-%f' '''
    time1 = datetime.datetime.strptime(time_str1, '%Y-%m-%d_%H-%M-%S-%f')
    time2 = datetime.datetime.strptime(time_str2, '%Y-%m-%d_%H-%M-%S-%f')

    return abs(time2 - time1).total_seconds()

def extract_modalities(
        start_frame_index : int,
        end_frame_index : int,
        time_arr : NDArray,
        data_arr : NDArray,
        modality : str, # all events except for gopro. Gopro is processed outside this function.
        time_label,
        save_syncronized_splt_folder : str,
        time_window = None,
        modality_freq = None,
        do_extract : bool = True, # whether to extract and save the np file. Default is True. If setting to False, this function only returns whether the modality is missing or not.
    ):
    global label_missing_cnt, modalit_missing_time
    if modality == 'np':
        start_frame = time_arr[start_frame_index]
        end_frame = time_arr[end_frame_index]
    else:
        if time_label == None:
            raise ValueError("time_label can be unset only if modality is neural pace")
        start_frame = find_close_frame(time_label[start_frame_index], time_arr)
        end_frame = find_close_frame(time_label[end_frame_index], time_arr)

    # Downstream task requires fixed length data for training, so here we directly extract the data with the required length.
    # If the event (label) is longer than required length (i.e, time_window), do normal data extraction;
    # else put the event in the middle, and expand the starting and ending frame to the required length
    # print(f"Extracting {modality}...")
    if time_window:
        if not modality_freq:
            raise ValueError("modality_freq must be provided if time_window is setted.")
        # print("original start_frame:", start_frame, "original end_frame:", end_frame)
        frame_len = end_frame - start_frame
        expand_frame = int(time_window*modality_freq - frame_len)
        if expand_frame > 0:
            start_frame = max(0, start_frame - expand_frame // 2)
            end_frame = min(len(data_arr), start_frame + frame_len + expand_frame)
            # print("expanded start_frame:", start_frame, "enpanded end_frame:", end_frame, "frame length: ", end_frame-start_frame)
            # input("Press Enter to continue...")

    # print("time_{}: ".format(modality), time_arr[start_frame], time_arr[end_frame], calculate_duration(time_arr[start_frame], time_arr[end_frame]))
    
    if modality in ['chestphone_acc', 'chestphone_gyro', 'chestphone_mag', 'pupilphone_acc', 'pupilphone_gyro', 'pupilphone_mag', 'xs_CoM', 'np']:
        if end_frame <= start_frame:
            label_missing_cnt[modality] = label_missing_cnt.get(modality, 0) + 1
            return False
        else:
            if do_extract:
                output_path = save_syncronized_splt_folder + '{}_{}.npy'.format(start_frame_index, modality)
                np.save(output_path, data_arr[start_frame:end_frame])
            return True
    elif modality in ['chestphone_gps', 'chestphone_light', 'pupilphone_gps']:
        if end_frame <= start_frame:
            if calculate_time_diff(time_label[start_frame_index], time_arr[start_frame]) > map_long_sample_freq[modality]:
                label_missing_cnt[modality] = label_missing_cnt.get(modality, 0) + 1
                return False
            else:
                end_frame += 1

        # If end_frame > start_frame or time_diff <= sample_freq, return true
        if do_extract:
            output_path = save_syncronized_splt_folder + '{}_{}.npy'.format(start_frame_index, modality)
            np.save(output_path, data_arr[start_frame:end_frame])
        
        return True 


for walk in walks:
    # fre_np = 250, fre_gopro = 60, fre_pupil = 60
    # Load all data and timestamp: Neural-Pace (NP) signal, GoPro videos, Pupil videos, Xsens, phone (acc, gyro, mag, GPS, light, audio)
    load_syncronized_folder = f'../RW{subject}/RW{subject}-Walk{walk}-extracted/'
    save_syncronized_splt_folder = f'../synchronized/RW{subject}/RW{subject}-Walk{walk}-self-syncronize-split/'

    if not os.path.exists(save_syncronized_splt_folder):
        # Create the directory
        os.makedirs(save_syncronized_splt_folder)

    # Event Description PupilFrame  GoProFrame  NPSample    NTP
    df = pd.read_csv(f'../label_RWNApp_Output_Jan2024/evnts_RWNApp_RW{subject}_Walk{walk}.csv')
    label = df['Event']
    ntp_label = df['NTP']
    # PupilFrame = df['PupilFrame']
    GoProFrame = df[video_sync_modality_frame]
    NPSample = df['NPSample']

    # convert matlab NTP time to datetime timestamp
    time_label = [matlab_datenum_to_formatted_string(md) for md in ntp_label/60/60/24]
    # np.save(save_folder + "time_label", time_label)
    num_of_label = len(time_label)

    # Neural-Pace (NP) signal, GoPro videos, Pupil videos, Xsens, phone (acc, gyro, mag, GPS, light, audio)
    # fre_np = 250, fre_gopro = 60, fre_pupil = 60

    ''''''''''''''' Load modalities data '''''''''''''''
    ## load np data
    data_np = np.load(load_syncronized_folder + 'data_np.npy')
    time_np = np.load(load_syncronized_folder + 'time_np.npy')

    ## load Gopro video
    data_gopro = load_syncronized_folder + 'data_video_gopro.mp4'
    time_gopro = np.load(load_syncronized_folder + 'time_gopro.npy')

    ## load Pupil video
    data_pupil = load_syncronized_folder + 'data_video_pupil.mp4'
    time_pupil = np.load(load_syncronized_folder + 'time_pupil.npy')

    # load xsense data: only center of mass currently
    df_xsense = pd.read_csv(load_syncronized_folder + 'data_xs_Center-of-Mass.csv')
    time_xsense = np.load(load_syncronized_folder + 'time_xs.npy')
    # frame_xsense = df_xsense['Frame']
    data_xsense = df_xsense.iloc[:, 1:]
    print("xs:", time_xsense.shape, data_xsense.shape, time_xsense[0], time_xsense[-1])

    ## load all of chestphone data
    df = pd.read_csv(load_syncronized_folder + "data_chest_phone_acc.csv", header=None)
    time_chestphone_acc = df.iloc[:, 0]
    data_chestphone_acc = df.iloc[:, 1:]
    print("chest acc:", time_chestphone_acc.shape, time_chestphone_acc.iloc[0], data_chestphone_acc.shape, data_chestphone_acc.iloc[0])

    df = pd.read_csv(load_syncronized_folder + "data_chest_phone_gyro.csv", header=None)
    time_chestphone_gyro = df.iloc[:, 0]
    data_chestphone_gyro = df.iloc[:, 1:]
    print("chest gyro:", time_chestphone_gyro.shape, time_chestphone_gyro.iloc[0], data_chestphone_gyro.shape, data_chestphone_gyro.iloc[0])

    df = pd.read_csv(load_syncronized_folder + "data_chest_phone_mag.csv", header=None)
    time_chestphone_mag = df.iloc[:, 0]
    data_chestphone_mag = df.iloc[:, 1:]
    print("chest mag:", time_chestphone_mag.shape, time_chestphone_mag.iloc[0], data_chestphone_mag.shape, data_chestphone_mag.iloc[0])

    df = pd.read_csv(load_syncronized_folder + "data_chest_phone_light.csv", header=None)
    time_chestphone_light = df.iloc[:, 0]
    data_chestphone_light = df.iloc[:, 1:]
    print("chest light:", time_chestphone_light.shape, time_chestphone_light.iloc[0], data_chestphone_light.shape, data_chestphone_light.iloc[0])

    df = pd.read_csv(load_syncronized_folder + "data_chest_phone_gps.csv", header=None)
    time_chestphone_gps = df.iloc[:, 0]
    data_chestphone_gps_1 = df.iloc[:, 1].str.extract(r'Lat: (\d+\.\d+)', expand=False)## delete the str of "Lat:"
    data_chestphone_gps_1 = np.array(data_chestphone_gps_1.astype(float))
    data_chestphone_gps_2 = df.iloc[:, 2].str.extract(r'Long: (-?\d+\.\d+)', expand=False)## delete the str of "Long:"
    data_chestphone_gps_2 = np.array(data_chestphone_gps_2.astype(float))
    data_chestphone_gps = np.stack((data_chestphone_gps_1, data_chestphone_gps_2), axis=1)
    print("chest gps:", time_chestphone_gps.shape, time_chestphone_gps[0], data_chestphone_gps.shape, data_chestphone_gps[0])

    ## load all of pupilphone data
    df = pd.read_csv(load_syncronized_folder + "data_pupil_phone_acc.csv", header=None)
    time_pupilphone_acc = df.iloc[:, 0]
    data_pupilphone_acc = df.iloc[:, 1:]
    print("pupil acc:", time_pupilphone_acc.shape, time_pupilphone_acc.iloc[0], data_pupilphone_acc.shape, data_pupilphone_acc.iloc[0])

    df = pd.read_csv(load_syncronized_folder + "data_pupil_phone_gyro.csv", header=None)
    time_pupilphone_gyro = df.iloc[:, 0]
    data_pupilphone_gyro = df.iloc[:, 1:]
    print("pupil gyro:", time_pupilphone_gyro.shape, time_pupilphone_gyro.iloc[0], data_pupilphone_gyro.shape, data_pupilphone_gyro.iloc[0])

    df = pd.read_csv(load_syncronized_folder + "data_pupil_phone_mag.csv", header=None)
    time_pupilphone_mag = df.iloc[:, 0]
    data_pupilphone_mag = df.iloc[:, 1:]
    print("pupil mag:", time_pupilphone_mag.shape, time_pupilphone_mag.iloc[0], data_pupilphone_mag.shape, time_pupilphone_mag.iloc[0])

    df = pd.read_csv(load_syncronized_folder + "data_pupil_phone_gps.csv", header=None)
    time_pupilphone_gps = df.iloc[:, 0]
    data_pupilphone_gps_1 = df.iloc[:, 1].str.extract(r'Lat: (\d+\.\d+)', expand=False)## delete the str of "Lat:"
    data_pupilphone_gps_1 = np.array(data_pupilphone_gps_1.astype(float))
    data_pupilphone_gps_2 = df.iloc[:, 2].str.extract(r'Long: (-?\d+\.\d+)', expand=False)## delete the str of "Long:"
    data_pupilphone_gps_2 = np.array(data_pupilphone_gps_2.astype(float))
    data_pupilphone_gps = np.stack((data_pupilphone_gps_1, data_pupilphone_gps_2), axis=1)
    print("pupil gps:", time_pupilphone_gps.shape, time_pupilphone_gps[0], data_pupilphone_gps.shape, data_pupilphone_gps[0])

    ## Merge gps data and time in the same second - Chest phone
    time = time_chestphone_gps[0]
    gps_datas = []
    gps_times = []
    gps_data = []
    for idx in range(len(time_chestphone_gps)):
        if time_chestphone_gps[idx][:19] == time[:19]:
            gps_data.append(data_chestphone_gps[idx])
        else:
            gps_datas.append(np.mean(gps_data, axis=0))
            # print(idx, gps_datas)
            gps_times.append(time)
            gps_data.clear()
            time = time_chestphone_gps[idx]
            gps_data.append(data_chestphone_gps[idx])

    time_chestphone_gps = pd.Series(gps_times)
    data_chestphone_gps = np.array(gps_datas)

    ## Merge gps data and time in the same second - Pupil phone
    time = time_pupilphone_gps[0]
    gps_datas = []
    gps_times = []
    gps_data = []
    for idx in range(len(time_pupilphone_gps)):
        if time_pupilphone_gps[idx][:19] == time[:19]:
            gps_data.append(data_pupilphone_gps[idx])
        else:
            gps_datas.append(np.mean(gps_data, axis=0))
            # print(idx, gps_datas)
            gps_times.append(time)
            gps_data.clear()
            time = time_pupilphone_gps[idx]
            gps_data.append(data_pupilphone_gps[idx])

    time_pupilphone_gps = pd.Series(gps_times)
    data_pupilphone_gps = np.array(gps_datas)
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    # Split Frames
    # ntp_start_0 = ntp_label[0] - GoProFrame[0] / video_clip.fps
    # short_frames = [22]
    greped_index = {} # {greped_index: (greped_label, grep reason, time label)} indexs that got filtered
    label_total_time = {} # {label: datetime.timedelta} total time in one walk of each label
    label_missing_cnt = {} # {label: missing times}

    ''''''''''''''' Split data of each modality '''''''''''''''
    ## Start at "Walk Beg"
    walk_beg_index = 0
    func_extract_label = lambda index : label[index][:-4] if (label[index].endswith("Beg") or label[index].endswith("End")) else label[index]
    while label[walk_beg_index] != "Walk Beg":
        greped_index[walk_beg_index] = (func_extract_label(walk_beg_index), "Event before Walk Beg", time_label[walk_beg_index])
        walk_beg_index += 1

    file_stats = save_syncronized_splt_folder + "index_stats.csv"

    with open(file_stats, mode='a+', newline='') as f:
        writer = csv.writer(f)
        # Write the header row
        writer.writerow(["Index", "Label", "Duration", "Num of Modalities", "Missing Modalities"])
        
        temp_index = walk_beg_index + 1
        while temp_index < num_of_label:
            ## End at "Walk End"
            if label[temp_index] == "Walk End":
                break
            
            try:
                ## skip "xxx End" events
                if label[temp_index].endswith("End"):
                    continue
                
                start_frame_index = temp_index
                end_frame_index = start_frame_index + 1

                cut_label = func_extract_label(start_frame_index)

                ## grep not interested labels
                if cut_label not in ["Doorway", "Talking", "Correct Turn", "Incorrect Turn", "Lost", "Stop", "Abnormal", "Pointing", "Outdoor", "Choice Point", "Stare", "New Context"]:
                    greped_index[start_frame_index] = (cut_label, "Not intereted event", time_label[start_frame_index])
                    print("Greped: ", "Not intereted event")
                    continue

                ## Find end_frame_index
                if label[start_frame_index].endswith("Beg"):
                    while end_frame_index < num_of_label:
                        if label[end_frame_index].endswith("End") and func_extract_label(end_frame_index) == cut_label:
                            break
                        end_frame_index += 1
                    if end_frame_index >= num_of_label:
                        raise ValueError(f"Corresponding End event missing: {start_frame_index} {cut_label}")
                # else: # merge successive identical label
                #     while func_extract_label(end_frame_index) == cut_label and end_frame_index < num_of_label:
                #         end_frame_index += 1
                #     temp_index = end_frame_index - 1 # align with the "+1" later
                ########################

                modality_num = 0
                missing_modality = []
                do_extract = True

                print("Frame ", start_frame_index, ":")
                print("label: ", label[start_frame_index])
                print("End frame index:", end_frame_index)
                # input("Press to continue......")
                print("time_label: ", time_label[start_frame_index], time_label[end_frame_index], calculate_duration(time_label[start_frame_index], time_label[end_frame_index]))

                ############### grep invalid data. If one of gopro/pupil/np frame is missing, grep all data ###############
                start_frame_gopro = GoProFrame[start_frame_index]
                end_frame_gopro = GoProFrame[end_frame_index]
                dura_gopro = calculate_duration(time_gopro[start_frame_gopro], time_gopro[end_frame_gopro])
                # print("time_gopro: ", time_gopro[start_frame_gopro], time_gopro[end_frame_gopro], calculate_duration(time_gopro[start_frame_gopro], time_gopro[end_frame_gopro]))

                if end_frame_gopro <= start_frame_gopro:
                    label_missing_cnt['gopro'] = label_missing_cnt.get('gopro', 0) + 1
                    greped_index[start_frame_index] = (cut_label, 'gopro', time_label[start_frame_index])
                    print("Greped: ", "gopro")
                    do_extract = False
                    # raise ValueError("End frame must be greater than start frame:gopro")

                ############### sample np signals ###############
                start_frame_np = NPSample[start_frame_index]
                end_frame_np = NPSample[end_frame_index]
                # print("time_np: ", time_np[start_frame_np], time_np[end_frame_np-1], calculate_duration(time_np[start_frame_np], time_np[end_frame_np-1]), data_np[start_frame_np:end_frame_np].shape) # the extracted end_frame_np is started from 1, so need to subtract 1 when apply to time_np. data_np slice won't include end_frame_np. Other modalities don't have this problem.
                if end_frame_np <= start_frame_np:
                    label_missing_cnt['np'] = label_missing_cnt.get('np', 0) + 1
                    greped_index[start_frame_index] = (cut_label, 'np', time_label[start_frame_index])
                    print("Greped: ", "np")
                    do_extract = False
                else:
                    extract_modalities(start_frame_index=start_frame_index, end_frame_index=end_frame_index,
                                       time_arr=NPSample, data_arr=data_np,
                                       time_label=None,
                                       save_syncronized_splt_folder=save_syncronized_splt_folder,
                                       modality='np',
                                       time_window=time_window,
                                       modality_freq=250,
                                       do_extract=do_extract)
                    modality_num += 1

                ############### sample gopro videos ###############
                if do_extract:
                    output_path = save_syncronized_splt_folder + '{}_gopro.mp4'.format(start_frame_index)
                    output_path_audio = save_syncronized_splt_folder + '{}_gopro_audio.wav'.format(start_frame_index)
                    extract_video_audio_subset(data_gopro, start_frame_gopro, end_frame_gopro, output_path, output_path_audio, time_window=time_window, fps=fps_for_frame)
                    modality_num += 2 # will extract two modalities
                
                    output_path = save_syncronized_splt_folder + '{}_pupil.mp4'.format(start_frame_index)
                    extract_video_noaudio_subset(data_pupil, start_frame_gopro, end_frame_gopro, output_path, time_window=time_window, fps=fps_for_frame)
                    modality_num += 1

                ############### sample other data ###############
                if extract_modalities(start_frame_index, end_frame_index,
                                      time_chestphone_acc, data_chestphone_acc,
                                      time_label=time_label,
                                      save_syncronized_splt_folder=save_syncronized_splt_folder,
                                      modality='chestphone_acc',
                                      time_window=time_window,
                                      modality_freq=100,
                                      do_extract=do_extract
                                    ):
                    modality_num += 1
                else:
                    missing_modality.append('chestphone_acc')
                
                if extract_modalities(start_frame_index, end_frame_index,
                                      time_chestphone_gyro, data_chestphone_gyro,
                                      time_label=time_label,
                                      save_syncronized_splt_folder=save_syncronized_splt_folder,
                                      modality='chestphone_gyro',
                                      time_window=time_window,
                                      modality_freq=50,
                                      do_extract=do_extract
                                    ):
                    modality_num += 1
                else:
                    missing_modality.append('chestphone_gyro')
                
                if extract_modalities(start_frame_index, end_frame_index,
                                      time_chestphone_mag, data_chestphone_mag,
                                      time_label=time_label,
                                      save_syncronized_splt_folder=save_syncronized_splt_folder,
                                      modality='chestphone_mag',
                                      time_window=time_window,
                                      modality_freq=50,
                                      do_extract=do_extract
                                    ):
                    modality_num += 1
                else:
                    missing_modality.append('chestphone_mag')
                
                if extract_modalities(start_frame_index, end_frame_index,
                                      time_chestphone_gps, data_chestphone_gps,
                                      time_label=time_label,
                                      save_syncronized_splt_folder=save_syncronized_splt_folder,
                                      modality='chestphone_gps',
                                      time_window=None,
                                      modality_freq=None,
                                      do_extract=do_extract
                                    ):
                    modality_num += 1
                else:
                    missing_modality.append('chestphone_gps')
                
                if extract_modalities(start_frame_index, end_frame_index,
                                      time_chestphone_light, data_chestphone_light,
                                      time_label=time_label,
                                      save_syncronized_splt_folder=save_syncronized_splt_folder,
                                      modality='chestphone_light',
                                      time_window=time_window,
                                      modality_freq=10,
                                      do_extract=do_extract
                                    ):
                    modality_num += 1
                else:
                    missing_modality.append('chestphone_light')
                
                if extract_modalities(start_frame_index, end_frame_index,
                                      time_pupilphone_acc, data_pupilphone_acc,
                                      time_label=time_label,
                                      save_syncronized_splt_folder=save_syncronized_splt_folder,
                                      modality='pupilphone_acc',
                                      time_window=time_window,
                                      modality_freq=100,
                                      do_extract=do_extract
                                    ):
                    modality_num += 1
                else:
                    missing_modality.append('pupilphone_acc')
                
                if extract_modalities(start_frame_index, end_frame_index,
                                      time_pupilphone_gyro, data_pupilphone_gyro,
                                      time_label=time_label,
                                      save_syncronized_splt_folder=save_syncronized_splt_folder,
                                      modality='pupilphone_gyro',
                                      time_window=time_window,
                                      modality_freq=50,
                                      do_extract=do_extract
                                    ):
                    modality_num += 1
                else:
                    missing_modality.append('pupilphone_gyro')
                
                if extract_modalities(start_frame_index, end_frame_index,
                                      time_pupilphone_mag, data_pupilphone_mag,
                                      time_label=time_label,
                                      save_syncronized_splt_folder=save_syncronized_splt_folder,
                                      modality='pupilphone_mag',
                                      time_window=time_window,
                                      modality_freq=50,
                                      do_extract=do_extract
                                    ):
                    modality_num += 1
                else:
                    missing_modality.append('pupilphone_mag')
                
                if extract_modalities(start_frame_index, end_frame_index,
                                      time_pupilphone_gps, data_pupilphone_gps,
                                      time_label=time_label,
                                      save_syncronized_splt_folder=save_syncronized_splt_folder,
                                      modality='pupilphone_gps',
                                      time_window=None,
                                      modality_freq=None,
                                      do_extract=do_extract
                                    ):
                    modality_num += 1
                else:
                    missing_modality.append('pupilphone_gps')
                
                if extract_modalities(start_frame_index, end_frame_index,
                                      time_xsense, data_xsense,
                                      modality='xs_CoM',
                                      time_label=time_label,
                                      save_syncronized_splt_folder=save_syncronized_splt_folder,
                                      time_window=time_window,
                                      modality_freq=100,
                                      do_extract=do_extract
                                    ):
                    modality_num += 1
                else:
                    missing_modality.append('xs_CoM')

                ############### record label time ###############
                if do_extract:
                    dura = calculate_duration(time_label[start_frame_index], time_label[end_frame_index])
                    label_total_time[cut_label] = label_total_time.get(cut_label, datetime.timedelta()) + dura
                    writer.writerow([start_frame_index, cut_label, dura, modality_num, ", ".join(missing_modality)])
            except Exception as e:
                greped_index[start_frame_index] = (cut_label, str(e), time_label[start_frame_index])
                print("Exception:", str(e))
                # raise Exception(e)
            finally:
                temp_index += 1

    assert (temp_index == num_of_label or label[temp_index] == "Walk End"), f"Unexpected exit: temp_index={temp_index}"
    for i in range(temp_index, num_of_label):
        greped_index[i] = (func_extract_label(i), "Event after Walk End", time_label[i])
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''


    ''''''''''''''' Save statistical results '''''''''''''''
    # write index label map, greped index and label total time into .csv file
    file_label_time = save_syncronized_splt_folder + "cal_label_time.csv"
    file_greped = save_syncronized_splt_folder + "greped_index.csv"
    file_miss = save_syncronized_splt_folder + "missing_label_cnt.csv"

    # Writing the dictionary to a CSV file with multiple columns

    print("Writing total time of each label......")
    with open(file_label_time, mode='w', newline='') as f:
        writer = csv.writer(f)
        # Write the header row
        writer.writerow(['Label', 'Total Time in Walk'])
        # Write the dictionary entries
        for i_label, i_time in label_total_time.items():
            writer.writerow([i_label, str(i_time)])
    print(f"Total time of each label has been saved to {file_label_time}")

    print("Writing greped label......")
    with open(file_greped, mode='w', newline='') as f:
        writer = csv.writer(f)
        # Write the header row
        writer.writerow(['Index', 'Label', 'Grep Reason', 'Time Label'])
        # Write the dictionary entries
        for index, value in greped_index.items():
            i_label, reason, time_label = value
            writer.writerow([index, i_label, reason, time_label])
    print(f"Greped label has been saved to {file_greped}")

    print("Writing counts of label......")
    with open(file_miss, mode='w', newline='') as f:
        writer = csv.writer(f)
        # Write the header row
        writer.writerow(['Modality', 'Missing Count'])
        # Write the dictionary entries
        for i_label, cnt in label_missing_cnt.items():
            writer.writerow([i_label, cnt])
    print(f"Counts of missing labels have been saved to {file_miss}")

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''