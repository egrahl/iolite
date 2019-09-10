"""
The program ice_ring_classifier_test was used to optimize the parameters
of the peak finding algorithm. The program ice-rings.py was run on 148 
datasets (list of datasets in "data_sets.txt") which were labelled before by
looking at the images. These correct labels were saved in a file
"ice_ring_present.txt"(the order of the labels(0 for no ice-rings, 
one for ice-rings) is the same like the order of the pdb_ids in
"data_sets.txt", so the label refers to the correct dataset). The correct labels
and the labels given by ice_rings.py are saved to an output text file.  

"""

import os
import os.path
import numpy as np

from ice_ring.ice_rings import IceRingClassifier


def list_from_txt(name):
    """
    This function reads the lines of a txt file and 
    writes them as a list.

    :param str name: name of the txt file

    :returns: list of the lines in txt file

    """
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
    """
    The main function of ice_ring_classifier_test.py.
    """
    #get list of pdb ids from txt file 
    list_pdb_id = list_from_txt("data_sets.txt")

    #get labels of the datasets from txt file 
    list_present_string = list_from_txt("ice_ring_present.txt")
    
    #convert the strings to int
    list_present = [0] * len(list_present_string)
    for i in range(len(list_present_string)):
        if list_present_string[i] == "1":
            list_present[i] = 1

    #prepare lists that will hold data
    list_detected = [0] * len(list_pdb_id)
    list_count = [0] * len(list_pdb_id)
    list_strong_count = [0] * len(list_pdb_id)
   
    count = 0
    count_strong_rings = 0

    #loop through the datasets
    for id in list_pdb_id:
        print(count, id)
        for file in os.listdir(os.path.join(os.getcwd(), id)):
            #only run ice_rings if pre-processing was done
            if file.endswith("table.txt"):
                os.chdir(id)
                #classify the dataset with IceRingClassifier
                ice_ring_classifier = IceRingClassifier("table.txt", False)
                ice_ring_detected, ice_ring_count, strength, peaked = (
                    ice_ring_classifier.main()
                )
                #add classification results to lists
                list_detected[list_pdb_id.index(id)] = int(ice_ring_detected)
                list_count[list_pdb_id.index(id)] = ice_ring_count
                list_strong_count[list_pdb_id.index(id)] = int(strength)

                #count a dataset with strong ice-rings
                if strength == 1:
                    count_strong_rings += 1

        os.chdir("/dls/mx-scratch/gwx73773/data_files")
        count += 1

    print(count_strong_rings)

    #get number of attempt to write output file
    output_file = "results_"+input("number of attempt: ")+ ".txt"
 
    os.chdir("result_files_icerings")

    #write output file 
    with open(output_file, "w") as outfile:
        for p, d, c, s in zip(
            list_present, list_detected, list_count, list_strong_count
        ):
            outfile.write("%i, %i, %i, %i\n" % (p, d, c, s))


if __name__ == "__main__":
    main()
