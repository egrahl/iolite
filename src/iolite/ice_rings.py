from timeit import default_timer as timer

import matplotlib.pyplot as plt
import numpy as np
import scipy
import scipy.signal
#from scipy.signal import find_peaks
from sklearn import preprocessing

from dxtbx.model.experiment_list import ExperimentListFactory


filein=open("table.txt","r")

resolution_data = []
intensity_data = []

for line in filein.readlines():
    tokens = line.split(",")
    resolution_data.append(tokens[0])
    intensity_data.append(tokens[1])

intensity_data_np = np.array(intensity_data)
intensity_data_reshape = np.reshape(intensity_data_np,(-1,1))

min_max_scaler = preprocessing.MinMaxScaler()
intensity_data_minmax = min_max_scaler.fit_transform(intensity_data_reshape)


#peaks, properties = scipy.signal.find_peaks(intensity_data,threshold=None, distance=0.01, prominence=1)

#print(peaks)



#plot data
plt.plot(resolution_data,intensity_data_minmax)
#plt.xlim(max(resolution_data),min(resolution_data) )                 #invert the x axis
plt.ylabel('Mean Intensity')
plt.xlabel('Resolution')
plt.title('Mean intensity vs resolution')
plt.savefig('plot')
plt.show()

#print(scipy.__version__)
