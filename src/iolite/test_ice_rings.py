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
    list_present_string = list_from_txt("ice_ring_present.txt")
    list_present=[0]*len(list_present_string)
    for i in range(len(list_present_string)):
        if list_present_string[i]=='1':
            list_present[i]=1

    list_detected = [0]*len(list_PDB_id)
    list_count = [0]*len(list_PDB_id)
    list_strong_count=[0]*len(list_PDB_id)
    count=0
    count_strong_rings=0
    for id in list_PDB_id:
        print(count, id)
        for file in os.listdir(os.path.join(os.getcwd(),id)):     
            if file.endswith("table.txt"):
                os.chdir(id)
                ice_ring_classifier=IceRingClassifier("table.txt",False)
                ice_ring_detected, ice_ring_count, strength, peaked = ice_ring_classifier.main()
                
                list_detected[list_PDB_id.index(id)]= ice_ring_detected 
                list_count[list_PDB_id.index(id)]=ice_ring_count
                list_strong_count[list_PDB_id.index(id)]=strength
                #os.system("dials.image_viewer imported.expt")
                #ice_ring_present= input("Ice-rings present? [0/1]: ")
                #list_present[list_PDB_id.index(id)]=int(ice_ring_present)
                if strength==1:
                    count_strong_rings +=1

        os.chdir("/dls/mx-scratch/gwx73773/data_files")
        count +=1
        
    print(count_strong_rings)   
    output_file= input("Name of output file: ")
    # with open(output_file,"w") as outfile:
    #     for id, res,prom,wid, desc in zip(id_l,resolutions,prominences,widths,descriptions):
    #         outfile.write("%s,%f, %f,%f,%s\n" % (id,res,prom,wid,desc))


    with open(output_file, "w") as outfile:
        for p, d, c,s in zip(list_present, list_detected, list_count,list_strong_count):
            outfile.write("%i, %i, %i, %i\n" % (p,d,c,s))       

    
    

if __name__ == "__main__":
    main()