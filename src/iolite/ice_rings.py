import os
import os.path
from math import sqrt
from timeit import default_timer as timer

import matplotlib.pyplot as plt
import numpy as np
import scipy
import scipy.signal
from matplotlib.ticker import FuncFormatter
from scipy.signal import find_peaks
from sklearn import preprocessing


class IceRingClassifier:

    '''
    This class takes resolution and intensity data from a .txt file and 
    classifies the dataset whether it does contain ice-rings or not. 
    '''
    def __init__(self,filename,showPlot):
        '''
        The ice ring classifier is initialized with default settings
        for the filename to open and the setting not to show and save a plot.

        :param str filename: name of file that contains the resolution and 
                             intensity data (default= "table.txt")
        :param bool showPlot: The boolean that determines if the data
                              should be plotted. (default = False)
        '''


        self.inputFile = filename
        self.showPlot = showPlot

    def resolution_intensity_from_txt(self):
        '''
        Create a lists of resolution data and intensity data from .txt file.

        
        :returns: list of resolution data and list of intensity data
        '''

        filein = open(self.inputFile, "r")

        resolution_data = []
        intensity_data = []

        for line in filein.readlines():
            tokens = line.split(",")
            resolution_data.append(float(tokens[0]))
            intensity_data.append(float(tokens[1].rstrip()))
        filein.close()

        return resolution_data, intensity_data

    def scale_intensity(self, raw_intensity, min, max):
        """ Scales the intensity data to the range between min and max.
        
        :param list raw_intensity: list of intensity data that will be scaled
        :param int min: minimum value of the scaled intensity data
        :param int max: maximum value of the scaled intensity data

        :returns: a 1D numpy array containing the scaled intensity data 
        """
        # reshape array to make it compatible for scaling
        intensity_data_reshape = np.reshape(np.array(raw_intensity), (-1, 1))

        min_max_scaler = preprocessing.MinMaxScaler(feature_range=(min, max))
        intensity_data_scaled = min_max_scaler.fit_transform(intensity_data_reshape)

        # transform scaled data back into a 1D array
        intensity_data_1D = intensity_data_scaled.flatten()

        return intensity_data_1D

    def resolution_peak_list(self, peaks, resolution_data):
        """ Writes a list of the corresponding resolutions to the found peaks.
        
        :param list peaks: list of indices of the peaks found in the intensity data
        :param list resolution_data: list of resolution data 
        :returns: list of the resolution values corresponding to the peaks
        """
        resolution_peaks = []

        for i in range(len(peaks)):
            resolution_peaks.append(resolution_data[peaks[i]])

        return resolution_peaks


    def ice_ring_plot(self, resolution_data,intensity_data,res_line,min_d2,max_d2):
        '''
        Plots intensity data against resolution with vertical lines at resolution
        where an ice-ring was found and marked ranges where peaks corresponding 
        to ice-rings can be detected, and saves plot to plot.png.

        :param list resolution_data: list of resolution data
        :param numpy array intensity_data: list of intensity data
        :param list res_line: list containing resolutions at which 
                              ice-rings were found
        :param list min_d2: list containing the minimum resolutions 
                            of the ranges where ice-rings can be detected
        :param list max_d2: list containing the maximum resolutions
                            of the ranges where ice-rings can be detected
        '''

        def format_xticks(x, p):
            """Changes x axis to resolution in angstroms."""
            if x <= 0:
                return " "

            else:    
                return "%.2f" % sqrt(1/x)
        
        pdb_id= self.get_pdb_id()

        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(FuncFormatter(format_xticks))
        plt.plot(resolution_data, intensity_data)

        # plot resolution ranges for ice-rings
        for min, max in zip(min_d2, max_d2):
            ax.axvspan(min, max, alpha=0.4, color="yellow")
        # plot vertical lines where ice-rings were detected
        for res in res_line:
            plt.axvline(x=res, color="red")

        plt.xlim(left=resolution_data[0], right=resolution_data[-1])
        plt.ylabel("Mean Intensity (scaled)")
        plt.xlabel("Resolution")
        plt.title("Mean intensity vs. resolution for " + pdb_id)
        plt.savefig("plot")
        plt.show()

    def read_resolution_ranges(self):
        '''
        Reads resolution ranges where ice-rings can be detected from text file 
        and creates lists containing the minima and maxima of these ranges.

        :returns: lists of minima and maxima of resolution ranges
        '''

        min_d2 = []
        max_d2 = []
        for line in open(
            "/dls/science/users/gwx73773/iolite/share/hexagonal.txt"
        ).readlines():
            a, b = map(float, line.split())
            min_d2.append(a)
            max_d2.append(b)
        return min_d2, max_d2



    def get_pdb_id(self):
        '''Reads PDB id of current dataset.


        :returns: PDB id
        """
        dirpath = os.getcwd()
        foldername = os.path.basename(dirpath)
        return foldername

    def main(self):
        """The main function of ice_rings that classifies the data set. 
        
        :returns: boolean ice_ring, count (number of ice-rings detected), 
                booleans strength of ice rings, peaked 
        '''

        start = timer()

        # prepare data
        resolution_data, intensity_data = self.resolution_intensity_from_txt()


        # scale intensity data to range 0 to 100 to make peak finding work
        intensity_scaled = self.scale_intensity(intensity_data,0,100)

        
        #detect the peaks in intensity

        #last values of intensity list is ignored because of high noise
        #other values have been determined to give best results
        peaks, peak_dict = scipy.signal.find_peaks(intensity_scaled[:(len(intensity_scaled)-450)],prominence=1.1,rel_height=0.2, width= 1.5)  
        resolution_peaks = self.resolution_peak_list(peaks,resolution_data)
        
        #create lists that will hold important data
        resolution_peaks_plt =[]
        prominences =[]
        widths=[]

        min_d2, max_d2 = self.read_resolution_ranges()

        # detect ice-rings and qualitites of peaks
        count_ir = 0
        count_round = 0
        first_prom = []
        for res, prom, wid in zip(
            resolution_peaks, peak_dict["prominences"], peak_dict["widths"]
        ):
            for minimum, maximum in zip(min_d2, max_d2):

                count_round +=1

                #detect ice-ring peak if it is in a resolution range where 
                #ice-rings are expected

                if res >= minimum and res <= maximum:
                    count_ir += 1
                    resolution_peaks_plt.append(res)
                    prominences.append(prom)
                    widths.append(wid)


                   """  track if there are peaks in any of the first 3 resolution ranges
                    (peak finding algorithm had difficulties with choosing the right 
                    prominences) """
                    if count_round<4:

                        first_prom.append(prom)
            count_round = 0

                 
        #decide if data set contains ice-rings
        ice_ring = (count_ir >1)
     
        
        #evaluate quality of the ice-rings

        if len(first_prom)>0:
            """the peak with the largest prominence detected in the first 3 
            resolution ranges will be excluded from the calculation of the
            averages, as its determined prominence is not actually the 
            prominence of the ice-ring peak (the background has typically a
            higher intensity in that region, which can be interpreted as a
             peak by the peak finding algorithm)"""

            max_prom=max(first_prom)
            if len(prominences)>1:
                average_prom=((sum(prominences)-max_prom)/(len(prominences)-1))
                average_width = ((sum(widths)-widths[prominences.index(max_prom)])/(len(widths)-1))
        else:
            if len(prominences)>0:
                average_prom=(sum(prominences)/len(prominences))
                average_width = (sum(widths)/len(widths))
        
        #values come from analysing previous data
        strength= (average_prom>5)
        peaked = ((average_prom/average_width)>0.5)

        if strength ==False:
            strength_string = 'weak'

        else:
            strength_string = "strong"

        if peaked ==False:
            peaked_string = 'diffuse'

        else:
            peaked_string = "sharp"

        # print output
        print("Number of ice-rings found:", count_ir)
        if ice_ring == 1:
            print(
                "The dataset contains ",
                strength_string,
                ",",
                peaked_string,
                "ice-rings.",
            )
        else:
            print("The dataset does not contain ice-rings.")

            strength=False
            peaked=False


        end = timer()

        print("Time taken:", end - start)

        # plot data and save plot
        if self.showPlot == True:
            self.ice_ring_plot(
                resolution_data, intensity_scaled, resolution_peaks_plt, min_d2, max_d2
            )

        return ice_ring, count_ir, strength, peaked



def run():
    """Allows ice_rings to be called from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="command line argument")

    parser.add_argument(
        "--filename",
        dest="filename",
        type=str,
        help="The name of the file that contains the resolution and intensity data.",
        default="table.txt",
    )
    parser.add_argument(
        "--showPlot",
        dest="showPlot",
        type=bool,
        help="The boolean that determines if the data should be plotted.",
        default=False,
    )

    args = parser.parse_args()
    ice_ring_classifier = IceRingClassifier(args.filename, args.showPlot)
    ice_ring_classifier.main()


if __name__ == "__main__":
    run()
