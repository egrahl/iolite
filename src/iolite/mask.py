from dials.array_family import flex
from dxtbx.model.experiment_list import ExperimentListFactory
import numpy as np




if __name__ == "__main__":

    experiments = ExperimentListFactory.from_json_file("datablock.json")
    assert len(experiments) == 1

    beam = experiments[0].beam
    detector = experiments[0].detector
    imageset = experiments[0].imageset
    panel = detector[0]

    print(len(imageset))
    
  
    reflections = flex.reflection_table.from_pickle("strong.pickle")
    
    #print(reflections[0])

    shoebox = reflections['shoebox']
   
    mask_list = [np.ones((image_width, image_length))]*len(imageset)    #need to find the right expression for that 

    
    for sbox in shoebox:
        x0, x1, y0, y1, z0, z1 = sbox.bbox
        #print(sbox.bbox) # ()
        mask = sbox.mask # 3D array where 0 is background and 1 | 4 = 5 is foreground
        mask_np = mask.as_numpy_array()
        #print(mask_np)
        
        for n in np.nditer(mask_np,op_flags = ['readwrite']):
            if n ==5:
                n[...] = False
            else:
                n[...] = True
        print(mask_np)

        for z in range(z0,z1):
            for y in range(y0,y1):
                for x in range(x0,x1):
                    mask_list[z][y][x] = #the mask_np array has different dimensions, I need to get the right elements
        
    
   


    """
    for i in range(10):
        coord = shoebox[i].bbox
        mask = shoebox[i].mask 
        mask_np = mask.as_numpy_array()

        print(coord)
        print(mask_np)

    #print(shoebox_coord)
    """
