from timeit import default_timer as timer

import matplotlib.pyplot as plt
import numpy as np
import scipy
import scipy.signal
from scipy.signal import find_peaks
from sklearn import preprocessing

#from dxtbx.model.experiment_list import ExperimentListFactory


filein=open("table.txt","r")

resolution_data = []
intensity_data = []

for line in filein.readlines():
    tokens = line.split(",")
    resolution_data.append(float(tokens[0]))
    intensity_data.append(float(tokens[1].rstrip()))

resolution_data_np = np.array(resolution_data)
intensity_data_np = np.array(intensity_data)
intensity_data_reshape = np.reshape(intensity_data_np,(-1,1))

min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0, 100))
intensity_data_minmax = min_max_scaler.fit_transform(intensity_data_reshape)
intensity_data_1D =  intensity_data_minmax.flatten()


peaks, _ = scipy.signal.find_peaks(intensity_data_1D,height= 10, prominence=0.8, width=5)
#print(peaks) 
resolution_peaks = []

for i in range(len(peaks)):
    resolution_peaks.append(resolution_data[peaks[i]])

print(resolution_peaks)


#plot data

plt.plot(resolution_data, intensity_data_1D)
plt.ylabel('Mean Intensity')
plt.xlabel('Resolution')
plt.title('Mean intensity vs resolution')
plt.savefig('plot')
plt.show()


