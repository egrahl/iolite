import itertools
from timeit import default_timer as timer

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pylab

from dials.array_family import flex
from dxtbx.model.experiment_list import ExperimentListFactory


class OverlapCounter:
    ''' A class that counts the overlaps of shoeboxes of spots on imagesets. 
        The overlaps can be counted either per pixel or per shoebox.'''

    def __init__(self,inputfile,num_bins,outputfile_l,outputfile_t,run_shoeboxes):
        '''
        The overlap counter is initialized with default settings
        for the filename to open, the number of resolution bins 
        the name of the output file containing the overlaps per resolution,
        the name of the outputfile containing the overlaps per dataset 
        and the boolean that dicides whether the overlaps should be counted per 
        shoebox. 

        :param str inputfile: name of json file that contains the reflection 
                             table (default= "13_integrated_experiments.json")
        :param int num_bins: number of resolution bins (default:50)
        :param str outputfile_l: name of outputfile written containing overlaps 
                                per resolution bin (default: overlap_lists)
        :param str outputfile_t: name of outputfile written containing average 
                                overlaps (default: overlap_total)
        :param bool run_shoeboxes: The boolean which decides whether overlaps
                                   per shoebox should be run. If set to False,
                                   overlaps per pixel will be run. (default:True)
        '''
        self.inputfile=inputfile
        self.num_bins=num_bins
        self.outputfile_l=outputfile_l
        self.outputfile_t=outputfile_t
        self.run_shoeboxes=run_shoeboxes

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

    def prepare_bins_shoebox(self,vmax, vmin, num_bins):
        '''
        This function prepares resolution bins for counting overlaps
        per shoebox.

        :param float vmax: maximum resolution in 1/d^2
        :param float vmin: minimum resolution in 1/d^2
        :param int num_bins: number of resolution bins

        :returns: list of average resolution of resolution bins 
                  and resolution intervall of resolution bins


        '''
        
        d2_list=[]
        intervall=(vmax-vmin)/(num_bins)
        for i in range(num_bins):
            d2=vmin+((2*i+1)/2)*intervall
            d2_list.append(d2)

        return d2_list,intervall

    def assign_shoebox_to_resolution_bin(self,d2_shoebox,vmin,vmax,intervall):
        '''
        This function assigns a shoebox to a resolution bin by writing an index
        array, which contains the indices of the resolution bin in the resolution 
        bin list the shoebox belongs to. Additionally, the weight of each resolution
        bin is recorded.

        :param list d2_shoebox: list of resolutions in 1/d^2 of each shoebox
        :param float vmax: maximum resolution in 1/d^2
        :param float vmin: minimum resolution in 1/d^2
        :param float intervall: resolution intervall of the resolution bins
        '''
        
        index_list=[]
        weight=[0]*self.num_bins
        num_bins=self.num_bins
        for d2 in d2_shoebox:
            if d2==vmin:
                index=0
            elif d2>=vmax:
                index=num_bins-1
            else:
                index=int((d2-vmin-intervall/2)/intervall)
            index_list.append(index)
            
            weight[index]+=1
        
        index_array=np.array(index_list)
        
        return index_array, weight

    def prepare_bins_pixel(self,vmax, vmin, num_bins,resolution):
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

            #avoid counting overlaps twice
            if index1>index2:
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

    def write_overlaps_per_shoebox(self,reflections,shoebox,y_dim,x_dim,z):
        '''
        This function counts shoebox overlaps (background/background,
        foreground/foreground, foreground/background, background/foreground)
        for each shoebox.

        :param reflections: the reflection table
        :param list shoebox: the list containing the shoeboxes on one image
        :param int y_dim: the height of the image
        :param int x_dim: the width of the image
        :param int z: the index of the current image

        :returns: lists of the fg/fg,fg/bg,bg/fg and bg/bg overlaps per shoebox

        '''
        # Get the bounding box overlaps
        bbox_overlaps = reflections.find_overlaps()

        #create empty masks with the shape of the image    
        n_background = np.zeros(dtype=int, shape=(y_dim,x_dim))
        n_foreground = np.zeros(dtype=int, shape=(y_dim,x_dim))
            
        no_shoeboxes=len(shoebox)
        fg_fg=[0]*no_shoeboxes
        fg_bg=[0]*no_shoeboxes
        bg_fg=[0]*no_shoeboxes
        bg_bg=[0]*no_shoeboxes

        #loop through the overlaps
        for edge in bbox_overlaps.edges():
            #get indices of overlapping shoeboxes in the shoebox list
            index1 = bbox_overlaps.source(edge)
            index2 = bbox_overlaps.target(edge)

            #avoid counting overlaps twice
            if index1>index2:
                bbox1 = shoebox[index1].bbox
                bbox2 = shoebox[index2].bbox
                mask1 = shoebox[index1].mask.as_numpy_array()
                mask2 = shoebox[index2].mask.as_numpy_array()
                
                #calculate coordinates of overlap
                x0 = max(bbox1[0], bbox2[0],0)        
                x1 = min(bbox1[1], bbox2[1],x_dim)        
                y0 = max(bbox1[2], bbox2[2],0)        
                y1 = min(bbox1[3], bbox2[3],y_dim)  
                        
                assert x1 > x0
                assert y1 > y0
            
                

                x01,x11,y01,y11,z01,_=bbox1
                x02,x12,y02,y12,z02,_=bbox2
                
                #get submasks of both shoeboxes for the overlapping area
                sub_mask1=mask1[(z-z01),(y0-y01):(y1-y01),(x0-x01):(x1-x01)]
                sub_mask2=mask2[(z-z02),(y0-y02):(y1-y02),(x0-x02):(x1-x02)]

                #create background and foreground masks for both shoeboxes
                array1_fg=np.zeros(sub_mask1.shape,dtype=int)
                array1_bg=np.zeros(sub_mask1.shape,dtype=int)
                array2_fg=np.zeros(sub_mask2.shape,dtype=int)
                array2_bg=np.zeros(sub_mask2.shape,dtype=int)

                #detect foreground and background pixels on submasks 
                array1_fg+=((sub_mask1&5)==5)
                array2_fg+=((sub_mask2&5)==5)
                array1_bg+=((sub_mask1&3)==3)
                array2_bg+=((sub_mask2&3)==3)

                #count overlaps
                fg_fg[index1]+=np.any(np.logical_and(array1_fg,array2_fg))
                fg_fg[index2]+=np.any(np.logical_and(array1_fg,array2_fg))

                bg_bg[index1]+=np.any(np.logical_and(array1_bg,array2_bg))
                bg_bg[index2]+=np.any(np.logical_and(array1_bg,array2_bg))

                fg_bg[index1]+=np.any(np.logical_and(array1_fg,array2_bg))
                fg_bg[index2]+=np.any(np.logical_and(array1_bg,array2_fg))

                bg_fg[index1]+=np.any(np.logical_and(array1_bg,array2_fg))
                bg_fg[index2]+=np.any(np.logical_and(array1_fg,array2_bg))

    
        return fg_fg,fg_bg,bg_fg,bg_bg

    def write_output_lists_pixel(self,res,total,bg,fg,bg_fg):
        '''This function writes a text file containing the lists of the 
        average resolution of the bins and the overlaps per pixel per bin.

        :param list res: list with resolution per bin
        :param list total: list of total overlaps per bin
        :param list bg: list of background overlaps per bin
        :param list fg: list of foreground overlaps per bin
        :param list bg_fg: list of background foreground overlaps per bin
        '''
        name_outfile=self.outputfile_l+"_pixel.txt"
        with open(name_outfile, "w") as outfile:
            for r, t,f,b,bf in zip(res, total,fg,bg,bg_fg):
                outfile.write("%f, %f, %f, %f, %f\n" % (r, t, f, b, bf))

    def write_output_total_pixel(self,ratio_total,ratio_bg,ratio_fg,ratio_bg_fg):
        '''This function writes a text file containing the average 
           overlaps per pixel of the dataset.

        :param float ratio_total: average total overlap ratio 
        :param float ratio_bg: average background overlap ratio
        :param float ratio_fg: average foreground overlap ratio
        :param float ratio_bg_fg: average background foreground overlap ratio
        '''

        text=["total overlap ratio:","foreground overlap ratio:",
         "background overlap ratio:","background foreground overlap ratio:"]
        data=[ratio_total,ratio_fg,ratio_bg,ratio_bg_fg]
        name_outfile=self.outputfile_t+"_pixel.txt"
        with open(name_outfile,"w") as outfile:
            for t,d in zip(text,data):
                outfile.write("%s, %f\n" %(t,d))
    
    def write_output_lists_shoebox(self,res,total_f,total_b,bg,fg,bg_fg,fg_bg):
        '''This function writes a text file containing the lists of the 
        average resolution of the bins and the overlaps per shoebox per bin.

        :param list res: list with resolution per bin
        :param list total: list of total overlaps per bin
        :param list bg: list of background overlaps per bin
        :param list fg: list of foreground overlaps per bin
        :param list bg_fg: list of background foreground overlaps per bin
        '''
        name_outfile=self.outputfile_l+"_shoebox.txt"
        with open(name_outfile, "w") as outfile:
            for r, tf,tb,f,b,fb,bf in zip(res, total_f,total_b,fg,bg,fg_bg,bg_fg):
                outfile.write("%f, %f, %f, %f, %f, %f, %f\n" % (r, tf, tb, f, b, fb, bf))

    def write_output_total_shoebox(self,ratio_total,ratio_bg,ratio_fg,ratio_bg_fg):
        '''This function writes a text file containing the average overlaps
        per shoebox of the dataset.

        :param float ratio_total: average total overlap ratio 
        :param float ratio_bg: average background overlap ratio
        :param float ratio_fg: average foreground overlap ratio
        :param float ratio_bg_fg: average background foreground overlap ratio
        '''

        text=["total overlap ratio:","foreground overlap ratio:",
         "background overlap ratio:","background foreground overlap ratio:"]
        data=[ratio_total,ratio_fg,ratio_bg,ratio_bg_fg]
        name_outfile=self.outputfile_t+"_shoebox.txt"
        with open(name_outfile,"w") as outfile:
            for t,d in zip(text,data):
                outfile.write("%s, %f\n" %(t,d))

    def prepare_data(self):
        '''
        This function extracts dimensions of the imageset the resolutions
        per pixel and the minimum and maximum resolution of the imagesets from 
        the input file.

        :returns: number of images, width and height of the images, minimum and maximum 
        resolutions and a resolution list per pixel

        '''
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
        
        print("Number of images in dataset:", z_dim)

        #write resolution array
        resolution= self.np_resolution(x_dim,y_dim,panel,beam)      
        print("Read in resolutions.")    

        #get vmin, vmx and number of bins
        vmin=np.amin(resolution)
        vmax=np.amax(resolution)
        

        return z_dim,y_dim, x_dim,vmin,vmax,resolution

    def count_overlaps_per_reflection(self):
        '''
        The function that counts overlaps per reflection.

        :returns:total overlpas ratio per shoebox, foreground overlsp
        ratio per shoebox, background overlap ratio per shoebox,
        background/foredround overlap per shoebox
        '''
        start_main=timer()
        #get dimensions of imageset and resolution values
        z_dim,y_dim, x_dim,vmin,vmax,resolution=self.prepare_data()
        
        #prepare the bins
        num_bins=self.num_bins
        d2_list,intervall=self.prepare_bins_shoebox(vmax,vmin,num_bins)

        #prepare the lists containing the overall overlap counts and ratios
        ratio_fg_fg=[0]*num_bins
        ratio_fg_bg=[0]*num_bins
        ratio_bg_fg=[0]*num_bins
        ratio_bg_bg=[0]*num_bins
        ratio_total_f=[0]*num_bins
        ratio_total_b=[0]*num_bins
        sum_fg_fg=[0]*num_bins
        sum_fg_bg=[0]*num_bins
        sum_bg_fg=[0]*num_bins
        sum_bg_bg=[0]*num_bins
        sum_total_f=[0]*num_bins
        sum_total_b=[0]*num_bins

        #loop through all images 
        for z in range(z_dim):    
            start=timer()
           
            filename= "shoeboxes_"+str(z)+".pickle"
        
            #get shoeboxes and resolutions from pickle file
            reflections = flex.reflection_table.from_pickle(filename)
            resolution=reflections["d"].as_numpy_array()
            
            d2_shoebox=np.array(map(lambda d: 1/(d**2),resolution))
            
            shoebox = reflections["shoebox"]
            no_shoeboxes=len(shoebox)

            #assign shoeboxes to resolution bins
            index_array, weight=self.assign_shoebox_to_resolution_bin(d2_shoebox,vmin,vmax,intervall)

            #count overlpas for each shoebox
            fg_fg,fg_bg,bg_fg,bg_bg=self.write_overlaps_per_shoebox(reflections,shoebox,y_dim,x_dim,z)

            #prepare lists containg overlap counts and ratio per image  
            ratio_fg_fg_im=[0]*num_bins
            ratio_fg_bg_im=[0]*num_bins
            ratio_bg_fg_im=[0]*num_bins
            ratio_bg_bg_im=[0]*num_bins
            ratio_total_f_im=[0]*num_bins
            ratio_total_b_im=[0]*num_bins
            sum_fg_fg_im=[0]*num_bins
            sum_fg_bg_im=[0]*num_bins
            sum_bg_fg_im=[0]*num_bins
            sum_bg_bg_im=[0]*num_bins
            sum_total_f_im=[0]*num_bins
            sum_total_b_im=[0]*num_bins
            
            #add counts to resolution bins
            for f,fb,bf,b,i in zip(fg_fg,fg_bg,bg_fg,bg_bg,index_array):
                if weight[i]>0:
                    ratio_fg_fg_im[i]+=f/weight[i]
                    ratio_fg_bg_im[i]+=fb/weight[i]
                    ratio_bg_fg_im[i]+=bf/weight[i]
                    ratio_bg_bg_im[i]+=b/weight[i]
                    ratio_total_f_im[i]+=(f+fb+b)/weight[i]
                    ratio_total_b_im[i]+=(f+bf+b)/weight[i]
                    sum_fg_fg_im[i]+=f
                    sum_fg_bg_im[i]+=fb
                    sum_bg_fg_im[i]+=bf
                    sum_bg_bg_im[i]+=b
                    sum_total_f_im[i]+=(f+fb+b)
                    sum_total_b_im[i]+=(f+bf+b)
                    ratio_fg_fg[i]+=f/(weight[i]*z_dim)
                    ratio_fg_bg[i]+=fb/(weight[i]*z_dim)
                    ratio_bg_fg[i]+=bf/(weight[i]*z_dim)
                    ratio_bg_bg[i]+=b/(weight[i]*z_dim)
                    ratio_total_f[i]+=(f+fb+b)/(weight[i]*z_dim)
                    ratio_total_b[i]+=(f+bf+b)/(weight[i]*z_dim)
                    sum_fg_fg[i]+=f/(z_dim)
                    sum_fg_bg[i]+=fb/(z_dim)
                    sum_bg_fg[i]+=bf/(z_dim)
                    sum_bg_bg[i]+=b/(z_dim)
                    sum_total_f[i]+=(f+fb+b)/(z_dim)
                    sum_total_b[i]+=(f+bf+b)/(z_dim)
                   
           
            #calculate overall overlap ratios of the current image
            overall_ratio_fg_fg_im=sum(sum_fg_fg_im)/no_shoeboxes
            overall_ratio_fg_bg_im=sum(sum_fg_bg_im)/no_shoeboxes
            overall_ratio_bg_fg_im=sum(sum_bg_fg_im)/no_shoeboxes
            overall_ratio_bg_bg_im=sum(sum_bg_bg_im)/no_shoeboxes
            overall_ratio_total_im=sum(sum_total_f_im)/no_shoeboxes
            
            end=timer()

            #print output
            print("Image no.:",z+1)
            print("No. of shoeboxes:", no_shoeboxes)
            print("total overlap ratio per shoebox",overall_ratio_total_im )
            print("foreground overlap ratio per shoebox",overall_ratio_fg_fg_im)
            print("background overlap ratio per shoebox",overall_ratio_bg_bg_im  )
            print("foreground background overlap ratio per shoebox",overall_ratio_fg_bg_im   )
            print("background foreground overlap ratio per shoebox", overall_ratio_bg_fg_im  )
            print("Time taken: ", end-start)
        
        #calculate overall overlap ratios of the whole dataset
        overall_ratio_fg_fg=sum(sum_fg_fg)/no_shoeboxes
        overall_ratio_fg_bg=sum(sum_fg_bg)/no_shoeboxes
        overall_ratio_bg_fg=sum(sum_bg_fg)/no_shoeboxes
        overall_ratio_bg_bg=sum(sum_bg_bg)/no_shoeboxes
        overall_ratio_total=sum(sum_total_f)/no_shoeboxes
        end_main=timer()
        
        #print output
        print("Overlap statistics for whole dataset:")    
        print("total overlap ratio per shoebox", overall_ratio_total)
        print("foreground overlap ratio per shoebox", overall_ratio_fg_fg)
        print("background overlap ratio per shoebox", overall_ratio_bg_bg)
        print("foreground background overlap ratio per shoebox", overall_ratio_fg_bg)
        print("background foreground overlap ratio per shoebox", overall_ratio_bg_fg)

        #write output files
        self.write_output_lists_shoebox(d2_list,ratio_total_f,ratio_total_b,ratio_bg_bg,ratio_fg_fg,ratio_fg_bg,ratio_bg_fg)
        self.write_output_total_shoebox(overall_ratio_total,overall_ratio_bg_bg,overall_ratio_fg_fg,overall_ratio_bg_fg)

        print("Time taken for imageset: ",end_main-start_main)
        return overall_ratio_total, overall_ratio_fg_fg,overall_ratio_bg_bg, overall_ratio_bg_fg
        
    def count_overlaps_per_pixel(self):
        '''The function that counts the overlaps per pixel on an image dataset.

        :returns: overall averages for the whole imageset (total, bg, fg, bg_fg)

        '''
        start_main=timer()
        z_dim,y_dim, x_dim,vmin,vmax,resolution=self.prepare_data()
       
        print(x_dim,y_dim)
        num_bins=self.num_bins
        #get bin labels(middle of resolution range) array with size of image with 
        #indices of bin the resolution is in and weight of each bin
        d2_list, index_array, weight = self.prepare_bins_pixel(vmax,vmin,num_bins,resolution)
        print("Prepared bins.")
        

        count_bg=[0]*num_bins
        count_fg=[0]*num_bins
        count_bg_fg=[0]*num_bins
        count_total=[0]*num_bins

        #loop through all images 
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
            print("Image no.:",z+1)
            print("No. of shoeboxes:", len(shoebox))
            print("total overlap ratio", (sum(count_bg_im)+sum(count_fg_im)+sum(count_bg_fg_im))/sum(weight))
            print("foreground overlap ratio",   sum(count_fg_im)/sum(weight))
            print("background overlap ratio",  sum(count_bg_im)/sum(weight))
            print("background foreground overlap ratio",   sum(count_bg_fg_im)/sum(weight))

            end=timer()
            
            print("Time taken for image:",end-start)  
        
        #ratio of overlaps per resolution bin
        ratio_total=[]
        ratio_bg=[]
        ratio_fg=[]
        ratio_bg_fg=[]

        for t,b,f,bf,w in zip(count_total,count_bg,count_fg,count_bg_fg,weight):      
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

        #write output files
        self.write_output_lists_pixel(d2_list,ratio_total,ratio_bg,ratio_fg,ratio_bg_fg)
        self.write_output_total_pixel(ratio_total_dataset,ratio_bg_dataset,ratio_fg_dataset,ratio_bg_fg_dataset)

        print("Time taken for dataset:", end_main-start_main)   

        return ratio_total_dataset, ratio_fg_dataset,ratio_bg_dataset, ratio_bg_fg_dataset


    def main(self):
        if self.run_shoeboxes:
            total,fg,bg,bg_fg= self.count_overlaps_per_reflection()
        else:
            total,fg,bg,bg_fg=self.count_overlaps_per_pixel()
        return total, fg,bg,bg_fg
def run():
    """Allows overlapping_spots to be called from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="command line argument")

    parser.add_argument(
        "--inputfile",
        dest="inputfile",
        type=str,
        help="The name of the json file that contains the reflection table.",
        default="13_integrated_experiments.json",
    )
    parser.add_argument(
        "--num_bins",
        dest="num_bins",
        type=int,
        help="The number of resolution bins",
        default=50,
    )
    parser.add_argument(
        "--outputfile_l",
        dest="outputfile_l",
        type=str,
        help="The name of the output file that contains the lists of the overlaps per resolution bin.",
        default="overlap_lists",
    )
    parser.add_argument(
            "--outputfile_t",
            dest="outputfile_t",
            type=str,
            help="The name of the output file that contains the average overlaps of the dataset",
            default="overlap_total",
        )
    parser.add_argument(
            "--run_shoeboxes",
            dest="run_shoeboxes",
            type=bool,
            help="The boolean which decides whether overlaps per shoebox should be run.",
            default=True,
        )
    args = parser.parse_args()
    overlap_counter = OverlapCounter(args.inputfile,args.num_bins,args.outputfile_l,args.outputfile_t,args.run_shoeboxes)
    overlap_counter.main()


if __name__ == "__main__":
    run()
