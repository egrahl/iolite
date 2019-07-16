from timeit import default_timer as timer

import matplotlib.pyplot as plt
import numpy as np
import scipy
import scipy.signal
from scipy.signal import find_peaks
from sklearn import preprocessing

def resolution_peak_list (peaks):
    resolution_peaks = []

    for i in range(len(peaks)):
        resolution_peaks.append(resolution_data[peaks[i]])
    return resolution_peaks



def additional_peaks(intensity_data,resolution_data,min,max):
    resolution_sub_index =[]
    for i in range(len(resolution_data)):
        if min<resolution_data[i] and max>resolution_data[i]:
            resolution_sub_index.append(i)
        

    intensity_data_sub = []
    for n in range(len(resolution_sub_index)):
        intensity_data_sub.append(intensity_data[resolution_sub_index[n]])

    index_list, _ =scipy.signal.find_peaks(intensity_data_sub)

    
    
    peaks=[]
    for k in range(len(index_list)):
        peaks.append(index_list[k]+resolution_sub_index[0])

    return peaks



#prepare data

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

#peak detection
peaks, peak_dictionary = scipy.signal.find_peaks(intensity_data_1D,height= 5, prominence=0.4, width=7)
 
resolution_peaks = resolution_peak_list(peaks)

print('Resolutions at the peaks:' ,resolution_peaks)
#print(peak_dictionary)

peaks2 =additional_peaks(intensity_data_1D, resolution_data,0.25,0.28)
resolution_peaks2 = resolution_peak_list(peaks2)

print('The additional peaks:' , resolution_peaks2)

#detect ice-rings

count = [0]*3


for i in range(len(resolution_peaks)):
    if resolution_peaks[i]>0.073 and resolution_peaks[i]<0.0755:
        count[0] = 1
    if resolution_peaks[i]>0.190 and resolution_peaks[i]<0.200:
        count[1] = 1
    if resolution_peaks[i]>0.269 and resolution_peaks[i]<0.2745:
        count[2] = 1


if resolution_data[-1]< 0.27:
#first case: resolution data does not include the resolution around 0.272
    if sum(count) ==2:
        print("The data set contains ice-rings.")

    else:
        print("The data set does not contain ice-rings.")

else: 
    #resolution data includes resolution around 0.272
    if sum(count) == 3:
        print("The data set contains ice-rings.")

    elif sum(count) ==2:
        pass
        #write something here
    else:
        print("The data set does not contain ice-rings.")






#plot data

plt.plot(resolution_data, intensity_data_1D)
plt.ylabel('Mean Intensity (Standardised)')
plt.xlabel('Resolution')
plt.title('Mean intensity vs resolution')
plt.savefig('plot')
plt.show()
