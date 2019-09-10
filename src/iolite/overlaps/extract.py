#!/usr/bin/env python
#
# extract.py
#
#  Copyright (C) 2013 Diamond Light Source
#
#  Author: James Parkhurst
#
#  This code is distributed under the BSD license, a copy of which is
#  included in the root directory of this package.

# LIBTBX_SET_DISPATCHER_NAME dev.dials.extract_shoeboxes

from __future__ import absolute_import, division, print_function

import logging

logger = logging.getLogger("dials.command_line.extract_shoeboxes")

help_message = """

This program takes an experiment list and reflections with shoeboxes and
extracts pixels from the images. The shoeboxes are then saved to file.

Examples::

dials.extract_shoeboxes models.expt observations.refl

"""

from libtbx.phil import parse
from collections import defaultdict
from dials.array_family import flex

phil_scope = parse(
    """
  output {
    prefix = 'shoeboxes_'
      .type = str
      .help = "The integrated output filename"
  }
"""
)


class Script(object):
    """ Class to run the script. """

    def __init__(self):
        """ Initialise the script. """

        from dials.util.options import OptionParser
        import libtbx.load_env

        # The script usage
        usage = (
            "usage: dials.python extract.py [options] experiment.expt observations.refl"
        )

        # Create the parser
        self.parser = OptionParser(
            usage=usage,
            phil=phil_scope,
            epilog=help_message,
            read_experiments=True,
            read_reflections=True,
        )

    def create_reflection_lookup(self, reflections):
        lookup = defaultdict(flex.size_t)
        for i, bbox in enumerate(reflections['bbox']):
            assert bbox[5] == bbox[4]+1
            lookup[bbox[4]].append(i)
        return dict((key, reflections.select(value)) for key, value in lookup.iteritems())

    def run(self):
        """ Extract the shoeboxes. """
        from dials.util.options import flatten_reflections
        from dials.util.options import flatten_experiments
        from dials.util.options import flatten_experiments
        from dials.util import log
        from dials.array_family import flex
        from dials.util import Sorry

        # Parse the command line
        params, options = self.parser.parse_args(show_diff_phil=False)

        # Configure logging
        log.config()

        # Log the diff phil
        diff_phil = self.parser.diff_phil.as_str()
        if diff_phil is not "":
            logger.info("The following parameters have been modified:\n")
            logger.info(diff_phil)

        # Get the data
        reflections = flatten_reflections(params.input.reflections)
        experiments = flatten_experiments(params.input.experiments)
        if not any([experiments, reflections]):
            self.parser.print_help()
            exit(0)
        elif len(experiments) > 1:
            raise Sorry("More than 1 experiment set")
        elif len(experiments) == 1:
            imageset = experiments[0].imageset
        if len(reflections) != 1:
            raise Sorry("Need 1 reflection table, got %d" % len(reflections))
        else:
            reflections = reflections[0]

        # Check the reflections contain the necessary stuff
        assert "bbox" in reflections
        assert "panel" in reflections

        # Check the experiments have a profile model
        assert experiments[0].profile is not None

        # Get some models
        detector = imageset.get_detector()
        scan = imageset.get_scan()
        frame0, frame1 = scan.get_array_range()

        # Split reflections into individual frames
        del reflections['shoebox']
        reflections.split_partials()

        # Remove junk
        reflections = reflections.select(reflections['id'] >= 0)
        reflections = reflections.select(reflections['miller_index'] != (0,0,0))
        reflections = reflections.select(reflections.get_flags(reflections.flags.integrated_sum))

        # Create a lookup of frame -> reflection table
        reflection_lookup = self.create_reflection_lookup(reflections)

        # Loop through frames
        for frame in range(len(imageset)):
       
            # Get the subset on this frame
            subset_reflections = reflection_lookup[frame]

            # Allocate the shoeboxes
            subset_reflections["shoebox"] = flex.shoebox(
                subset_reflections["panel"], subset_reflections["bbox"], allocate=True
            )
                        
            # Extract the shoeboxes
            subset_reflections.extract_shoeboxes(imageset[frame:frame+1], verbose=True)

            # Compute the mask
            subset_reflections.compute_mask(experiments)

            # Saving the reflections to disk
            filename = "%s%d.pickle" % (params.output.prefix, frame)
            logger.info("Saving %d reflections to %s" % (len(subset_reflections), filename))
            subset_reflections.as_pickle(filename)


if __name__ == "__main__":
    from dials.util import halraiser

    try:
        script = Script()
        script.run()
    except Exception as e:
        halraiser(e)
