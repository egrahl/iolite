from dxtbx.model.experiment_list import ExperimentListFactory

experiments = ExperimentListFactory.from_json_file("datablock.json")
assert len(experiments) == 1

beam = experiments[0].beam
detector = experiments[0].detector
imageset = experiments[0].imageset

panel = detector[0]
d = panel.get_resolution_at_pixel(beam.get_s0(), (0,0))
print("Resolution at pixel (0,0) = %f" % d)
