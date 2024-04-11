# Brain-Navigation Dataset Processing
Code Repository to pre-process the Brain Navigation Data

## Overview of the dataset
### Sensor data
- Neural-Pace (NP) signal: 250Hz, 4 channels, may need to remove the large spikes
- Physics sensor system: Gopro videos (60Hz), Pupil videos (60Hz), Xsens (100Hz, acc), Chestphone (acc, gyro, mag, GPS, light), PupilePhone (acc, gyro, mag, GPS, light)

### Annotation of the events: 
- Original annotation (16 events in total) Doorway, Talking Beg/End, Correct Turn Beg/End,  Incorrect Turn Beg/End, Lost Beg/End, Stop Beg/End, Abnormal, Pointing, Notes, Outdoor, Choice Point, Stare, Held Door, Clapper, Landmark, Beg/End, New Context Beg/End
- Events of Interests (13 events): Doorway, Talking, Correct Turn,  Incorrect Turn, Lost, Stop, Abnormal, Pointing, Outdoor, Choice Point, Stare, Beg/End, New Context
  
## Tasks of data processing
- Step 1: Extract labels, data and timestamp from matlab files; and put other valid sensor data in the same folder.
    - Extract labels from matlab files, and save to csv files: ```extract_mat_label.m```
    - Extrac data and timestamp from matlab files, and save to the same folder: ```extract_mat_data.py```
    - Copy other valid sensor data (sepecify in the next section) to the same folder ```RW1-Walk1-extracted```: currently done manually, could be done automatically by code later. Examples of extracted datafolder [here](https://drive.google.com/drive/folders/1KQeMCWv0vR59Ny9mFTZfRZDt0bZX52QE?usp=sharing).
- Step 2: Synchronize all sensor data using NTP timestamp; Split them according to each event and save corresponding labels.
    - ```syncronize.py```. Examples of syncronized datafolder [here](https://drive.google.com/drive/folders/1KQeMCWv0vR59Ny9mFTZfRZDt0bZX52QE?usp=sharing).
- Step 3: Select data from 13 events of interest.
- Step 4: Slice data into windows of T seconds (T needs to be defined later) and filter out invalid data.
- Step 5: Scale to different subjects and walking sessions.

### Data and timestamp of each sensor for synchronizing (for Step 1)
- Videos:
    - Data: We use videos from the “Synced” folder, as they are concatenated to one video. And we split audio from videos.
        - Data in “Synced” folder: pupil and Gopro video are both 60fps; synchronized and have the same length.
        - Data in “Original” folder: pupil video is 80fps; Gopro video is 60fps and has multiple videos; Gopro and pupil videos have time shifts.
    - Timestamp: We use frames from “RWNApp_RW1_Walk1.mat” for synchronization.
- Xsense:
    - Data: We use data from “Original” folder, and only choose “xs_Center-of-Mass.csv”.
    - Timestamp: We use timestamps from “RWNApp_RW1_Walk1.mat” for synchronization.
- Phone data:
    - Data: We use data from “Original” folder
        - “ChestPhone”: light, acc, gyro, mag, GPS
        - “PupilPhone”: acc, gyro, mag, GPS
    - Timestamp: We use NTP time in each csv file for synchronization.
- Label: “label_RWNApp_Output_Jan2024”

### Data after synchronization: 14 files for each event (for Step 2)
- {}_gopro.mp4, {}_pupil.mp4, {}_gopro_audio.wav, 
- {}_np.npy, 
- {}_xs_CoM.npy, 
- {}_chestphone_acc.npy, {}_chestphone_gyro.npy, {}_chestphone_mag.npy, {}_chestphone_gps.npy, {}_chestphone_light.npy, 
- {}_pupilphone_acc.npy, {}_pupilphone_gyro.npy, {}_pupilphone_mag.npy, {}_pupilphone_gps.npy

  
## Problems of scaling in data processing: 
- Heterogeneity lengths of events: how to slice the data
    - some events are instant (several frames): Doorway, Choice Point
    - some events are short (<2s): Correct Turn, Lost
    - some events are long (>2s): New Context Beg-New Context End, Include other short events in between
      
  **Need to verrify the window used for analyzing the brain signal.** For example, the instant event may be the center of the window (10 seconds).

- Unify the event name: Talking Beg, Talking End -> Talking
- Missing modality in some sessions and some timestamps (run-time failure)

