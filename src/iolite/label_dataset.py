import os
from os.path import basename
from prettytable import PrettyTable
from iolite.classification.classify_sigma import SigmaClassifier
from iolite.classification.classify_overlaps import OverlapClassifier
from iolite.ice_ring.ice_rings import IceRingClassifier

class DatasetLabeller:
    """This class labels datasets with regard to ice-rings, overlapping
    spots and mosaicity. Additionally, if given a list of directories to 
    classify, it classifies each dataset and writes txt files containing 
    the classifications of all datasets in the list.
    """
    def __init__(self,ice_ring_label,multiple_datasets):
        """
        Initializing the dataset labeller object.

        :param str ice_ring_label: the name of the txt file containing 
                                   the classification of ice-rings
                                   (default= label_ice_rings.txt)
        :param bool multiple_datasets: boolean that decides if multiple
                                       datasets are classified (default=True)
        """
        self.ice_ring_label=ice_ring_label
        self.multiple_datasets=multiple_datasets

       

    def list_from_txt(self,name):
        """
        This function reads the lines from a text file and puts them in a list,
        in this context it reads in the pdb ids.

        :param str name: filename of the txt file containing the list

        :returns: list with pdb_ids
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

    def read_data(self,inputfile,num_entries):
        """
        This function reads the data from a txt file that contains
        the classification of the dataset.

        :param str inputfile: txt file containing the classification
        :param int num_entries: number of entries in the label file

        :returns: list containing the classification data
        """
        data=[]
        try:
            with open(inputfile,"r") as infile:
                for line in infile.readlines():
                    tokens=line.split(":")
                    try:
                        #format floats
                        data.append(str(round(float(tokens[1].strip()),2)))
                    except:
                        data.append(tokens[1].strip())
                    
        except IOError:
            #in case the file does not exist
            data=["---"]*num_entries
        
        return data

    def write_output_file(self,filename,table_txt):
        """
        This function writes a text file with the classification of all 
        classified datasets.

        :param str filename: name of output file
        :param str table_txt: table containing the classifications
        """
        with open(filename,"w") as outfile:
            outfile.write(table_txt)

    def write_pdb_id_l_directory(self):
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

    def main(self):
        """The main function of DatasetLabeller where either on or multiple 
        datasets can be classified.
        """

        path=os.getcwd()

        #classification of multiple datasets
        if self.multiple_datasets:
            pdb_id_l=self.write_pdb_id_l_directory()
            
            #prepare tables
            headers_table_ir=["PDB_id","Ice-rings","No. ice-rings","Strength","Sharpness"]
            table_ir=PrettyTable(headers_table_ir)
            headers_table_sigma=["PDB_id","sigma b","Rank sigma b","sigma m","Rank sigma m"]
            table_sigma=PrettyTable(headers_table_sigma)
            headers_table_overlap_pixel=["PDB_id","total(pixel)","Rank total(pixel)","fg(pixel)","Rank fg(pixel)","bg(pixel)","Rank bg(pixel)","bg/fg (pixel)","Rank bg/fg(pixel)"]
            table_overlap_pixel=PrettyTable(headers_table_overlap_pixel)
            headers_table_overlap_reflection=["PDB_id","total(refl.)","Rank total(refl.)","fg(refl.)","Rank fg(refl.)","bg(refl.)","Rank bg(refl.)","bg/fg (refl.)","Rank bg/fg(refl.)"]
            table_overlap_reflection=PrettyTable(headers_table_overlap_reflection)

            #classify each dataset
            for id in pdb_id_l:
                os.chdir(id)
                #prepare classifiers
                sigma_classifier=SigmaClassifier(os.getcwd(),os.getcwd())
                overlap_classifier_pixel=OverlapClassifier(False,os.getcwd(),os.getcwd())
                overlap_classifier_refl=OverlapClassifier(True,os.getcwd(),os.getcwd())
                ice_ring_classifier=IceRingClassifier("table.txt",False)

                #write rows for overall tables
                try:
                    sigma_data=[id]+sigma_classifier.main()
                except:
                    sigma_data=[id]+["---"]*4

                try:
                    overlap_p_data=[id]+overlap_classifier_pixel.main()
                except: 
                    overlap_p_data=[id]+["---"]*8

                try:
                    overlap_r_data=[id]+overlap_classifier_refl.main()
                except:
                    overlap_r_data=[id]+["---"]*8

                try:
                    ice_ring_classifier.main()
                    ice_ring_data=[id]+self.read_data(self.ice_ring_label,4)
                except:
                    ice_ring_data=[id]+["---"]*4

                #add rows to tables
                table_ir.add_row(ice_ring_data)
                table_sigma.add_row(sigma_data)
                table_overlap_pixel.add_row(overlap_p_data)
                table_overlap_reflection.add_row(overlap_r_data)

                os.chdir(path)

            
            #write tables to strings so they can be written in txt file 
            table_ir_str=table_ir.get_string()
            table_sigma_str=table_sigma.get_string()
            table_overlap_pixel_str=table_overlap_pixel.get_string()
            table_overlap_reflection_str=table_overlap_reflection.get_string()   
                
            # write outputfiles
            self.write_output_file("table_ice_ring_classification.txt",table_ir_str)
            self.write_output_file("table_sigma_classification.txt",table_sigma_str)
            self.write_output_file("table_overlap_pixel_classification.txt",table_overlap_pixel_str)
            self.write_output_file("table_overlap_reflection_classification.txt",table_overlap_reflection_str)

        #classification of one dataset
        else:
            #prepare classifiers
            sigma_classifier=SigmaClassifier(os.getcwd(),os.getcwd())
            overlap_classifier_pixel=OverlapClassifier(False,os.getcwd(),os.getcwd())
            overlap_classifier_refl=OverlapClassifier(True,os.getcwd(),os.getcwd())
            ice_ring_classifier=IceRingClassifier("table.txt",False)
            
            #classify the dataset
            try:
                sigma_classifier.main()
            except:
                print("The dataset cannot be classified, run xia2 first!")

            try:
                overlap_classifier_pixel.main()
            except: 
                print("The dataset cannot be classified, run overlapping_spots --run_pixel first!")

            try:
                overlap_classifier_refl.main()
            except:
                print("The dataset cannot be classified, run overlapping_spots first!")

            try:
                ice_ring_classifier.main()   
            except:
                print("The dataset cannot be classified, run radial_average_bg first!")




def run():
    """Allows label_dataset to be called from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="command line argument")

    parser.add_argument(
        "--ice_ring_label",
        dest="ice_ring_label",
        type=str,
        help="The name of the file containing the ice-ring label",
        default="label_ice_rings.txt",
    )
    parser.add_argument(
        "--multiple_datasets",
        dest="multiple_datasets",
        type=bool,
        help="The boolean that decides if multiple datasets should be classified.",
        default=True,
    )
    parser.add_argument(
        "--single_dataset",
        dest="multiple_datasets",
        help="Sets multiple_datasets to false.",
        action='store_false',
    )
    args = parser.parse_args()
    dataset_labeller = DatasetLabeller(args.ice_ring_label,args.multiple_datasets)
    dataset_labeller.main()


if __name__ == "__main__":
    run()
