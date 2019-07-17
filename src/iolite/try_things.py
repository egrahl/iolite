from dxtbx.model.experiment_list import ExperimentListFactory

experiments = ExperimentListFactory.from_json_file("datablock.json")
assert len(experiments) == 1

beam = experiments[0].beam
detector = experiments[0].detector
imageset = experiments[0].imageset

panel = detector[0]

summed_data = None
summed_mask = None

# Loop through images
for i in range(10):
        
# Read image
            
    data = imageset.get_raw_data(i)
    mask = imageset.get_mask(i)
    assert isinstance(data, tuple)
    assert isinstance(mask, tuple)

    if summed_data is None:
        summed_mask = mask
        summed_data = data
    else:
        summed_data = [sd + d for sd, d in zip(summed_data, data)]
        summed_mask = [sm & m for sm, m in zip(summed_mask, mask)]        

mask_np = mask[0].as_numpy_array()
data_np = data[0].as_numpy_array()

from matplotlib import pylab
pylab.imshow(mask_np)
pylab.show()
#print(help(imageset))
