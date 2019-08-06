# from dxtbx.model.experiment_list import ExperimentListFactory

# experiments = ExperimentListFactory.from_json_file("datablock.json")
# assert len(experiments) == 1

# beam = experiments[0].beam
# detector = experiments[0].detector
# imageset = experiments[0].imageset

# panel = detector[0]

# summed_data = None
# summed_mask = None

# # Loop through images
# for i in range(10):

# # Read image

#     data = imageset.get_raw_data(i)

#     mask = imageset.get_mask(i)
#     assert isinstance(data, tuple)
#     assert isinstance(mask, tuple)

#     if summed_data is None:
#         summed_mask = mask
#         summed_data = data
#     else:
#         summed_data = [sd + d for sd, d in zip(summed_data, data)]
#         summed_mask = [sm & m for sm, m in zip(summed_mask, mask)]
# print(data[0].all()[0], data[0].all()[1])
# print(type(summed_mask[0]))
# mask_np = mask[0].as_numpy_array()
# data_np = data[0].as_numpy_array()
# summed_data_np = summed_data[0].as_numpy_array()
# summed_mask_np = summed_mask[0].as_numpy_array()

# from matplotlib import pylab
# pylab.imshow(summed_data_np,vmax=2000)
# pylab.show()

# ########################################################################
# # code for ice-ring-test:

# list_PDB_id = dataset_list()
# results=np.empty((len(list_PDB_id),2))
# os.chdir("/dls/mx-scratch/gwx73773/data_files")
# pickle_file=None
# count=0
# for id in list_PDB_id:

#     for file in os.listdir(os.path.join(os.getcwd(),id)):
#         if file.endswith("table.txt"):

#             ice_ring_classifier=IceRingClassifier(0.073,0.0755,0.196,0.200,0.269,0.2745,"table.txt",True)
#             ice_ring_detected= ice_ring_classifier.main()
#             results[list_PDB_id.index(id),1]= ice_ring_detecte
#             os.system("dials.image_viewer imported.expt")
#             ice_ring_present= input("Ice-rings present? [0/1]: ")
#             results[list_PDB_id.index(id),0]=ice_ring_present

#     os.chdir("/dls/mx-scratch/gwx73773/data_files")
#     count +=1
#     print(count, id)
# output_file= input("Name of output file: ")
# np.savetxt(output_file,results)


def list_from_txt(name):
    filein = open(name, "r")

    list_dataset = []
    for line in filein.readlines():
        if not line.strip():
            continue
        else:
            list_dataset.append(line.rstrip())
    filein.close()

    return list_dataset


def main():
    ir_present = list_from_txt("ice_ring_present.txt")

    ir_present_new = [0] * len(ir_present)
    for i in range(len(ir_present)):
        if ir_present[i] == "1.000000":
            ir_present_new[i] = 1

    with open("ice_ring_present_1.txt", "w") as outfile:
        for i in ir_present_new:
            outfile.write("%i\n" % (i))


if __name__ == "__main__":
    main()
