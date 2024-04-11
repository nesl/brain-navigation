import numpy as np
import scipy.io
import ntplib
import datetime
# from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt
import os
import pandas as pd
import cv2
from moviepy.editor import VideoFileClip, concatenate_videoclips
import re


def extract_video_subset(video_path, start_frame, end_frame, output_path):
    """
    Extract a subset of frames from a video file while keeping a subset of the audio.

    Parameters:
        video_path (str): Path to the input video file.
        start_frame (int): Starting frame index.
        end_frame (int): Ending frame index.
        output_path (str): Path to save the output video file.
    """
    # Load video clip
    video_clip = VideoFileClip(video_path)

    print("video_clip.fps:", video_clip.fps)

    # Extract audio
    audio_clip = video_clip.audio

    # Extract subset of audio
    subset_audio_clip = audio_clip.subclip(start_frame / video_clip.fps, end_frame / video_clip.fps)

    # Extract subset of frames
    subset_clip = video_clip.subclip(start_frame / video_clip.fps, end_frame / video_clip.fps)

    # Set audio for subset clip
    subset_clip = subset_clip.set_audio(subset_audio_clip)

    # Write video file with audio
    subset_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

    # Close the video clip
    video_clip.close()


def extract_video_noaudio_subset(video_path, start_frame, end_frame, output_path):
    """
    Extract a subset of frames from a video file without including audio.

    Parameters:
        video_path (str): Path to the input video file.
        start_frame (int): Starting frame index.
        end_frame (int): Ending frame index.
        output_path (str): Path to save the output video file.
    """
    # Load video clip
    video_clip = VideoFileClip(video_path)

    # Extract subset of frames
    subset_clip = video_clip.subclip(start_frame / video_clip.fps, end_frame / video_clip.fps)

    # Write video file without audio
    subset_clip.write_videofile(output_path, codec="libx264", audio=False)

    # Close the video clip
    video_clip.close()

def extract_video_audio_subset(video_path, start_frame, end_frame, output_video_path, output_audio_path):
    """
    Extract a subset of frames from a video file and save the video and audio separately.

    Parameters:
        video_path (str): Path to the input video file.
        start_frame (int): Starting frame index.
        end_frame (int): Ending frame index.
        output_video_path (str): Path to save the output video file.
        output_audio_path (str): Path to save the output audio file.
    """
    # Validate input parameters
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found at {video_path}")
    if start_frame < 0 or end_frame < 0:
        raise ValueError("Frame indices must be non-negative")
    if end_frame <= start_frame:
        raise ValueError("End frame must be greater than start frame")

    # Load video clip
    video_clip = VideoFileClip(video_path)

    # Extract subset of frames
    subset_clip = video_clip.subclip(start_frame / video_clip.fps, end_frame / video_clip.fps)

    # Write video file
    subset_clip.write_videofile(output_video_path, codec="libx264")

    # Close the video clip
    subset_clip.close()

    # Extract audio
    audio_clip = video_clip.audio

    # Calculate time in seconds for subclipping
    start_time = start_frame / video_clip.fps
    end_time = end_frame / video_clip.fps

    # Extract subset of audio
    subset_audio_clip = audio_clip.subclip(start_time, end_time)

    # Write audio file
    subset_audio_clip.write_audiofile(output_audio_path)

    # Close the audio clip
    subset_audio_clip.close()

    # Close the video clip
    video_clip.close()


def matlab_datenum_to_formatted_string(matlab_datenum):

    # Convert MATLAB datenum to Python datenum by subtracting the MATLAB epoch
    python_datenum = matlab_datenum# - 366  # Adjust for MATLAB epoch

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
        str: Duration between the two datetime strings.
    """
    # Convert the datetime strings to datetime objects
    datetime_obj1 = datetime.datetime.strptime(datetime_str1, '%Y-%m-%d_%H-%M-%S-%f')
    datetime_obj2 = datetime.datetime.strptime(datetime_str2, '%Y-%m-%d_%H-%M-%S-%f')

    # Calculate the duration
    duration = datetime_obj2 - datetime_obj1

    # Return the duration as a string
    return str(duration)


def find_close_frame(time_label, time_data_array):

    frame_index_data = 0
    time_label_num = datetime.datetime.strptime(time_label, '%Y-%m-%d_%H-%M-%S-%f')

    for temp_index in range(time_data_array.shape[0]):

        # print(time_label, time_data_array[temp_index])
        temp_time_data = datetime.datetime.strptime(time_data_array[temp_index], '%Y-%m-%d_%H-%M-%S-%f')

        if temp_time_data >= time_label_num:

            frame_index_data = temp_index
            # print("syncronze frame: ", frame_index_data, time_label, time_data_array[temp_index])
            break

    return frame_index_data


# Event Description PupilFrame  GoProFrame  NPSample    NTP
df = pd.read_csv('../label_RWNApp_Output_Jan2024/evnts_RWNApp_RW1_Walk1.csv')
label = df['Event']
ntp_label = df['NTP']
PupilFrame = df['PupilFrame']
GoProFrame = df['GoProFrame']
NPSample = df['NPSample']

# convert matlab NTP time to datetime timestamp
time_label = [matlab_datenum_to_formatted_string(md) for md in ntp_label/60/60/24]
# np.save(save_folder + "time_label", time_label)
num_of_label = len(time_label)


# fre_np = 250, fre_gopro = 60, fre_pupil = 60
# Load all data and timestamp: Neural-Pace (NP) signal, GoPro videos, Pupil videos, Xsens, phone (acc, gyro, mag, GPS, light, audio)
load_syncronized_folder = "../RW1/RW1-Walk1-extracted/"
save_syncronized_splt_folder = "../RW1/RW1-Walk1-self-syncronize-split/"

## load np data
data_np = np.load(load_syncronized_folder + 'data_np.npy')
time_np = np.load(load_syncronized_folder + 'time_np.npy')

## load Gopro video
data_gopro = load_syncronized_folder + 'data_gopro_video.mp4'
time_gopro = np.load(load_syncronized_folder + 'time_gopro.npy')

## load Pupil video
data_pupil = load_syncronized_folder + 'data_pupil_video.mp4'
time_pupil = np.load(load_syncronized_folder + 'time_pupil.npy')

## load xsense data: only center of mass currently
df_xsense = pd.read_csv(load_syncronized_folder + 'data_xs_Center-of-Mass.csv')
time_xsense = np.load(load_syncronized_folder + 'time_xs.npy')
data_xsense = df_xsense.iloc[:, 1:]

print(time_xsense.shape, data_xsense.shape, time_xsense[0], time_xsense[-1])

## load all of chestphone data
df = pd.read_csv(load_syncronized_folder + "data_chestphone_acc.csv", header=None)
time_chestphone_acc = df.iloc[:, 0]
data_chestphone_acc = df.iloc[:, 1:]
print(time_chestphone_acc.shape, data_chestphone_acc.shape)

df = pd.read_csv(load_syncronized_folder + "data_chestphone_gyro.csv", header=None)
time_chestphone_gyro = df.iloc[:, 0]
data_chestphone_gyro = df.iloc[:, 1:]
print(time_chestphone_gyro.shape, data_chestphone_gyro.shape)

df = pd.read_csv(load_syncronized_folder + "data_chestphone_mag.csv", header=None)
time_chestphone_mag = df.iloc[:, 0]
data_chestphone_mag = df.iloc[:, 1:]
print(time_chestphone_mag.shape, data_chestphone_mag.shape)

df = pd.read_csv(load_syncronized_folder + "data_chestphone_light.csv", header=None)
time_chestphone_light = df.iloc[:, 0]
data_chestphone_light = df.iloc[:, 1:]
print(time_chestphone_light.shape, data_chestphone_light.shape)

df = pd.read_csv(load_syncronized_folder + "data_chestphone_gps.csv", header=None)
time_chestphone_gps = df.iloc[:, 0]
data_chestphone_gps_1 = df.iloc[:, 1].str.extract(r'Lat: (\d+\.\d+)', expand=False)## delete the str of "Lat:"
data_chestphone_gps_1 = np.array(data_chestphone_gps_1.astype(float))
data_chestphone_gps_2 = df.iloc[:, 2].str.extract(r'Long: (-?\d+\.\d+)', expand=False)## delete the str of "Long:"
data_chestphone_gps_2 = np.array(data_chestphone_gps_2.astype(float))
data_chestphone_gps = np.stack((data_chestphone_gps_1, data_chestphone_gps_2))
print(data_chestphone_gps.shape, time_chestphone_gps.shape)


## load all of pupilphone data
df = pd.read_csv(load_syncronized_folder + "data_pupilphone_acc.csv", header=None)
time_pupilphone_acc = df.iloc[:, 0]
data_pupilphone_acc = df.iloc[:, 1:]
print(data_pupilphone_acc.shape, data_pupilphone_acc.shape)

df = pd.read_csv(load_syncronized_folder + "data_pupilphone_gyro.csv", header=None)
time_pupilphone_gyro = df.iloc[:, 0]
data_pupilphone_gyro = df.iloc[:, 1:]
print(time_pupilphone_gyro.shape, data_pupilphone_gyro.shape)

df = pd.read_csv(load_syncronized_folder + "data_pupilphone_mag.csv", header=None)
time_pupilphone_mag = df.iloc[:, 0]
data_pupilphone_mag = df.iloc[:, 1:]
print(time_pupilphone_mag.shape, data_pupilphone_mag.shape)

df = pd.read_csv(load_syncronized_folder + "data_pupilphone_gps.csv", header=None)
time_pupilphone_gps = df.iloc[:, 0]
data_pupilphone_gps_1 = df.iloc[:, 1].str.extract(r'Lat: (\d+\.\d+)', expand=False)## delete the str of "Lat:"
data_pupilphone_gps_1 = np.array(data_pupilphone_gps_1.astype(float))
data_pupilphone_gps_2 = df.iloc[:, 2].str.extract(r'Long: (-?\d+\.\d+)', expand=False)## delete the str of "Long:"
data_pupilphone_gps_2 = np.array(data_pupilphone_gps_2.astype(float))
data_pupilphone_gps = np.stack((data_pupilphone_gps_1, data_pupilphone_gps_2))
print(data_pupilphone_gps.shape, data_pupilphone_gps.shape)


for temp_index in range(label.shape[0]):

    start_frame_index = temp_index
    end_frame_index = temp_index + 1

    print("\nlabel: ", label[temp_index])
    print("time_label: ", time_label[start_frame_index], time_label[end_frame_index], calculate_duration(time_label[start_frame_index], time_label[end_frame_index]))

    ## sample gopro videos
    start_frame = GoProFrame[start_frame_index]
    end_frame = GoProFrame[end_frame_index]
    print("time_gopro: ", time_gopro[start_frame], time_gopro[end_frame], calculate_duration(time_gopro[start_frame], time_gopro[end_frame]))

    if end_frame <= start_frame:
        continue
    output_path = save_syncronized_splt_folder + '{}_gopro.mp4'.format(temp_index)
    output_path_audio = save_syncronized_splt_folder + '{}_gopro_audio.wav'.format(temp_index)
    extract_video_audio_subset(data_gopro, start_frame, end_frame, output_path, output_path_audio)

    ## sample pupil videos, the same frame with GoPro using the syncronized videos
    start_frame = GoProFrame[start_frame_index]
    end_frame = GoProFrame[end_frame_index]
    print("time_pupil: ", time_gopro[start_frame], time_gopro[end_frame], calculate_duration(time_gopro[start_frame], time_gopro[end_frame]))

    if end_frame <= start_frame:
        continue
    output_path = save_syncronized_splt_folder + '{}_pupil.mp4'.format(temp_index)
    extract_video_noaudio_subset(data_pupil, start_frame, end_frame, output_path)

    # sample np signals
    start_frame = NPSample[start_frame_index]
    end_frame = NPSample[end_frame_index]
    print("time_np: ", time_np[start_frame], time_np[end_frame], calculate_duration(time_np[start_frame], time_np[end_frame]), data_np[start_frame:end_frame].shape)

    if end_frame <= start_frame:
        continue
    output_path = save_syncronized_splt_folder + '{}_np.npy'.format(temp_index)
    np.save(output_path, data_np[start_frame:end_frame])

    ## sample xsense signals
    start_frame = find_close_frame(time_label[start_frame_index], time_xsense)
    end_frame = find_close_frame(time_label[end_frame_index], time_xsense)
    print("time_xsense: ", time_xsense[start_frame], time_xsense[end_frame], calculate_duration(time_xsense[start_frame], time_xsense[end_frame]))

    if end_frame <= start_frame:
        continue
    output_path = save_syncronized_splt_folder + '{}_xs_CoM.npy'.format(temp_index)
    np.save(output_path, data_xsense[start_frame:end_frame])

    # sample chestphone data
    # acc
    start_frame = find_close_frame(time_label[start_frame_index], time_chestphone_acc)
    end_frame = find_close_frame(time_label[end_frame_index], time_chestphone_acc)
    print("time_chestphone_acc: ", time_chestphone_acc[start_frame], time_chestphone_acc[end_frame], calculate_duration(time_chestphone_acc[start_frame], time_chestphone_acc[end_frame]))

    if end_frame <= start_frame:
        continue
    output_path = save_syncronized_splt_folder + '{}_chestphone_acc.npy'.format(temp_index)
    np.save(output_path, data_chestphone_acc[start_frame:end_frame])

    ## gyro
    start_frame = find_close_frame(time_label[start_frame_index], time_chestphone_gyro)
    end_frame = find_close_frame(time_label[end_frame_index], time_chestphone_gyro)
    print("time_chestphone_gyro: ", time_chestphone_gyro[start_frame], time_chestphone_gyro[end_frame], calculate_duration(time_chestphone_gyro[start_frame], time_chestphone_gyro[end_frame]))

    if end_frame <= start_frame:
        continue
    output_path = save_syncronized_splt_folder + '{}_chestphone_gyro.npy'.format(temp_index)
    np.save(output_path, data_chestphone_gyro[start_frame:end_frame])
    
    ## mag
    start_frame = find_close_frame(time_label[start_frame_index], time_chestphone_mag)
    end_frame = find_close_frame(time_label[end_frame_index], time_chestphone_mag)
    print("time_chestphone_mag: ", time_chestphone_mag[start_frame], time_chestphone_mag[end_frame], calculate_duration(time_chestphone_mag[start_frame], time_chestphone_mag[end_frame]))

    if end_frame <= start_frame:
        continue
    output_path = save_syncronized_splt_folder + '{}_chestphone_mag.npy'.format(temp_index)
    np.save(output_path, data_chestphone_mag[start_frame:end_frame])

    ## gps
    start_frame = find_close_frame(time_label[start_frame_index], time_chestphone_gps)
    end_frame = find_close_frame(time_label[end_frame_index], time_chestphone_gps)
    print("time_chestphone_gps: ", time_chestphone_gps[start_frame], time_chestphone_gps[end_frame], calculate_duration(time_chestphone_gps[start_frame], time_chestphone_gps[end_frame]))

    if end_frame <= start_frame:
        continue
    output_path = save_syncronized_splt_folder + '{}_chestphone_gps.npy'.format(temp_index)
    np.save(output_path, data_chestphone_gps[start_frame:end_frame])

    ## light
    start_frame = find_close_frame(time_label[start_frame_index], time_chestphone_light)
    end_frame = find_close_frame(time_label[end_frame_index], time_chestphone_light)
    print("time_chestphone_light: ", time_chestphone_light[start_frame], time_chestphone_light[end_frame], calculate_duration(time_chestphone_light[start_frame], time_chestphone_light[end_frame]))

    if end_frame <= start_frame:
        continue
    output_path = save_syncronized_splt_folder + '{}_chestphone_light.npy'.format(temp_index)
    np.save(output_path, data_chestphone_light[start_frame:end_frame])


    ## sample pupilphone data
    ## acc
    start_frame = find_close_frame(time_label[start_frame_index], time_pupilphone_acc)
    end_frame = find_close_frame(time_label[end_frame_index], time_pupilphone_acc)
    print("time_pupilphone_acc: ", time_pupilphone_acc[start_frame], time_pupilphone_acc[end_frame], calculate_duration(time_pupilphone_acc[start_frame], time_pupilphone_acc[end_frame]))

    if end_frame <= start_frame:
        continue
    output_path = save_syncronized_splt_folder + '{}_pupilphone_acc.npy'.format(temp_index)
    np.save(output_path, data_pupilphone_acc[start_frame:end_frame])

    ## gyro
    start_frame = find_close_frame(time_label[start_frame_index], time_pupilphone_gyro)
    end_frame = find_close_frame(time_label[end_frame_index], time_pupilphone_gyro)
    print("time_pupilphone_gyro: ", time_pupilphone_gyro[start_frame], time_pupilphone_gyro[end_frame], calculate_duration(time_pupilphone_gyro[start_frame], time_pupilphone_gyro[end_frame]))

    if end_frame <= start_frame:
        continue
    output_path = save_syncronized_splt_folder + '{}_pupilphone_gyro.npy'.format(temp_index)
    np.save(output_path, data_pupilphone_gyro[start_frame:end_frame])
    
    ## mag
    start_frame = find_close_frame(time_label[start_frame_index], time_pupilphone_mag)
    end_frame = find_close_frame(time_label[end_frame_index], time_pupilphone_mag)
    print("time_pupilphone_mag: ", time_pupilphone_mag[start_frame], time_pupilphone_mag[end_frame], calculate_duration(time_pupilphone_mag[start_frame], time_pupilphone_mag[end_frame]))

    if end_frame <= start_frame:
        continue
    output_path = save_syncronized_splt_folder + '{}_pupilphone_mag.npy'.format(temp_index)
    np.save(output_path, data_pupilphone_mag[start_frame:end_frame])

    ## gps
    start_frame = find_close_frame(time_label[start_frame_index], time_pupilphone_gps)
    end_frame = find_close_frame(time_label[end_frame_index], time_pupilphone_gps)
    print("time_pupilphone_gps: ", time_pupilphone_gps[start_frame], time_pupilphone_gps[end_frame], calculate_duration(time_pupilphone_gps[start_frame], time_pupilphone_gps[end_frame]))

    if end_frame <= start_frame:
        continue
    output_path = save_syncronized_splt_folder + '{}_pupilphone_gps.npy'.format(temp_index)
    np.save(output_path, data_pupilphone_gps[start_frame:end_frame])

