import itertools
from timeit import default_timer as timer

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pylab

from dials.array_family import flex
from dxtbx.model.experiment_list import ExperimentListFactory


class OverlapCounter:
''' A class that counts the overlaps of shoeboxes of spots on imagesets.'''

    def __init__(self,filename):
         '''
        The overlap counter is initialized with default settings
        for the filename to open.

        :param str filename: name of json file that contains the reflection 
                             table (default= "13_integrated_experiments.json")
        '''
        self.inputfile=filename

    def np_resolution(self,x_dim,y_dim,panel,beam):
        '''
        This function writes a 2D numpy array of the resolutions (1/d^2) 
        corresponding to the pixels on the image.

        :param int x_dim: width of the image and resolution numpy array
        :param int y_dim: length of the image and resolution numpy array
        :param   panel:
        :param   beam:

        :returns: 2D numpy array containing the resolutions (1/d^2)
        '''
        resolution=np.zeros((y_dim,x_dim))
        for y in range(y_dim):
            for x in range(x_dim):
                d = panel.get_resolution_at_pixel(beam.get_s0(), (x,y))
                resolution[y,x]=(1/d**2)

        return resolution

    def np_prepare_bins(self,vmax, vmin, num_bins,resolution):
        '''This function sets bins with resolution ranges and a list of indices 
        of the bin in the resolution bin list to enable referring back from a 
        pixel to the right resolution bin. Additionally it tracks how many pixels 
        go into each bin.

        :param float vmax: maximum 1/d^2 value of image
        :param float vmin: minimum 1/d^2 value of image
        :param int num_bins: number of resolution bins
        :param numpy array resolution: 2D numpy array containing the 1/d^2 values
                                    for each pixel
        
        :returns: list of average value of resolution bins, 1D numpy array of 
                indices in the resolution bin list, list of weight of bins
        '''
        d2_list=[]
        weight=[0]*num_bins
        resolution_1d=resolution.reshape(-1)
        index_list=[]
        
        intervall=(vmax-vmin)/(num_bins)
        
        for i in range(num_bins):
            d2=vmin+((2*i+1)/2)*intervall
            d2_list.append(d2)
        for d2 in resolution_1d:
            if d2==vmin:
                index=0
            elif d2==vmax:
                index=num_bins-1
            else:
                index=int((d2-vmin-intervall/2)/intervall)
            index_list.append(index)
            
            weight[index]+=1
        index_array=np.array(index_list)
        
    
        return d2_list, index_array, weight
        


    def write_bg_and_fg_mask(self,reflections,shoebox,y_dim,x_dim,z):
        '''This function writes masks (one for forground, one for background)
        of the shape of the image that contain the counts of shoeboxes that 
        have a foreground/background at the specific pixels.

        :param dials_array_family_flex_ext.reflection_table reflections: reflection table
        :param list shoeboxes: list that contains all shoeboxes on the image
        :param int y_dim: height of the image
        :param int x_dim: width of the image
        :param int z: index of image in dataset

        :returns: masks of counts of background and foreground pixels in shoeboxes 
        
        '''
        # Get the bounding box overlaps
        bbox_overlaps = reflections.find_overlaps()

        #create empty masks with the shape of the image    
        n_background = np.zeros(dtype=int, shape=(y_dim,x_dim))
        n_foreground = np.zeros(dtype=int, shape=(y_dim,x_dim))

        for edge in bbox_overlaps.edges():
            #get indices of overlapping shoeboxes in the shoebox list
            index1 = bbox_overlaps.source(edge)
            index2 = bbox_overlaps.target(edge)

            bbox1 = shoebox[index1].bbox
            bbox2 = shoebox[index2].bbox
            mask1 = shoebox[index1].mask.as_numpy_array()
            mask2 = shoebox[index2].mask.as_numpy_array()
            
            shoebox_mask=[mask1,mask2]
            shoebox_bbox=[bbox1,bbox2]
            indices=[index1,index2]

            #calculate coordinates of overlap
            x0 = max(bbox1[0], bbox2[0],0)        
            x1 = min(bbox1[1], bbox2[1],x_dim)        
            y0 = max(bbox1[2], bbox2[2],0)        
            y1 = min(bbox1[3], bbox2[3],y_dim)  
                    
            assert x1 > x0
            assert y1 > y0

            #add background and foreground information of shoeboxes to overall masks
            for mask,bbox,index in zip(shoebox_mask,shoebox_bbox,indices):
                x0m,x1m,y0m,y1m,z0m,_=bbox 
                sub_mask=mask[(z-z0m),(y0-y0m):(y1-y0m),(x0-x0m):(x1-x0m)]
                n_background[y0:y1,x0:x1] += ((sub_mask & 3) == 3)
                n_foreground[y0:y1,x0:x1] += ((sub_mask & 5) == 5)

                #set submask values to zero to avoid counting shoeboxes double
                sub_mask[sub_mask==3]=0
                sub_mask[sub_mask==5]=0
                shoebox[index].mask=flex.int(mask)

        return n_background,n_foreground

    def plot_bar_chart(self,d2_list, ratio):
        plt.bar(d2_list,ratio)
        plt.show()


    def main():
        
        start_main=timer()

        #get input from json file
        experiments = ExperimentListFactory.from_json_file(self.inputfile)
        assert len(experiments) == 1
        imageset = experiments[0].imageset
        beam = experiments[0].beam
        detector = experiments[0].detector  
        panel = detector[0]

        # get dimensions of the dataset
        y_dim = imageset.get_raw_data(0)[0].all()[0]
        x_dim = imageset.get_raw_data(0)[0].all()[1]
        z_dim = len(imageset)
        
        #write resolution array
        resolution= self.np_resolution(x_dim,y_dim,panel,beam)      
        print("Read in resolutions.")    

        #get vmin, vmx and number of bins
        vmin=np.amin(resolution)
        vmax=np.amax(resolution)
        num_bins=50
        
        #get bin labels(middle of resolution range) array with size of image with 
        #indices of bin the resolution is in and weight of each bin
        d2_list, index_array, weight = self.np_prepare_bins(vmax,vmin,num_bins,resolution)
        print("Prepared bins.")

        count_bg=[0]*num_bins
        count_fg=[0]*num_bins
        count_bg_fg=[0]*num_bins
        count_total=[0]*num_bins

        for z in range(z_dim):    
            start=timer()
            filename= "shoeboxes_"+str(z)+".pickle"
        
            #get shoeboxes from pickle file
            reflections = flex.reflection_table.from_pickle(filename)
            shoebox = reflections["shoebox"]

            #write masks of background of shoeboxes and foreground of shoeboxes
            n_background, n_foreground=self.write_bg_and_fg_mask(reflections,shoebox,y_dim,x_dim,z)
            
            #prepare lists that will contain count of different kinds of overlap
            #per resolution bin for the current image
            count_bg_im=[0]*len(d2_list)
            count_fg_im=[0]*len(d2_list)
            count_bg_fg_im=[0]*len(d2_list)

            #fill lists of overlap counts
            for bg,fg,index in itertools.izip(n_background.reshape(-1),n_foreground.reshape(-1),index_array):
                count_bg_im[index]+=(bg*(bg-1)/2)
                count_fg_im[index]+=(fg*(fg-1)/2)
                count_bg_fg_im[index]+=bg*fg

            bg_ratio_im=[]
            fg_ratio_im=[]
            bg_fg_ratio_im= []
            total_ratio_im=[]
            bin=0

            #calculate ratios of overlaps (no. of overlaps in bin/no. of pixels in bin)
            #add count of overlaps of image to overall counts
            for b,f,bf,w in zip(count_bg_im,count_fg_im,count_bg_fg_im,weight):
                bg_ratio_im.append(b/w)
                fg_ratio_im.append(f/w) 
                bg_fg_ratio_im.append(bf/w)
                total_ratio_im.append(b/w+f/w+bf/w)
                count_fg[bin]+= f
                count_bg[bin]+= b
                count_bg_fg[bin]+= bf
                count_total[bin]+= (b+f+bf)
                bin +=1
            
        
            #print output
            print("Image no.:",z)
            print("No. of shoeboxes:", len(shoebox))
            print("total overlap ratio", (sum(count_bg_im)+sum(count_fg_im)+sum(count_bg_fg_im))/sum(weight))
            print("foreground overlap ratio",   sum(count_fg_im)/sum(weight))
            print("background overlap ratio",  sum(count_bg_im)/sum(weight))
            print("background foreground overlap ratio",   sum(count_bg_fg_im)/sum(weight))

            end=timer()
            #plot_bar_chart(d2_list,fg_ratio_im)
            print("Time taken for image:",end-start)  
        
        #ratio of overlaps per resolution bin
        ratio_total=[]
        ratio_bg=[]
        ratio_fg=[]
        ratio_bg_fg=[]

        for t,b,f,bf in zip(count_total,count_bg,count_fg,count_bg_fg):      
            ratio_total.append(t/(w*z_dim))
            ratio_bg.append(b/(w*z_dim))
            ratio_fg.append(f/(w*z_dim))
            ratio_bg_fg.append(bf/(w*z_dim))

        #calculate the average overlap ratios for the dataset
        ratio_total_dataset=(sum(count_bg)+sum(count_fg)+sum(count_bg_fg))/(sum(weight)*z_dim)
        ratio_fg_dataset=sum(count_fg)/(sum(weight)*z_dim)
        ratio_bg_dataset= sum(count_bg)/(sum(weight)*z_dim)
        ratio_bg_fg_dataset=sum(count_bg_fg)/(sum(weight)*z_dim)

        end_main=timer()

        #print output
        print("Overlap statistics for whole dataset:")    
        print("total overlap ratio", ratio_total_dataset)
        print("foreground overlap ratio", ratio_fg_dataset)
        print("background overlap ratio", ratio_bg_dataset)
        print("background foreground overlap ratio", ratio_bg_fg_dataset)

        print("Time taken for dataset:", end_main-start_main)   

def run():
    """Allows overlapping_spots to be called from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="command line argument")

    parser.add_argument(
        "--filename",
        dest="filename",
        type=str,
        help="The name of the json file that contains the reflection table.",
        default="13_integrated_experiments.json",
    )

    args = parser.parse_args()
    overlap_counter = OverlapCounter(args.filename)
    overlap_counter.main()


if __name__ == "__main__":
    run()
