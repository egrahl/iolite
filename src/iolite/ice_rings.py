from timeit import default_timer as timer

import matplotlib.pyplot as plt
import numpy as np
import scipy
import scipy.signal
from scipy.signal import find_peaks
from sklearn import preprocessing

def resolution_peak_list (peaks,resolution_data):
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

    index_list, _ =scipy.signal.find_peaks(intensity_data_sub, prominence=0.1)

    peaks=[]
    for k in range(len(index_list)):
        peaks.append(index_list[k]+resolution_sub_index[0])

    return peaks

def gradient_peak(intensity_data,resolution_data,min,middle,max):
    
    index_min = resolution_data.index(list(filter(lambda i: i > min, resolution_data))[0]) 
    index_middle = resolution_data.index(list(filter(lambda i: i > middle, resolution_data))[0]) 
    index_max = resolution_data.index(list(filter(lambda i: i > max, resolution_data))[0])

    pos_gradient = intensity_data[index_middle]-intensity_data[index_min]
    neg_gradient = intensity_data[index_max]-intensity_data[index_middle]

    return pos_gradient , neg_gradient



def main():

    start = timer()

    #prepare data

    filein=open("table.txt","r")

    resolution_data = []
    intensity_data = []

    for line in filein.readlines():
        tokens = line.split(",")
        resolution_data.append(float(tokens[0]))
        intensity_data.append(float(tokens[1].rstrip()))

    # scale intensity data to 100
    intensity_data_np = np.array(intensity_data)
    intensity_data_reshape = np.reshape(intensity_data_np,(-1,1))

    min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0, 100))
    intensity_data_minmax = min_max_scaler.fit_transform(intensity_data_reshape)
    intensity_data_1D =  intensity_data_minmax.flatten()

    #peak detection
    peaks, peak_dictionary = scipy.signal.find_peaks(intensity_data_1D,height= 5, prominence=0.4, width=7)
    
    resolution_peaks = resolution_peak_list(peaks,resolution_data)

    #print('Resolutions at the peaks:' ,resolution_peaks)


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
            if count[0] == 0:
                pos_gradient, neg_gradient = gradient_peak(intensity_data_1D,resolution_data, 0.065,0.074,0.083)

            if count[1] == 0:
                pos_gradient, neg_gradient = gradient_peak(intensity_data_1D,resolution_data, 0.190,0.198,0.206)

            if count[2] == 0:
                pos_gradient, neg_gradient = gradient_peak(intensity_data_1D,resolution_data, 0.260,0.272,0.280)

            if pos_gradient>0.1 and neg_gradient<0:
                print("The data set contains ice-rings.")
            else:
                print("The data set does not contain ice-rings.")
        else:
            print("The data set does not contain ice-rings.")


    end =timer()

    print('Time taken:', end-start)

    """

    #plot data

    plt.plot(resolution_data, intensity_data_1D)
    plt.ylabel('Mean Intensity (Standardised)')
    plt.xlabel('Resolution')
    plt.title('Mean intensity vs resolution')
    plt.savefig('plot')
    plt.show()
    """

main()