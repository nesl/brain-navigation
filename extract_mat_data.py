import numpy as np
import scipy.io
import ntplib
from datetime import datetime, timezone
import matplotlib.pyplot as plt


mat = scipy.io.loadmat('../RWNApp_Output_Jan2024/RWNApp_RW1_Walk1.mat')
print(mat.keys())

data_np = mat['d_np']
data_xs = mat['d_xs']
time_np = mat['ntp_np']
time_xs = mat['ntp_xs']
time_gopro = mat['ntp_gp']
time_pupil = mat['ntp_pupil']
# print(data_np.shape)
# print(data_xs.shape)
# print(time_np, data_np)
# print(time_xs, data_xs)

save_folder = "../RW1/RW1-Walk1-extracted/"
np.save(save_folder + "data_np", data_np)
np.save(save_folder + "data_xs", data_xs)


def matlab_datenum_to_formatted_string(matlab_datenum):

    # Convert MATLAB datenum to Python datenum by subtracting the MATLAB epoch
    python_datenum = matlab_datenum - 366  # Adjust for MATLAB epoch

    # Convert Python datenum to datetime
    python_datetime = datetime.datetime.fromordinal(int(python_datenum)) + datetime.timedelta(days=python_datenum % 1) - datetime.timedelta(days=366)

    # Format datetime string
    formatted_string = python_datetime.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]

    return formatted_string


# convert matlab NTP time to datetime timestamp
np_formatted_strings = [matlab_datenum_to_formatted_string(md) for md in time_np[:, 0]/60/60/24]
np.save(save_folder + "time_np", np_formatted_strings)

xs_formatted_strings = [matlab_datenum_to_formatted_string(md) for md in time_xs[:, 0]/60/60/24]
np.save(save_folder + "time_xs", xs_formatted_strings)

gopro_formatted_strings = [matlab_datenum_to_formatted_string(md) for md in time_gopro[:, 0]/60/60/24]
np.save(save_folder + "time_gopro", gopro_formatted_strings)

pupil_formatted_strings = [matlab_datenum_to_formatted_string(md) for md in time_pupil[:, 0]/60/60/24]
np.save(save_folder + "time_pupil", pupil_formatted_strings)



