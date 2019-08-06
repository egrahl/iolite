from __future__ import absolute_import, division, print_function
from dials.array_family import flex
from dxtbx.model.experiment_list import ExperimentListFactory
from timeit import default_timer as timer
import numpy as np

help_message = """

This program masks the strong spots of an imageset, followed by averaging of the images and making a radial average over resolution shells.


"""

# Create the phil scope
from libtbx.phil import parse

phil_scope = parse(
    """
  
  filename_pickle = 'strong.pickle'
        .type = str
        .help = "The filename of the file containing information about strong spots."
  
  output {
    filename = 'table.txt'
      .type = str
      .help = "The filename for the output table"
  }

  scan_range = None
    .type = ints(size=2)
    .help = "The scan range to do the average over"

  num_bins = None
    .type = int(value_min=1)
    .help = "The number of bins (default = w+h of image)"

  d_min = None
    .type = float
    .help = "The high resolution limit"

  d_max = None
    .type = float
    .help = "The low resolution limit"

"""
)


class Script:
    '''This class masks the strong spots of an imageset, followed by averaging of the images and making a radial average over resolution shells.'''

    def __init__(self):
        '''Initialise the script.'''
        from dials.util.options import OptionParser
        import libtbx.load_env

        # The script usage
        usage = "usage: iolite.radial_average_bg [options] imported.expt"

        # Create the parser
        self.parser = OptionParser(
            usage=usage, phil=phil_scope, epilog=help_message, read_experiments=True)


    def init_list_of_objects(self,size):
        ''' Create a list of empty lists of length size.
        
        :param int size: length of the nested list
        :returns: list of length size of empty lists  
        ''' 

        list_of_objects = list()
        for i in range(size):
            list_of_objects.append(list()) 
        return list_of_objects


    def summed_data_mask(self,imageset,scan_range,shoebox):
        '''Create numpy array of summed data and summed mask of an imageset,respectively, including masking of strong spots. 

        :param dxtbx_imageset_ext.ImageSweep imageset: imageset that contains the raw data
        :param tuple scan_range: range of images in the imageset
        :param list shoebox: list of all shoeboxes found in the imageset
        :returns: numpy array summed_data and summed_mask
        '''
    
        #get dimensions of the image
        y_dim = imageset.get_raw_data(0)[0].all()[0]   
        x_dim = imageset.get_raw_data(0)[0].all()[1]     

        #create nested list of shoeboxes per image
        _,_,_,_,_,z1 = shoebox[-1].bbox
        image_shoebox_l=self.init_list_of_objects(z1)
        for sbox in shoebox:
            x0, x1, y0, y1, z0, z1 = sbox.bbox
            for i in range(z0,z1):
                image_shoebox_l[i].append(sbox)

        summed_data = None
        summed_mask = None

        # Loop through images
        for n in range(*scan_range):   
            mask_array = np.zeros((y_dim,x_dim), dtype=bool) 
            data = tuple(i.as_numpy_array() for i in imageset.get_raw_data(n))[0]
            mask = tuple(m.as_numpy_array() for m in imageset.get_mask(n))[0]

            #create strong spot mask of current image 
            for sbox in image_shoebox_l[n]:
                    
                x0, x1, y0, y1, z0, z1 = sbox.bbox
                mask_sp = sbox.mask.as_numpy_array()
                mask_sp_slice = mask_sp[n-z0,:,:]
                true_pixels = (mask_sp_slice == 5)
                mask_array[y0:y1,x0:x1] = np.logical_or(mask_array[y0:y1,x0:x1], true_pixels)

            mask_array = ~mask_array
            mask_combined = np.logical_and(mask,mask_array).astype(np.int)


            #apply mask on data and sum data and mask up
            temp = data * mask_combined

            if summed_data is None:
                summed_data = temp
                summed_mask = mask_combined
            else:
                summed_data += temp
                summed_mask += mask_combined
        
        return summed_data, summed_mask

    def run(self):
        ''' Perform the integration.'''
        from dials.util.options import flatten_experiments
        from dials.util import log
        
        #start timer
        start=timer()

        # Parse the command line
        params, options = self.parser.parse_args(show_diff_phil=False)
        experiments = flatten_experiments(params.input.experiments)
        #experiments = ExperimentListFactory.from_json_file("11_refined_experiments.json")     
        if len(experiments) == 0:
            self.parser.print_help()
            return

        assert len(experiments) == 1
        imageset = experiments[0].imageset
        beam = experiments[0].beam
        detector = experiments[0].detector
        reflections = flex.reflection_table.from_pickle(params.filename_pickle)
        shoebox = reflections['shoebox']

        
        # Set the scan range
        if params.scan_range is None:
            scan_range = (0, len(imageset))
           
        else:
            scan_range = params.scan_range
            i0, i1 = scan_range
           
            if i0 < 0 or i1 > len(imageset):
                raise RuntimeError("Scan range outside image range")
            if i0 >= i1:
                raise RuntimeError("Invalid scan range")
    
        #apply masks on data, sum up data and mask
        summed_data, summed_mask = self.summed_data_mask(imageset, scan_range,shoebox)

        #calculate the average
        index = np.where(summed_mask > 0)
        summed_data[index] = summed_data[index] / summed_mask[index]
        average = summed_data
        final_mask = summed_mask > 5

        #filter out random high intensity pixels
        from scipy.signal import medfilt
        average = medfilt(average)

        #save average as .png file
        from matplotlib import pylab
        pylab.imshow(average)
        pylab.imsave('average_data',average)
        pylab.show()
        

        # Compute min and max and num
        if params.num_bins is None:
            num_bins = sum(sum(p.get_image_size()) for p in detector)
        if params.d_max is None:
            vmin = 0
        else:
            vmin = (1.0 / d_max) ** 2
        if params.d_min is None:
            params.d_min = detector.get_max_resolution(beam.get_s0())
        vmax = (1.0 / params.d_min) ** 2

        
        # Compute the radial average
        from dials.algorithms.background import RadialAverage

        radial_average = RadialAverage(beam, detector, vmin, vmax, num_bins)
        radial_average.add(flex.double(average.tolist()), flex.bool(final_mask))
        mean = radial_average.mean()
        reso = radial_average.inv_d2()

        #measure time taken
        end=timer()
        print('Time Taken:', end-start)

        #write output file
        with open(params.output.filename, "w") as outfile:
            for r, m in zip(reso, mean):
                outfile.write("%f, %f\n" % (r, m))


if __name__ == "__main__":
        script = Script()
        script.run()
    
