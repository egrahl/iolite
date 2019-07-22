from timeit import default_timer as timer

import matplotlib.pyplot as plt
import numpy as np
import scipy
import scipy.signal
from scipy.signal import find_peaks
from sklearn import preprocessing

class IceRingClassifier:
'''This class takes resolution and intensity data from a .txt file and classifies the dataset wether it does contain ice-rings or not. 

'''
    def __init__(self, 
                min_1st_ir=0.073,max_1st_ir=0.0755,
                min_2nd_ir=0.1990,max_2nd_ir=0.200,
                min_3rd_ir=0.269,max_3rd_ir=0.2745, 
                filename="table.txt",showPlot=False):
    '''The ice ring classifier is initialized with default settings for the resolution limits of the ice rings, the filename to open and 
    the setting not to show a plot.
    '''
        pass
    
    def resolution_intensity_from_txt(filename):
        '''Create a list of resolution data and intensity data from .txt file, respectively.
        
        :param str filename: name of txt file the resolution and intensity data lists are created from
        :returns: list of resolution data and list of intensity data
        '''
        filein=open(filename,"r")

        resolution_data = []
        intensity_data = []

        for line in filein.readlines():
            tokens = line.split(",")
            resolution_data.append(float(tokens[0]))
            intensity_data.append(float(tokens[1].rstrip()))
        filein.close()
        return resolution_data, intensity_data

    def scale_intensity(raw_intensity,min,max):
        ''' Scales the intensity data to the range between min and max.
        
        :param list raw_intensity: list of intensity data that will be scaled
        :param int min: minimum value of the scaled intensity data
        :param int max: maximum value of the scaled intensity data
        :returns: a 1D numpy array containing the scaled intensity data 
        '''
        #reshape array to make it compatible for scaling
        intensity_data_reshape = np.reshape(np.array(raw_intensity),(-1,1))

        min_max_scaler = preprocessing.MinMaxScaler(feature_range=(min, max))
        intensity_data_scaled = min_max_scaler.fit_transform(intensity_data_reshape)

        #transform scaled data back into a 1D array
        intensity_data_1D =  intensity_data_scaled.flatten()

        return intensity_data_1D

    def resolution_peak_list (peaks,resolution_data):
        ''' Writes a list of the corresponding resolutions to the found peaks.
        
        :param list peaks: list of indices of the peaks found in the intensity data
        :param list resolution_data: list of resolution data 
        :returns: list of the resolution values corresponding to the peaks
        '''
        resolution_peaks = []

        for i in range(len(peaks)):
            resolution_peaks.append(resolution_data[peaks[i]])
        return resolution_peaks



    def run():

        start = timer()

        #prepare data
        resolution_data, intensity_data = resolution_intensity_from_txt("table.txt")
    

        # scale intensity data to 100
        intensity_scaled = scale_intensity(intensity_data,0,100)

        #peak detection
        peaks, _ = scipy.signal.find_peaks(intensity_scaled, prominence=0.4, width=7)
        resolution_peaks = resolution_peak_list(peaks,resolution_data)


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
        #first case: resolution data does not include the resolution greater 0.27
            if sum(count) ==2:
                print("The data set contains ice-rings.")
            else:
                print("The data set does not contain ice-rings.")

        else: 
            #resolution data includes resolution greater than 0.27
            if sum(count) == 3:
                print("The data set contains ice-rings.") 
            else:
                print("The data set does not contain ice-rings.")


        end =timer()

        print('Time taken:', end-start)


        """
        #plot data

        plt.plot(resolution_data, intensity_scaled)
        plt.ylabel('Mean Intensity (Standardised)')
        plt.xlabel('Resolution')
        plt.title('Mean intensity vs resolution')
        plt.savefig('plot')
        plt.show()
        """

    main()

