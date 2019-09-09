"""
run_xia2 is a program that runs xia2 on data from the 2
source input directories and writes the output into the current 
working directory. It can only run successfully, if the images 
have the same prefix. Furthermore, it runs xia2 in a way, that 
extratc.py can extract the shoeboxes of each image.

"""

import os
import os.path


def run_xia2(inputpaths,id):
    """
    This functions runs xia2 on the dataset.

    :param list inputpaths: the list containing the paths to both input directories
    :param str id: pdb id of the dataset
    """
    path = os.getcwd()
    os.system("module load xia2")
  
    #get path to directory that contains the images
    for ipath in inputpaths:
        for file in os.listdir(ipath):
            if file.endswith(id):
                image_dir_path = os.path.join(ipath, file)
                break

    #list of all files in directory
    list_files = os.listdir(image_dir_path)
    
    #get only the image files of the directory
    list_files_for_processing=[]
    for file in list_files:
        if file.endswith(".mccd") or file.endswith(".img") or file.endswith(".cbf"):
            list_files_for_processing.append(file)

    num_images=len(list_files_for_processing)
    first_image=list_files_for_processing[0]        
    first_image_path = os.path.join(image_dir_path, first_image)

    dest_directory = path
    os.chdir(dest_directory)
    
    #run xia2
    command = (
        "xia2 image="
        + first_image_path
        + ":1:"
        + str(num_images)
        + " dials.integrate.phil_file=/dls/science/users/gwx73773/iolite/share/integrate_params.phil"
    )
    os.system(command)
    os.chdir(path)

def main(inputpath1,inputpath2,pdb_id):
    """
    This is the main function of run_xia.py.

    :param str inputpath1: path to first input directory
    :param str inputpath2: path to second input directory
    :param str pdb_id: pdb id of the dataset
    """
    list_inputs=[inputpath1,inputpath2]
    run_xia2(list_inputs,pdb_id)


def run():
    """Allows run_xia2 to be called from command line."""
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
    parser.add_argument(
        "--id",
        dest="pdb_id",
        type=str,
        help="Pdb id",
    )
   


    args = parser.parse_args()
    main(args.inputpath1,args.inputpath2,args.pdb_id)
    
    

if __name__ == "__main__":
    run()
