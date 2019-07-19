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
    experiments = ExperimentListFactory.from_json_file("imported.expt")
    assert len(experiments) == 1

    beam = experiments[0].beam
    detector = experiments[0].detector
    imageset = experiments[0].imageset
    panel = detector[0]
  
    reflections = flex.reflection_table.from_pickle("strong.refl")
    

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
        data = tuple(i.as_numpy_array() for i in imageset.get_raw_data(n))[0]
        mask = tuple(m.as_numpy_array() for m in imageset.get_mask(n))[0]

        #create strong spot mask for image
        for sbox in image_shoebox_l[n]:
                
                x0, x1, y0, y1, z0, z1 = sbox.bbox
                mask_sp = sbox.mask.as_numpy_array()
                mask_sp_slice = mask_sp[n-z0,:,:]
                true_pixels = (mask_sp_slice == 5)
                mask_array[y0:y1,x0:x1] = np.logical_or(mask_array[y0:y1,x0:x1], true_pixels)

        mask_array = ~mask_array
        mask_combined = np.logical_and(mask,mask_array).astype(np.int)
        temp = data * mask_combined

        if summed_data is None:
            summed_data = temp
            summed_mask = mask_combined
        else:
            summed_data += temp
            summed_mask += mask_combined
        
   
    index = np.where(summed_mask > 0)
    summed_data[index] = summed_data[index] / summed_mask[index]

    average = summed_data
    final_mask = summed_mask > 0
    # from matplotlib import pylab
    # pylab.imshow(summed_data, vmax=100)
    # pylab.show()

    
    end = timer()
    print('Time taken:', end-start)
    """
    #show example mask
    from matplotlib import pylab
    pylab.imshow(temp_np)
    pylab.show()
    """
    

