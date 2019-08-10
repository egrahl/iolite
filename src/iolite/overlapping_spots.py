from dials.array_family import flex
from dxtbx.model.experiment_list import ExperimentListFactory
from timeit import default_timer as timer
import numpy as np

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

def count_overlaps(shoebox,total_overlaps,num_bins, xy_list,index_list,x_dim,y_dim,z_dim):
    count_fg=[0]*num_bins
    count_bg=[0]*num_bins
    count_bg_fg=[0]*num_bins

    round=0
    for overlap in total_overlaps:
        print(overlap)
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
                                        pass #count_bg[index_list[xy_list.index((x,y))]] +=1
                                        
                                    elif intensity_a==intensity_b==5:
                                        pass #count_fg[index_list[xy_list.index((x,y))]] +=1
                                    else:
                                        pass #count_bg_fg[index_list[xy_list.index((x,y))]] +=1
        print(round)
        round +=1


    return count_bg,count_fg,count_bg_fg

def main():
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
    
    resolution=[]
    
    xy_list=[]
    
    for y in range(y_dim):
        for x in range(x_dim):
            xy_list.append((x,y))
            d = panel.get_resolution_at_pixel(beam.get_s0(), (x,y))
            resolution.append((1/d**2))
          
    print("Read in resolutions.")       
    vmin=min(resolution)
    vmax=max(resolution)
    num_bins=200
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
    
    print("Prepared bins.")
    
    #n_pixels = y_dim*x_dim

    
    ratio_bg=[0]*num_bins
    ratio_fg=[0]*num_bins
    ratio_bg_fg=[0]*num_bins
    ratio_total=[0]*num_bins

    end_main=timer()
    print("Time taken for preparation:", end_main-start_main)

    for i in range(z_dim):   #z_dim
        start = timer()

        filename= "shoeboxes_"+str(i)+".pickle"
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
        count_bg_im,count_fg_im, count_bg_fg_im = count_overlaps(shoebox,total_overlaps,num_bins,xy_list,index_list,x_dim,y_dim,z_dim)

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


        
        
    
        #print output
        print("Image no.:",i)
        print("No. of shoeboxes:", len(shoebox))
        print("total count overlap and ratio", sum(total_ratio_im))
        print("foreground overlap and ratio",   sum(fg_ratio_im))
        print("background overlap and ratio",  sum(bg_ratio_im))
        print("background foreground overlap and ratio",   sum(bg_fg_ratio_im))

        end=timer()
        print(end-start)

    print("Summed counts for the whole dataset:")
    print("total count overlap", sum(ratio_total))
    print("foreground overlap", sum(ratio_fg))
    print("background overlap", sum(ratio_bg))
    print("background foreground overlap", sum(ratio_total))
    
        

    


if __name__ == "__main__":
    main()