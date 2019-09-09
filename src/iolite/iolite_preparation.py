"""
iolite_preparation runs all programs of the software-package that are needed 
for the classification of the datasets by label_dataset.py

In order to run successfully, the dataset must consist of only one
sweep.
"""

import os
import os.path


def get_input_directories(source_directory_path,list_directories):
    """
    This function gets all the names (pdb ids) of the directories
    in the source directory and adds them to the list of directories.

    :param str source_directory_path: path to the source directory
    :param list list_directories: list of the directories

    :returns: list_directories
    """
    list_directories=list_directories+os.listdir(source_directory_path)

    return list_directories


def main(inputpath1,inputpath2):
    """
    This is the main function of iolite_preparation in which all preparation
    programs necessary for the classification of the datasets are run.

    :param str inputpath1: path to first source-directory
    :param str inputpath2: path to second source-directory
    """
    working_directory=os.getcwd()
    inputpaths=[inputpath1,inputpath2]

    #load cluster
    os.system("module load global/cluster")

    #write list of directories
    list_directories=[]
    list_directories=get_input_directories(inputpath1,list_directories)
    list_directories=get_input_directories(inputpath2,list_directories)

    #loop through pdb_ids(directories)
    for id in list_directories:
        #create directory for output in working directory
        make_directory="mkdir "+id
        os.system(make_directory)
        os.chdir(id)

        #get path to input data
        for ipath in inputpaths:
            for file in os.listdir(ipath):
                if file.endswith(id):
                    image_dir_path = os.path.join(ipath, file)
                    break

        #run preparation for ice_rings.py
        os.system(
            "chmod +x /dls/science/users/gwx73773/iolite/src/iolite/run_prep_for_ice_rings.sh"
        )
        os.system(
           "qsub -q low.q /dls/science/users/gwx73773/iolite/src/iolite/run_prep_for_ice_rings.sh "+image_dir_path
        )
        print("submitted " +id)

        #run preparation for overlapping spots and sigma_values
        os.system(
            "chmod +x /dls/science/users/gwx73773/iolite/src/iolite/run_prep_overlaps_sigma.sh"
        )
        os.system(
            "qsub -q low.q /dls/science/users/gwx73773/iolite/src/iolite/run_prep_overlaps_sigma.sh "+id + inputpath1 + inputpath2
        )
        print("Submitted "+id)
    

        os.chdir(working_directory)







def run():
    """Allows iolite_preparation to be called from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="command line argument")

    parser.add_argument(
        "--input1",
        dest="inputpath1",
        type=str,
        help="The path of the first input directory",
        default="/dls/metrix/metrix/anomalous_data",
    )
    parser.add_argument(
        "--input2",
        dest="inputpath2",
        type=str,
        help="The path of the second input directory.",
        default="/dls/metrix/metrix/MR_data",
    )



    args = parser.parse_args()
    main(args.inputpath1,args.inputpath2)

if __name__ == "__main__":
    run()