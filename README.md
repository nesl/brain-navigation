# Brain-Navigation Dataset Processing
Code Repository to pre-process the Brain Navigation Data

## Sensor data
- Neural-Pace (NP) signal: 250Hz, 4 channels, may need to remove the large spikes
- Physics sensor system: Gopro videos (60Hz), Pupil videos (60Hz), Xsens (100Hz, acc), Chestphone (acc, gyro, mag, GPS, light), PupilePhone (acc, gyro, mag, GPS, light)

## Annotation of the events: 
- Original annotation (16 events in total) Doorway, Talking Beg/End, Correct Turn Beg/End,  Incorrect Turn Beg/End, Lost Beg/End, Stop Beg/End, Abnormal, Pointing, Notes, Outdoor, Choice Point, Stare, Held Door, Clapper, Landmark, Beg/End, New Context Beg/End
- Events of Interests (13 events): Doorway, Talking, Correct Turn,  Incorrect Turn, Lost, Stop, Abnormal, Pointing, Outdoor, Choice Point, Stare, Beg/End, New Context
  
## Tasks of data processing
- Extract and put all valid sensor data in the same folder: extract_mat_data.py
- Synchronize all sensor data using NTP timestamp; Split them according to each event and save corresponding labels: syncronize.py
- Select data from 13 events of interest.
- Slice data into windows of T seconds (T needs to be defined later) and filter out invalid data.
- Scale to different subjects and walking sessions.

### Data and timestamp of each sensor for synchronizing 
- Videos:
    - We use videos from the “Synced” folder, as they are concatenated to one video. And we split audio from videos.
          - Data in “Synced” folder: pupil and Gopro video are both 60fps; synchronized and have the same length.
          - Data in “Original” folder: pupil video is 80fps; Gopro video is 60fps and has multiple videos; Gopro and pupil videos have time shifts.
    - We use frames from “RWNApp_RW1_Walk1.mat” for synchronization.
- Xsense:
    - We use data from “Original” folder, and only choose “xs_Center-of-Mass.csv”.
    - We use timestamps from “RWNApp_RW1_Walk1.mat” for synchronization.
- Phone data:
    - We use data from “Original” folder
        - “ChestPhone”: light, acc, gyro, mag, GPS
        - “PupilPhone”: acc, gyro, mag, GPS
    - We use NTP time in each csv file for synchronization.
- Label: “label_RWNApp_Output_Jan2024”

### Data after synchronization: 14 files for each event
- {}_gopro.mp4, {}_pupil.mp4, {}_gopro_audio.wav, 
- {}_np.npy, 
- {}_xs_CoM.npy, 
- {}_chestphone_acc.npy, {}_chestphone_gyro.npy, {}_chestphone_mag.npy, {}_chestphone_gps.npy,
- {}_chestphone_light.npy, 
- {}_pupilphone_acc.npy, {}_pupilphone_gyro.npy, {}_pupilphone_mag.npy, {}_pupilphone_gps.npy

  
## Problems of scaling in data processing: 
- Heterogeneity lengths of events: how to slice the data
    - some events are instant (several frames): Doorway, Choice Point
    - Center of the window (10 seconds): the window used for analyzing the brain signal
    - some events are short (<2s): Correct Turn, Lost
    - some events are long (>2s): New Context Beg-New Context End, Include other short events in between
- Unify the event name: Talking Beg, Talking End -> Talking
- Missing modality in some sessions and some timestamps (run-time failure)

