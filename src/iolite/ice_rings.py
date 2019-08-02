from timeit import default_timer as timer

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import scipy
import scipy.signal
from scipy.signal import find_peaks
from sklearn import preprocessing
from math import sqrt
import bisect
import os
import os.path
import sympy
from sympy import limit, Symbol

class IceRingClassifier:
    '''This class takes resolution and intensity data from a .txt file and classifies the dataset whether it does contain ice-rings or not. 
    '''
    def __init__(self,filename,showPlot):
        '''The ice ring classifier is initialized with default settings for the resolution limits of the ice rings, 
        the filename to open and the setting not to show a plot.

       
        :param str filename: name of file that contains the resolution and intensity data (default= "table.txt")
        :param bool showPlot: The boolean that determines if the data should be plotted. (default = False)
        '''

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

    def ice_ring_plot(self, resolution_data,intensity_data,res_line,min_d2,max_d2):
        '''Plots intensity data against resolution with vertical lines at resolution where an ice-ring was found and saves plot to plot.png.

        :param list resolution_data: list of resolution data
        :param numpy array intensity_data: list of intensity data
        :param list res_line: list containing resolutions at which ice-rings were found
        '''
        def format_xticks(x, p):
            if x <= 0:
                return " "
            else:    
                return "%.2f" % sqrt(1/x)
        
        pdb_id= self.get_PDB_id()
        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(FuncFormatter(format_xticks))
        plt.plot(resolution_data, intensity_data)
        
        for min,max in zip(min_d2,max_d2):
            ax.axvspan(min, max, alpha=0.4, color='yellow')
        for res in res_line:
            plt.axvline(x=res,color='red')
        plt.xlim(left=resolution_data[0],right=resolution_data[-1])
        plt.ylabel('Mean Intensity (scaled)')
        plt.xlabel('Resolution')
        plt.title('Mean intensity vs. resolution for '+pdb_id)
        plt.savefig('plot')
        plt.show()

    def read_resolution_ranges(self):
        min_d2 = []
        max_d2 = []
        for line in open("/dls/science/users/gwx73773/iolite/share/hexagonal.txt").readlines():
            a, b = map(float, line.split())
            min_d2.append(a)
            max_d2.append(b)
        return min_d2, max_d2

    def mean_variance(self,intensity_data):
        width = 9
        mean_data=[0]*width
        var_data = [0]*width
        variance_mean_data = [0]*width
        for i in range(width,(len(intensity_data)-width)):
        
            window= np.array(intensity_data[(i-width):(i+width+1)])
            mean= np.mean(window)
            mean_data.append(mean)
            variance = np.var(window)
            var_data.append(variance)
            if mean ==0:
                variance_mean = 0
            else:
                variance_mean= variance/mean
            variance_mean_data.append(variance_mean)
        for n in range(width):
            mean_data.append(0)
            var_data.append(0)
            variance_mean_data.append(0)

        return mean_data, var_data, variance_mean_data

    def compare_mean(self, resolution_data, intensity_data, min_d2, max_d2):
        mean_window_l = []
        mean_neighbours=[]
        ratio=[]
        for min, max in zip(min_d2, max_d2):
            index_min_int=bisect.bisect_right(resolution_data,min)
            index_max_int=bisect.bisect_left(resolution_data,max)
            print(index_min_int, index_max_int)
            window = np.array(intensity_data[index_min_int:(index_max_int+1)])
            print(window)
            mean_window=np.mean(window)
            index = min_d2.index(min)
            
            if index==0:
                index_right=bisect.bisect_left(resolution_data,((min_d2[index+1]+max)/2))
                window_right = np.array(intensity_data[index_max_int:index_right])
                mean_right = np.mean(window_right)
                index_left=bisect.bisect_right(resolution_data,(min-(min_d2[index+1]-max)/2))
                window_left= np.array(intensity_data[index_left:index_min_int])
                mean_left = np.mean(window_left)
            elif index ==(len(min_d2)-1):
                index_left=bisect.bisect_right(resolution_data,((min+max_d2[index-1])/2))
                window_left = np.array(intensity_data[index_left:index_min_int])
                mean_right = np.mean(window_right)
                index_right=bisect.bisect_left(resolution_data,(max+(min-max_d2[index-1])/2))
                window_right= np.array(intensity_data[index_max_int:index_right])
                mean_right = np.mean(window_right)
            else:
                width_left=(min-max_d2[index-1])
                width_right= (min_d2[index+1]-max)
                if width_left<width_right:
                    index_left=bisect.bisect_right(resolution_data,((min+max_d2[index-1])/2))
                    window_left = np.array(intensity_data[index_left:index_min_int])
                    mean_right = np.mean(window_right)
                    index_right=bisect.bisect_left(resolution_data,(max+(min-max_d2[index-1])/2))
                    window_right= np.array(intensity_data[index_max_int:index_right])
                    mean_right = np.mean(window_right)
                else:
                    index_right=bisect.bisect_left(resolution_data,((min_d2[index+1]+max)/2))
                    window_right = np.array(intensity_data[index_max_int:index_right])
                    mean_right = np.mean(window_right)
                    index_left=bisect.bisect_right(resolution_data,(min-(min_d2[index+1]-max)/2))
                    window_left= np.array(intensity_data[index_left:index_min_int])
                    mean_left = np.mean(window_left)
            mean_neighbours.append((mean_left+mean_right)/2)
            ratio.append((2*mean_window)/(mean_left+mean_right))

        return ratio

    def get_PDB_id(self):
        dirpath = os.getcwd()
        foldername = os.path.basename(dirpath)
        return foldername




    def main(self):
        '''The main function of ice_rings that classifies the data set. '''
        start = timer()

        #prepare data
        resolution_data, intensity_data = self.resolution_intensity_from_txt()

       

        # scale intensity data to range 0 to 100
        intensity_scaled = self.scale_intensity(intensity_data,0,100)

        #peak detection
        peaks, peak_dict = scipy.signal.find_peaks(intensity_scaled[:(len(intensity_scaled)-450)],prominence=1.1,rel_height=0.2, width= 1.5)  
        resolution_peaks = self.resolution_peak_list(peaks,resolution_data)
        resolution_peaks_plt =[]
        prominences =[]
        widths=[]

        #print(resolution_peaks)
        

        min_d2, max_d2 = self.read_resolution_ranges()
        #ratio=self.compare_mean(resolution_data,intensity_data,min_d2,max_d2)

        #detect ice-rings
        count = 0
        for res,prom,wid in zip(resolution_peaks,peak_dict['prominences'],peak_dict['widths']):
            for min, max in zip(min_d2, max_d2):
                if res >= min and res <= max:
                    count += 1
                    resolution_peaks_plt.append(res)
    
                    if min_d2.index(a)>1:
                        prominences.append(prom)
                        widths.append(wid)
        if len(prominences)==0:  
            for res,prom,wid in zip(resolution_peaks,peak_dict['prominences'],peak_dict['widths']):
                for min, max in zip(min_d2, max_d2):
                    if res >= min and res <= max:
                        prominences.append(prom)
                        widths.append(wid)
        
                
                            
                
        print("Number of ice-rings found:", count)
        ice_ring = 0

        #decide if data set contains ice-rings
        if count >1:
            ice_ring=1
        
        
       

        #evaluate quality of the ice-rings
        strength=0
        peaked = 0
        average_prom=(sum(prominences)/len(prominences))
        average_width = (sum(widths)/len(widths))

        if  average_prom>7:
            strength=1
            
        if (average_prom/average_width)>0.5:
                peaked=1

        if strength ==0:
            strength_string = 'weak'
        else:
            strength_string = 'strong'

        if peaked ==0:
            peaked_string = 'diffuse'

        else:
            peaked_string = 'sharp'


        if ice_ring ==1:
            print("The dataset contains ",strength_string,",",peaked_string,"ice-rings.")
        else: 
            print("The dataset does not contain ice-rings.")

        end =timer()

        print('Time taken:', end-start)
        
       

        #plot data and save plot
        if self.showPlot ==True:
            self.ice_ring_plot(resolution_data,intensity_scaled,resolution_peaks_plt,min_d2,max_d2)
        
        return ice_ring, count,strength, peaked

def run():
    '''Allows ice_rings to be called from command line.'''
    import argparse
    
    parser = argparse.ArgumentParser(description = 'command line argument')
  
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
    ice_ring_classifier = IceRingClassifier(args.filename,args.showPlot)
    ice_ring_classifier.main()

if __name__ == "__main__":
    run()


