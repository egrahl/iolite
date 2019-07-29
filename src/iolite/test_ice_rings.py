import os
import os.path
import numpy as np

from ice_rings import IceRingClassifier

def list_from_txt(name):
    filein= open(name,"r")

    list_dataset=[]
    for line in filein.readlines():
        if not line.strip():
            continue
        else: list_dataset.append(line.rstrip())
    filein.close()
    
    return list_dataset



def main():

    list_PDB_id = list_from_txt("data_sets.txt")
    list_present = list_from_txt("ice_ring_present.txt")
    
    for i in list_present:
        i= float(i)
        i=int(i)
    print(type(list_present[0]))
    list_detected = [0]*len(list_PDB_id)
    os.chdir("/dls/mx-scratch/gwx73773/data_files")
    count=0
    for id in list_PDB_id:
        
        for file in os.listdir(os.path.join(os.getcwd(),id)):    
            if file.endswith("table.txt"):
                os.chdir(id)
                ice_ring_classifier=IceRingClassifier(0.072,0.0765,0.190,0.205,0.265,0.2755,"table.txt",False)
                ice_ring_detected = ice_ring_classifier.main()
                list_detected[list_PDB_id.index(id)]= ice_ring_detected 
                #os.system("dials.image_viewer imported.expt")
                #ice_ring_present= input("Ice-rings present? [0/1]: ")
                #list_present[list_PDB_id.index(id)]=int(ice_ring_present)
                

        os.chdir("/dls/mx-scratch/gwx73773/data_files")
        count +=1
        print(count, id)
        
    output_file= input("Name of output file: ")
    with open(output_file, "w") as outfile:
        for p, d in zip(list_present, list_detected):
            outfile.write("%s, %i\n" % (p, d))       

    

if __name__ == "__main__":
    main()