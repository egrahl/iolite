"""
The program collect_data_overlaps can combine the data of 
overlapping_spots.py from several datasets. These datasets are
either given in a txt file or the program will look through
all the dataset directories in the current working directory.
It will write txt files with the overlap data of all datasets,
if present. 

output files: "count_overlaps_shoebox.txt","count_overlaps_pixel.txt"

"""

import os
import os.path




def list_from_txt(name):
    """
    This function reads out a list from a txt file.

    :param str name: name of txt file

    :returns: list from txt file 
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

def write_pdb_id_l_directory():
    """
    This function writes a list of all pdb_id directories in the current
    working directory.

    :returns: list of pdb_ids in the directories
    """
    list_dir=os.listdir()
    pdb_id_l=[]
    for dir in list_dir:
        if len(dir)==4:
            if dir.startswith("1") or dir.startswith("2") or dir.startswith("3") or dir.startswith("4") or dir.startswith("5"):
                pdb_id_l.append(dir)

    return(pdb_id_l)

def put_data_overlap_in_file(pdb_id_l,inputfile,outputfile):
    """
    This function collects all the available total overlap data
    of the datasets and writes them into one txt file.

    :param list pdb_id_l: list with all dataset pdb_ids
    :param str inputfile: the name of the file containing the overlap data
    :param str outputfile: the name of the outputfile
    """
    path = os.getcwd()
    

    #prepare overlap lists
    total_ratio = []
    fg_ratio = []
    bg_ratio = []
    bg_fg_ratio = []
    pdb_id_l_output=[]
    #loop through the datasets
    for id in pdb_id_l:
        #make sure inputfile exists
        try:
            for file in os.listdir(
                os.path.join(path, id, "DEFAULT/NATIVE/SWEEP1/integrate")
            ):
                if file == inputfile:
                    pdb_id_l_output.append(id)
                    dest_path = os.path.join(path, id, "DEFAULT/NATIVE/SWEEP1/integrate")
                    os.chdir(dest_path)
                    filein = open(file, "r")
        
                    count_line = 0
                    #read data from txt file
                    for line in filein.readlines():
                        tokens = line.split(",")
                        if count_line == 0:
                            total_ratio.append(float(tokens[1]))
                        elif count_line == 1:
                            fg_ratio.append(float(tokens[1]))
                        elif count_line == 2:
                            bg_ratio.append(float(tokens[1]))
                        else:
                            bg_fg_ratio.append(float(tokens[1]))

                        count_line += 1

                    filein.close()
        except:
            pass
        os.chdir(path)
       
    #write output file
    with open(outputfile, "w") as outfile:
        for id, t, f, b, bf in zip(
            pdb_id_l_output, total_ratio, fg_ratio, bg_ratio, bg_fg_ratio
        ):
            outfile.write("%s, %f, %f, %f, %f\n" % (id, t, f, b, bf))

def main(inputfile):
    """This is the main function of collect_data_overlaps.

    :param bool inputfile: boolean that decides if the pdb_ids should be
                           read from a txt file (default:True)
    """
    #select source of list of pdb_ids
    if inputfile:
        infile = input("give inputfile: ")
        pdb_id_list = list_from_txt(infile)
    else:
        pdb_id_list=write_pdb_id_l_directory()

    #collect overlap data and write to file (shoebox and pixel)
    put_data_overlap_in_file(pdb_id_list,"overlap_total_shoebox.txt","count_overlaps_shoebox.txt")
    put_data_overlap_in_file(pdb_id_list,"overlap_total_pixel.txt","count_overlaps_pixel.txt")

def run():
    """Allows collect_data_overlaps to be called from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="command line argument")

    parser.add_argument(
        "--no_inputfile",
        dest="inputfile",
        help="Enables the reading of the pdb ids from the directory",
        action="store_false",
    )
    parser.add_argument(
        "--inputfile",
        dest="inputfile",
        type=bool,
        help="Enables the reading of the pdb ids from txt file",
        default=True,
    )
    
    args = parser.parse_args()
    main(args.inputfile)

if __name__ == "__main__":
    run()
