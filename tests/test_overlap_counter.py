import pytest
from iolite.overlaps.overlapping_spots import OverlapCounter
import random
import numpy as np

def test_overlap_counter():
    from dials.model.data import Shoebox
    from dials.array_family import flex
    from dxtbx.model.experiment_list import ExperimentListFactory, ExperimentListDumper

    # Generate input experiments file
    experiments = ExperimentListFactory.from_json_file("/dls/mx-scratch/gwx73773/data_files/3SNK/DEFAULT/NATIVE/SWEEP1/integrate/13_integrated_experiments.json")
    experiments[0].imageset = experiments[0].imageset[0:1]
    experiments[0].scan = experiments[0].scan[0:1]
    input_file="one_image_integrated_experiments.json"
    experiments.as_json("one_image_integrated_experiments.json")

    # Generate 1 example shoebox file
    reflections = flex.reflection_table(8)
    reflections['bbox'] = flex.int6(8)
    reflections['bbox'][0]=(1,6,1,6,0,1)
    reflections['bbox'][1]=(1,6,2,8,0,1)
    reflections['bbox'][2]=(5,10,4,9,0,1)
    reflections['bbox'][3]=(8,13,1,7,0,1)
    reflections['bbox'][4]=(8,13,5,10,0,1)
    reflections['bbox'][5]=(1,5,12,16,0,1)
    reflections['bbox'][6]=(4,8,12,16,0,1)
    reflections['bbox'][7]=(7,12,12,16,0,1)
    

    reflections['shoebox'] = flex.shoebox(8)
    for i in range(8):
        reflections['shoebox'][i]=Shoebox(reflections['bbox'][i])

    reflections['shoebox'][0].mask=flex.int(np.array([[[3,3,3,3,3],
                                                        [3,5,5,5,3],
                                                        [3,5,5,5,3],
                                                        [3,5,5,5,3],
                                                        [3,3,3,3,3]]], dtype=np.int32))
    reflections['shoebox'][1].mask=flex.int(np.array([[[3,3,3,3,3],
                                                    [3,5,5,5,3],
                                                    [3,5,5,5,3],
                                                    [3,5,5,5,3],
                                                    [3,3,3,3,3],
                                                    [3,3,3,3,3]]], dtype=np.int32))
    reflections['shoebox'][2].mask=flex.int(np.array([[[3,3,3,3,3],
                                                    [3,5,5,5,3],
                                                    [3,5,5,5,3],
                                                    [3,5,5,5,3],
                                                    [3,3,3,3,3]]], dtype=np.int32))
    reflections['shoebox'][3].mask=flex.int(np.array([[[3,3,3,3,3],
                                                    [3,3,3,3,3],
                                                    [3,5,5,5,3],
                                                    [3,5,5,5,3],
                                                    [3,5,5,5,3],
                                                    [3,3,3,3,3]]], dtype=np.int32))
    reflections['shoebox'][4].mask=flex.int(np.array([[[3,3,5,5,3],
                                                    [3,3,5,5,3],
                                                    [3,3,5,5,3],
                                                    [3,3,3,3,3],
                                                    [3,3,3,3,3]]], dtype=np.int32))
    reflections['shoebox'][5].mask=flex.int(np.array([[[3,3,3,3],
                                                    [3,5,5,3],
                                                    [3,5,5,3],
                                                    [3,3,3,3]]], dtype=np.int32))
    reflections['shoebox'][6].mask=flex.int(np.array([[
                                                    [3,3,3,3],
                                                    [3,5,5,3],
                                                    [3,5,5,3],
                                                    [3,3,3,3]]], dtype=np.int32))      
    reflections['shoebox'][7].mask=flex.int(np.array([[[3,3,3,3,3],
                                                        [3,5,5,3,3],
                                                        [3,5,5,3,3],
                                                        [3,3,3,3,3]
                                                        ]], dtype=np.int32))

    reflections['id']=flex.int(8)
    reflections['d']=flex.double(8)
    reflections['panel']=flex.size_t(8)
    reflections['imageset_id']=flex.int(8)
    for i in range(8):
        reflections['d'][i]= random.random()  
        reflections['id'][i]=0
        reflections['imageset_id'][i]=0
        reflections['panel'][i]=0                                           
    reflections.as_file("shoeboxes_0.pickle")

    # Run counter
    counter = OverlapCounter(input_file, 4, "test_overlap_lists.txt", "test_overlap_total.txt", True)
    total,fg,bg,bg_fg=counter.main()
    
    
    # Test output
    assert total==3.375
    assert bg==2
    assert fg==0.5
    assert bg_fg==0.875