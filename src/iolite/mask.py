from dials.array_family import flex
from dxtbx.model.experiment_list import ExperimentListFactory
from timeit import default_timer as timer
import numpy as np


def init_list_of_objects(size):
    list_of_objects = list()
    for i in range(size):
        list_of_objects.append(list()) #different object reference each time
    return list_of_objects



if __name__ == "__main__":
    start = timer()
    experiments = ExperimentListFactory.from_json_file("datablock.json")
    assert len(experiments) == 1

    beam = experiments[0].beam
    detector = experiments[0].detector
    imageset = experiments[0].imageset
    panel = detector[0]
  
    reflections = flex.reflection_table.from_pickle("strong.pickle")
    

    shoebox = reflections['shoebox']
   

    #get dimensions of the image
    y_dim = imageset.get_raw_data(0)[0].all()[0]   
    x_dim = imageset.get_raw_data(0)[0].all()[1]     

    
    #create nested list of shoeboxes 
    image_shoebox_l=init_list_of_objects(len(imageset))

    for sbox in shoebox:
        x0, x1, y0, y1, z0, z1 = sbox.bbox
        
        for i in range(z0,z1):
            image_shoebox_l[i].append(sbox)
        
    
    summed_data = None
    summed_mask = None
   

    # Read image
    for n in range(len(imageset)):   
        mask_array = np.zeros((y_dim,x_dim), dtype=bool) 
        data = imageset.get_raw_data(i)
        mask = imageset.get_mask(i)

        assert isinstance(data, tuple)
        assert isinstance(mask, tuple)

        #create strong spot mask for image
        for sbox in image_shoebox_l[n]:
                
                x0, x1, y0, y1, z0, z1 = sbox.bbox
                mask_sp = sbox.mask 
                mask_np = mask_sp.as_numpy_array()
                mask_np_slice = mask_np[n-z0]
                true_pixels = (mask_np_slice == 5)
                mask_array[y0:y1,x0:x1] = np.logical_or(mask_array[y0:y1,x0:x1], true_pixels)

        mask_array = ~mask_array
        mask_array_flex=flex.bool(mask_array)
        mask_strong_spots=(mask_array_flex,)
        mask_strong_spots_np = mask_strong_spots[0].as_numpy_array()
        
        mask_np = mask[0].as_numpy_array()
        
        mask_combined_np = np.logical_and(mask_np,mask_array)
        mask_combined = (flex.int(mask_combined_np),)
        mask_combined_int_np = mask_combined[0].as_numpy_array()

        temp = data[0] * mask_combined[0]

        if summed_data is None:
            summed_data = temp
            summed_mask = mask_combined
        else:
            summed_data += temp
            summed_mask += mask_combined
        
        from matplotlib import pylab
        pylab.imshow(mask_combined_np)
        pylab.show()
   
    summed_mask_np = summed_mask.as_numpy_array()
    """
    if np.any(summed_mask_np):
        average = summed_data / summed_mask
    else:
        average = summed_data/len(imageset)
    """
    #average_np = average.as_numpy_array()
    summed_data_np = summed_data.as_numpy_array()
    mask_strong_spots_np = mask_strong_spots[0].as_numpy_array()
    temp_np = temp.as_numpy_array()

    
    end = timer()
    print('Time taken:', end-start)
    """
    #show example mask
    from matplotlib import pylab
    pylab.imshow(temp_np)
    pylab.show()
    """
    

