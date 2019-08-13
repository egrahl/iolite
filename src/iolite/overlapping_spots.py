from dials.array_family import flex
from dxtbx.model.experiment_list import ExperimentListFactory
from timeit import default_timer as timer
import numpy as np
import itertools
import matplotlib.pyplot as plt

def write_list_overlap_shoeboxes(coordinates):
    index_a=0
   
    total_overlaps=[]
    #loop through all shoeboxes (their coordinates)
    for c in coordinates:
        overlaps = []
        #make sure this is not the last shoebox in the list
        if index_a<(len(coordinates)-1):
            #writes list of coordinates of shoeboxes that overlap with the current shoebox, checks only shoeboxes that come later in the list
            overlaps=[i for i in coordinates[(index_a+1):] if (i[4]<c[5])  and (i[2]<c[3]) and (i[0]<c[1]) and (i[4]>=c[4]) and (i[2]>=c[2]) and (i[0]>=c[0])]
        #appends list of tuple of the index of the current shoebox in the list and a list of indices of the overlapping showboxes in the list
        if len(overlaps)>0:
            index_b_list=[]
            for o in overlaps:
                index_b=coordinates.index(o)
                index_b_list.append(index_b)
            total_overlaps.append((index_a,index_b_list))
        index_a +=1

    return total_overlaps

def count_overlaps(shoebox,total_overlaps,num_bins,index_np,x_dim,y_dim,z_dim):
    count_fg=[0]*num_bins
    count_bg=[0]*num_bins
    count_bg_fg=[0]*num_bins

    for overlap in total_overlaps:
       
        index_shoebox_a=overlap[0]
        for index_shoebox_b in overlap[1]:
            sbox_a=shoebox[index_shoebox_a]
            sbox_b=shoebox[index_shoebox_b]
            mask_a=sbox_a.mask.as_numpy_array()
            mask_b=sbox_b.mask.as_numpy_array()
            
            xa0,xa1,ya0,ya1,za0,za1=sbox_a.bbox
            xb0,xb1,yb0,yb1,zb0,zb1=sbox_b.bbox
            
            for i in range(min(za1,zb1)-zb0):
                z=zb0+i
                if (z>=0) and (z<z_dim): 
                    for j in range(min(ya1,yb1)-yb0):
                        y=yb0+j
                        if (y>=0) and (y<y_dim):
                            for n in range(min(xa1,xb1)-xb0):
                                x=xb0+n
                                if (x>=0) and (x<x_dim):
                                    intensity_b=mask_b[i,j,n]
                                    intensity_a=mask_a[(z-za0),(y-ya0),(x-xa0)]
                                    
                                    if intensity_a== intensity_b ==3:
                                        count_bg[index_np[y,x]] +=1
                                        
                                    elif intensity_a==intensity_b==5:
                                        count_fg[index_np[y,x]] +=1
                                    elif ((intensity_a==3) and (intensity_b==5)) or ((intensity_a==5)and (intensity_b==3)):
                                        count_bg_fg[index_np[y,x]] +=1
        
    
   
    return count_bg,count_fg,count_bg_fg

def lists_xy_resolution(x_dim,y_dim,panel,beam):
    resolution=[]
    xy_np=np.zeros((y_dim*x_dim),dtype=tuple)
    xy_list=[]
    round=0
    for y in range(y_dim):
        for x in range(x_dim):
            xy_np[round]=(x,y)
            xy_list.append((x,y))
            d = panel.get_resolution_at_pixel(beam.get_s0(), (x,y))
            resolution.append((1/d**2))
            round+=1
    
    return xy_list,xy_np, resolution
def np_resolution(x_dim,y_dim,panel,beam):
    resolution=np.zeros((y_dim,x_dim))
    for y in range(y_dim):
        for x in range(x_dim):
            d = panel.get_resolution_at_pixel(beam.get_s0(), (x,y))
            resolution[y,x]=(1/d**2)

    return resolution
def np_prepare_bins(vmax, vmin, num_bins,resolution):
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
    index_array_reshape=np.reshape(index_array,resolution.shape)
   
    return d2_list, index_array_reshape, weight
     
def prepare_bins_1d_np(vmax, vmin, num_bins,resolution):
    d2_list=[]
    weight=[0]*num_bins
    index_np=np.zeros((len(resolution)),dtype=int)
    intervall=(vmax-vmin)/(num_bins)
    
    for i in range(num_bins):
        d2=vmin+((2*i+1)/2)*intervall
        d2_list.append(d2)
    round=0
    for d2 in resolution:
        if d2==vmin:
            index=0
        elif d2==vmax:
            index=num_bins-1
        else:
            index=int((d2-vmin-intervall/2)/intervall)
        index_np[round]=index
        
        weight[index]+=1
        round+=1

    return d2_list, index_np, weight 




def prepare_bins(vmax, vmin, num_bins,resolution):
    d2_list=[]
    weight=[0]*num_bins
    index_list=[]
    intervall=(vmax-vmin)/(num_bins)
    
    for i in range(num_bins):
        d2=vmin+((2*i+1)/2)*intervall
        d2_list.append(d2)
    for d2 in resolution:
        if d2==vmin:
            index=0
        elif d2==vmax:
            index=num_bins-1
        else:
            index=int((d2-vmin-intervall/2)/intervall)
        index_list.append(index)
      
        weight[index]+=1

    return d2_list, index_list, weight 

def sum_masks(shoebox,x_dim,y_dim,z):
    mask_im=np.zeros((y_dim,x_dim),dtype=int)
    mask_count=np.zeros((y_dim,x_dim),dtype=int)
    for sbox in shoebox:
        x0, x1, y0, y1, z0, z1 = sbox.bbox
        mask_sbox=sbox.mask.as_numpy_array()
        count_x0=0
        count_y0=0
        count_x1=-1
        count_y1=-1

        #set invalid pixels to 0
        mask_sbox[mask_sbox==2]=0
        mask_sbox[mask_sbox==4]=0


        for x in range(x0,(x1+1)):
            if x<=x_dim:
                x1=x
                count_x1+=1  
        
        for x in range(x0,(x1+1)):
            if x>=0:
                x0=x
                break
            count_x0+=1

        for y in range(y0,(y1+1)):
            if y<=y_dim:
                y1=y
                count_y1+=1
              
        for y in range(y0,(y1+1)):
            if y>=0:
                y0=y
                break
            count_y0+=1
        count=np.ones(((count_y1-count_y0),(count_x1-count_x0)),dtype=int)
        mask_im[y0:y1, x0:x1]=np.add(mask_im[y0:y1,x0:x1],mask_sbox[z-z0,count_y0:count_y1,count_x0:count_x1])  
        mask_count[y0:y1, x0:x1]=np.add(mask_count[y0:y1,x0:x1],count)
    return mask_im, mask_count

def find_shoeboxes_per_pixel(xy_list,z, coordinates, shoebox):
    start_t=timer()
    overlaps=[]
    
    for xy in xy_list:
        x=xy[0]
        y=xy[1]
        sboxes_at_pixel= [s for s,c in zip(shoebox,coordinates) if (x>=c[0])and (x<c[1])and (y>=c[2])and (y<c[3])and (z>=c[4])and (z<c[5])]
        overlaps.append(sboxes_at_pixel)
      
    end_t=timer()    
    print("time to find shoeboxes at pixel", end_t-start_t)
    return overlaps

def specify_overlap(overlap, xy_list,z):
    bg=[0]*len(overlap)
    fg=[0]*len(overlap)
    bg_fg=[0]*len(overlap)
    for o,xy, b,f, bf in zip(overlap,xy_list,bg,fg,bg_fg):
        num_sbox =len(o)
        x= xy[0]
        y=xy[1]
        if num_sbox>1:
            for sbox1 in o[:(num_sbox-1)]:
                index_a= o.index(sbox1)
                for sbox2 in o[(index_a+1):]:
                    mask1 = sbox1.mask.as_numpy_array()
                    mask2 = sbox2.mask.as_numpy_array()
                    intensity1= mask[(z-sbox1.bbox[4]),(y-sbox1.bbox[2]),(x-sbox1.bbox[0])]
                    intensity2= mask[(z-sbox2.bbox[4]),(y-sbox2.bbox[2]),(x-sbox2.bbox[0])]

                    if intensity_a== intensity_b ==3:
                        b+=1
                        
                    elif intensity_a==intensity_b==5:
                        f+=1
                    else:
                        bf+=1
                        

    return bg, fg, bg_fg

def plot_bar_chart(d2_list, ratio):
    plt.bar(d2_list,ratio)
    plt.show()
def first_try():
    start_main=timer()

    experiments = ExperimentListFactory.from_json_file("13_integrated_experiments.json")
    assert len(experiments) == 1
    imageset = experiments[0].imageset
    beam = experiments[0].beam
    detector = experiments[0].detector  
    panel = detector[0]

    # get dimensions of the dataset
    y_dim = imageset.get_raw_data(0)[0].all()[0]
    x_dim = imageset.get_raw_data(0)[0].all()[1]
    z_dim = len(imageset)
    
    resolution = np_resolution(x_dim,y_dim,panel,beam)
          
    print("Read in resolutions.")    

    vmin=np.amin(resolution)
    vmax=np.amax(resolution)
    num_bins=10

    d2_list, index_np, weight = np_prepare_bins(vmax,vmin,num_bins,resolution)

    print("Prepared bins.")

    
    ratio_bg=[0]*num_bins
    ratio_fg=[0]*num_bins
    ratio_bg_fg=[0]*num_bins
    ratio_total=[0]*num_bins

    end_main=timer()
    print("Time taken for preparation:", end_main-start_main)

    for z in range(1):   #z_dim
        start = timer()

        filename= "shoeboxes_"+str(z)+".pickle"
        #get shoeboxes from pickle file
        reflections = flex.reflection_table.from_pickle(filename)
        shoebox = reflections["shoebox"]

        #write list of coordinates of every shoebox
        coordinates=[]
      
        for sbox in shoebox:
            coordinates.append(sbox.bbox)
            


        #get list of tuples of indexes of overlapping shoeboxes    
        total_overlaps=write_list_overlap_shoeboxes(coordinates)
        
        
        print("Wrote list of overlaps")
       
        #get list of counts of different overlaps for whole dataset
        count_bg_im,count_fg_im, count_bg_fg_im = count_overlaps(shoebox,total_overlaps,num_bins,index_np,x_dim,y_dim,z_dim)

        #calculated weighted counts and sum up for overall dataset
        bg_ratio_im=[]
        fg_ratio_im=[]
        bg_fg_ratio_im= []
        total_ratio_im=[]
        round=0
        for b,f,bf,w in zip(count_bg_im,count_fg_im,count_bg_fg_im,weight):
            bg_ratio_im.append(b/w)
            fg_ratio_im.append(f/w) 
            bg_fg_ratio_im.append(bf/w)
            total_ratio_im.append(b/w+f/w+bf/w)
            ratio_bg[round]+= (b/w)
            ratio_fg[round]+= (f/w)
            ratio_bg_fg[round]+= (bf/w)
            ratio_total[round]+= (b/w+f/w+bf/w)
            round +=1

        print(count_bg_im)
        #print output
        print("Image no.:",z)
        print("No. of shoeboxes:", len(shoebox))
        print("total count overlap ratio", (sum(count_bg_im)+sum(count_fg_im)+sum(count_bg_fg_im))/sum(weight))
        print("foreground overlap ratio",   sum(count_fg_im)/sum(weight))
        print("background overlap ratio",  sum(count_bg_im)/sum(weight))
        print("background foreground overlap ratio",   sum(count_bg_fg_im)/sum(weight))

        end=timer()
        print("Time for image:", end-start)
        #plot_bar_chart(d2_list,bg_ratio_im)

    # print("Summed counts for the whole dataset:")
    # print("total count overlap", sum(ratio_total))
    # print("foreground overlap", sum(ratio_fg))
    # print("background overlap", sum(ratio_bg))
    # print("background foreground overlap", sum(ratio_total))

def second_try():
    start_main=timer()

    experiments = ExperimentListFactory.from_json_file("13_integrated_experiments.json")
    assert len(experiments) == 1
    imageset = experiments[0].imageset
    beam = experiments[0].beam
    detector = experiments[0].detector  
    panel = detector[0]

    # get dimensions of the dataset
    y_dim = imageset.get_raw_data(0)[0].all()[0]
    x_dim = imageset.get_raw_data(0)[0].all()[1]
    z_dim = len(imageset)

    xy_list, resolution = lists_xy_resolution(x_dim,y_dim,panel,beam)
          
    print("Read in resolutions.")    

    vmin=min(resolution)
    vmax=max(resolution)
    num_bins=200

    d2_list, index_list, weight = prepare_bins(vmax,vmin,num_bins,resolution)

    print("Prepared bins.")

    for z in range(z_dim):
        filename= "shoeboxes_"+str(z)+".pickle"
        #get shoeboxes from pickle file
        reflections = flex.reflection_table.from_pickle(filename)
        shoebox = reflections["shoebox"]

        #write list of coordinates of every shoebox
        coordinates=[]
      
        for sbox in shoebox:
            coordinates.append(sbox.bbox)
        
        #write a list which contains lists of shoeboxes at each pixel
        overlaps=find_shoeboxes_per_pixel(xy_list,z,coordinates,shoebox)

        #write lists containing count of overlaps(kind is specified) corresponding to every pixel 
        bg_im,fg_im, bg_fg_im = specify_overlap(overlap,xy_list,z)

        #bin the overlaps
        bg_bin=[0]*len(d2_list)
        fg_bin=[0]*len(d2_list)
        bg_fg_bin=[0]*len(d2_list)

        for b,f, bf, index in zip(bg_im, fg_im, bg_fg_im,index_list):
            bg_bin[index]+=b
            fg_bin[index]+=f
            bg_fg_bin[index]+=bf

        #calculate weighted lists
        bg_w=[]
        fg_w=[]
        bg_fg_w=[]
        for b,f,bf,w in zip(bg_bin,fg_bin,bg_fg_bin,weight):
            bg_w.append(b/w)
            fg_w.append(f/w)
            bg_fg_w.append(bf/w)

def third_try():
    start_main=timer()

    experiments = ExperimentListFactory.from_json_file("13_integrated_experiments.json")
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
    resolution= np_resolution(x_dim,y_dim,panel,beam)      
    print("Read in resolutions.")    

    #get vmin, vmx and number of bins
    vmin=np.amin(resolution)
    
    vmax=np.amax(resolution)
    num_bins=50
    
    #get bin labels(middle of resolution range) array with size of image with 
    #indices of bin the resolution is in and weight of each bin
    d2_list, index_array, weight = np_prepare_bins(vmax,vmin,num_bins,resolution)
    print("Prepared bins.")

    print(weight)
    #array of possible sums of the masks at one pixel
    #row index = number of bg, column index=number of fg
    outputs=np.array([[0,5,10,15,20,25,30],
                    [3,8,13,18,23,28,0],
                    [6,11,16,21,26,0,0],
                    [9,14,19,24,0,0,0],
                    [12,17,22,0,0,0,0]])

    ratio_bg=[0]*num_bins
    ratio_fg=[0]*num_bins
    ratio_bg_fg=[0]*num_bins
    ratio_total=[0]*num_bins

    for z in range(z_dim):    #z_dim
        start=timer()
        filename= "shoeboxes_"+str(z)+".pickle"
        #get shoeboxes from pickle file
        reflections = flex.reflection_table.from_pickle(filename)
        shoebox = reflections["shoebox"]

        mask_im, mask_count=sum_masks(shoebox,x_dim,y_dim,z)
        y_round=0
        x_round=0
        count_bg=[0]*len(d2_list)
        count_fg=[0]*len(d2_list)
        count_bg_fg=[0]*len(d2_list)

        for row_value,row_count in itertools.izip(mask_im,mask_count):
            for value, count in itertools.izip(mask_im[row_value[0]],mask_count[row_count[0]]):
                if value >5:
                    
                    if value==15 and count==5:
                        count_bg[index_array[y_round,x_round]] +=10
                    elif value==20 and count==6:
                        count_bg[index_array[y_round,x_round]] +=10
                        count_bg_fg[index_array[y_round,x_round]]+=5
                    elif value==18 and count==6:
                        count_bg[index_array[y_round,x_round]] +=15
                    else:
                        no_bg=np.where(outputs== value)[0][0]
                        no_fg=np.where(outputs== value)[1][0]
                        
                        count_bg[index_array[y_round,x_round]]+= (no_bg*(no_bg-1)/2)
                        count_fg[index_array[y_round,x_round]]+= (no_fg*(no_fg-1)/2)
                        count_bg_fg[index_array[y_round,x_round]]+= no_bg*no_fg

                
            y_round+=1
            x_round=0
        
        print(count_bg)
        bg_ratio_im=[]
        fg_ratio_im=[]
        bg_fg_ratio_im= []
        total_ratio_im=[]
        round=0
        for b,f,bf,w in zip(count_bg,count_fg,count_bg_fg,weight):
            bg_ratio_im.append(b/w)
            fg_ratio_im.append(f/w) 
            bg_fg_ratio_im.append(bf/w)
            total_ratio_im.append(b/w+f/w+bf/w)
            ratio_bg[round]+= (b/w)
            ratio_fg[round]+= (f/w)
            ratio_bg_fg[round]+= (bf/w)
            ratio_total[round]+= (b/w+f/w+bf/w)
            round +=1
        
    
        #print output
        print("Image no.:",z)
        print("No. of shoeboxes:", len(shoebox))
        print("total count overlap ratio", (sum(count_bg)+sum(count_fg)+sum(count_bg_fg))/sum(weight))
        print("foreground overlap ratio",   sum(count_fg)/sum(weight))
        print("background overlap ratio",  sum(count_bg)/sum(weight))
        print("background foreground overlap ratio",   sum(count_bg_fg)/sum(weight))

        end=timer()
        print("Time for image:", end-start)
        #plot_bar_chart(d2_list,fg_ratio_im)

    # print("Summed counts for the whole dataset:")
    # print("total count overlap", sum(ratio_total))
    # print("foreground overlap", sum(ratio_fg))
    # print("background overlap", sum(ratio_bg))
    # print("background foreground overlap", sum(ratio_total))


def main():
    #first_try()
    third_try()
        

    
    
        

    


if __name__ == "__main__":
    main()