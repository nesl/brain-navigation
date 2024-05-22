# RW1 Data Processing Record

### Data amount of modalities

|       | GoPro Video&Audio | Pupil Video | Neural Pace (NP) | Xsens | chestphone acc | chestphone  gyro | chestphone mag | chestphone light | chestphone gps | pupilphone acc | pupilphone gyro | pupilphone mag | pupilphone gps |
| ----- | ----------------- | ----------- | ---------------- | ----- | -------------- | ---------------- | -------------- | ---------------- | -------------- | -------------- | --------------- | -------------- | -------------- |
| Walk1 | 137               | 137         | 137              | 137   | 119            | 118              | 117            | 117              | 89             | 114            | 114             | 112            | 92             |
| Walk2 | 0                 | 0           | 183              | 0     | 139            | 138              | 137            | 136              | 130            | 130            | 130             | 132            | 144            |
| Walk3 | 152               | 152         | 152              | 0     | 127            | 127              | 127            | 119              | 66             | 128            | 128             | 128            | 116            |
| Walk4 | 153               | 153         | 153              | 153   | 124            | 124              | 124            | 115              | 104            | 130            | 130             | 130            | 106            |
| Walk5 | 0                 | 0           | 146              | 145   | 0              | 0                | 0              | 0                | 0              | 127            | 126             | 127            | 102            |
| Walk6 | 0                 | 0           | 181              | 180   | 126            | 126              | 125            | 117              | 122            | 123            | 121             | 123            | 141            |
| Walk7 | 135               | 135         | 135              | 135   | 103            | 103              | 102            | 99               | 94             | 99             | 98              | 98             | 78             |

### Notes

Walk1: 

- Videos in `Synced`: GoPro video fps=60, Pupil video fps=60. Use GoProFrame for videos extraction with fps=60 (GoProFrame and PupilFrame are in `.mat` files)

Walk2:

- XSense missing
- Videos in `Synced`: GoPro video fps=60, Pupil video fps=60. GoProFrame and PupilFrame both exceed the duration of video, **skip videos **;

Walk3:

- XSense missing
- Videos in `Synced`: GoPro video fps=60, Pupil video fps=60. GoproFrame exceeds the duration of video. Use PupilFrame for videos extraction with fps=**30**

Walk4:

- Videos in `Synced`: GoPro video fps=**30**, Pupil video fps=**30**. Use GoProFrame for videos extraction with fps=**120**

Walk5:

- chestphone data missing
- Videos in `Synced`: GoPro video fps=60, Pupil video fps=60. GoProFrame (fps=60) exceeds the duration of video, PupilFrame (fps=30) doesn't match the labels, **skip videos **

Walk6:

- Videos in `Synced`: GoPro video fps=60, Pupil video fps=60. Both GoProFrame and PupilFrame don't match the labels in synchronized videos. PupilFrame matches with the original video, but the audio and video are not synchronized in original video , **skip videos **

Walk7:

- Videos in `Synced`: GoPro video fps=**30**, Pupil video fps=**30**. Use GoProFrame for videos extraction with fps=60



For video unsynchronized problem:

- Ideally the fps (frame per second) of gopro video, pupil video and GoProFrame in `.mat` should be 60, but some may be different.
- We can try with fps=60 first, and check if the extracted video pieces match with the event label. If not, try with other fps (usually 30 or 120 will work). If still not matches, see if PupilFrame matches. Otherwise skip the videos.