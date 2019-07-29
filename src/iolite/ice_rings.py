from timeit import default_timer as timer

import matplotlib.pyplot as plt
import numpy as np
import scipy
import scipy.signal
from scipy.signal import find_peaks
from sklearn import preprocessing


class IceRingClassifier:
    '''This class takes resolution and intensity data from a .txt file and classifies the dataset whether it does contain ice-rings or not. 
    '''
    def __init__(self, 
                min_1st_ir,max_1st_ir,
                min_2nd_ir,max_2nd_ir,
                min_3rd_ir,max_3rd_ir, 
                filename,showPlot):
        '''The ice ring classifier is initialized with default settings for the resolution limits of the ice rings, 
        the filename to open and the setting not to show a plot.

        :param float min_1st_ir: The minimum resolution at which the first ice-ring can be detected. (default = 0.073)
        :param float max_1st_ir: The maximum resolution at which the first ice-ring can be detected. (default = 0.0755)
        :param float min_2nd_ir: The minimum resolution at which the second ice-ring can be detected. (default = 0.196)
        :param float max_2nd_ir: The maximum resolution at which the second ice-ring can be detected. (default = 0.200)
        :param float min_3rd_ir: The minimum resolution at which the third ice-ring can be detected. (default = 0.269)
        :param float max_3rd_ir: The maximum resolution at which the third ice-ring can be detected.(default = 0.2745)
        :param str filename: name of file that contains the resolution and intensity data (default= "table.txt")
        :param bool showPlot: The boolean that determines if the data should be plotted. (default = False)
        '''

        self.min_1st_ir = min_1st_ir
        self.max_1st_ir = max_1st_ir
        self.min_2nd_ir = min_2nd_ir
        self.max_2nd_ir = max_2nd_ir
        self.min_3rd_ir = min_3rd_ir
        self.max_3rd_ir = max_3rd_ir
        self.inputFile = filename
        self.showPlot = showPlot
    
    def resolution_intensity_from_txt(self):
        '''Create a list of resolution data and intensity data from .txt file, respectively.
        
        #:param str filename: name of txt file the resolution and intensity data lists are created from
        :returns: list of resolution data and list of intensity data
        '''

        filein=open(self.inputFile,"r")

        resolution_data = []
        intensity_data = []

        for line in filein.readlines():
            tokens = line.split(",")
            resolution_data.append(float(tokens[0]))
            intensity_data.append(float(tokens[1].rstrip()))
        filein.close()
        return resolution_data, intensity_data

    def scale_intensity(self,raw_intensity,min,max):
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

    def resolution_peak_list (self,peaks,resolution_data):
        ''' Writes a list of the corresponding resolutions to the found peaks.
        
        :param list peaks: list of indices of the peaks found in the intensity data
        :param list resolution_data: list of resolution data 
        :returns: list of the resolution values corresponding to the peaks
        '''
        resolution_peaks = []

        for i in range(len(peaks)):
            resolution_peaks.append(resolution_data[peaks[i]])
       
        return resolution_peaks

    def ice_ring_plot(self, resolution_data,intensity_data,res_line):
        '''Plots intensity data against resolution with vertical lines at resolution where an ice-ring was found and saves plot to plot.png.

        :param list resolution_data: list of resolution data
        :param numpy array intensity_data: list of intensity data
        :param list res_line: list containing resolutions at which ice-rings were found
        '''
        plt.plot(resolution_data, intensity_data)
        for res in res_line:
            plt.axvline(x=res,color='red')
        plt.ylabel('Mean Intensity')
        plt.xlabel('Resolution')
        plt.title('Mean intensity vs resolution')
        plt.savefig('plot')
        plt.show()


    def main(self):
        '''The main function of ice_rings that classifies the data set. '''
        start = timer()

        #prepare data
        resolution_data, intensity_data = self.resolution_intensity_from_txt()
    
        # scale intensity data to range 0 to 100
        intensity_scaled = self.scale_intensity(intensity_data,0,100)

        #peak detection
        peaks, _ = scipy.signal.find_peaks(intensity_scaled, prominence=0.2, width=4)  #prom=0.4 w=7
        resolution_peaks = self.resolution_peak_list(peaks,resolution_data)
        resolution_peaks_plt =[]

        #detect ice-rings
        count = 0
        for res in resolution_peaks:
            if res>self.min_1st_ir and res<self.max_1st_ir:
                count += 1
                resolution_peaks_plt.append(res)
            if res>self.min_2nd_ir and res<self.max_2nd_ir:
                count += 1
                resolution_peaks_plt.append(res)
            if res>self.min_3rd_ir and res<self.max_3rd_ir:
                count += 1
                resolution_peaks_plt.append(res)

        ice_ring = 0

        #decide if data set contains ice-rings
        if resolution_data[-1]< self.max_2nd_ir:
        #resolution data does not include the resolution greater 0.2
            if count ==1:
                print("The data set contains ice-rings.")
                ice_ring = 1
            else:
                print("The data set does not contain ice-rings.")

        elif resolution_data[-1]< self.max_3rd_ir:
        #resolution data does not include resolution greater 0.2745
            if count ==2:
                print("The data set contains ice-rings.")
                ice_ring = 1
            else:
                print("The data set does not contain ice-rings.")

        else: 
            #resolution data includes resolution greater than 0.2745
            if count == 3:
                print("The data set contains ice-rings.") 
                ice_ring = 1
            else:
                print("The data set does not contain ice-rings.")

        end =timer()

        print('Time taken:', end-start)
        
        #plot data
        if self.showPlot ==True:
            self.ice_ring_plot(resolution_data,intensity_scaled,resolution_peaks_plt)
        
        return ice_ring

def run():
    '''Allows ice_rings to be called from command line.'''
    import argparse
    
    parser = argparse.ArgumentParser(description = 'command line argument')
    parser.add_argument('--min_1st_ir',
                        dest = 'min_1st_ir',
                        type = float,
                        help = 'The minimum resolution at which the first ice-ring can be detected.',
                        default = 0.073)
    parser.add_argument('--max_1st_ir',
                        dest = 'max_1st_ir',
                        type = float,
                        help = 'The maximum resolution at which the first ice-ring can be detected.',
                        default = 0.0755)
    parser.add_argument('--min_2nd_ir',
                        dest = 'min_2nd_ir',
                        type = float,
                        help = 'The minimum resolution at which the second ice-ring can be detected.',
                        default = 0.196)
    parser.add_argument('--max_2nd_ir',
                        dest = 'max_2nd_ir',
                        type = float,
                        help = 'The maximum resolution at which the second ice-ring can be detected.',
                        default = 0.200)
    parser.add_argument('--min_3rd_ir',
                        dest = 'min_3rd_ir',
                        type = float,
                        help = 'The minimum resolution at which the third ice-ring can be detected.',
                        default = 0.269)
    parser.add_argument('--max_3rd_ir',
                        dest = 'max_3rd_ir',
                        type = float,
                        help = 'The maximum resolution at which the third ice-ring can be detected.',
                        default = 0.2745)
    parser.add_argument('--filename',
                        dest = 'filename',
                        type = str,
                        help = 'The name of the file that contains the resolution and intensity data.',
                        default = "table.txt")
    parser.add_argument('--showPlot',
                        dest = 'showPlot',
                        type = bool,
                        help = 'The boolean that determines if the data should be plotted.',
                        default = False)


    args=parser.parse_args()
    ice_ring_classifier = IceRingClassifier(args.min_1st_ir,args.max_1st_ir,
                                            args.min_2nd_ir,args.max_2nd_ir,
                                            args.min_3rd_ir,args.max_3rd_ir,
                                            args.filename,args.showPlot)
    ice_ring_classifier.main()

if __name__ == "__main__":
    run()


