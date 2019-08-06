import os
import os.path
import matplotlib.pyplot as plt
from math import sqrt
def write_list_pdb_id():
    '''Creates a list of pdb ids based on the PBD ids listed in the file pdb_id_list.txt (all pdb_ids).

    :returns: list_pdb_id
    '''
    filein= open("PDB_id_list.txt","r")

    list_pdb_id_d=[]
    for line in filein.readlines():
        if not line.strip():
            continue
        else: list_pdb_id_d.append(line.rstrip())
    filein.close()
    list_pdb_id = list(set(list_pdb_id_d))
    return list_pdb_id


def write_list_sigma(list_pdb_id):
    
    list_sigma_b=[]
    list_sigma_m=[]
   
    for id in list_pdb_id:
        for file in os.listdir(os.path.join(os.getcwd(),id)):     
            if file.endswith("dials.integrate.log"):
                
                os.chdir(id)
                with open("dials.integrate.log") as f:
                    f = f.readlines()

                for line in f[:200]:
                    
                    index_b=line.find('sigma b')
                    index_m=line.find('sigma m')
                    if index_b>(-1):
                        tokens = line.split(' ')
                        list_sigma_b.append(float(tokens[3]))
               
                    if index_m>(-1):
                        tokens = line.split(' ')
                        list_sigma_m.append(float(tokens[3]))

        os.chdir("/dls/mx-scratch/gwx73773/data_files")
       
    return list_sigma_b, list_sigma_m
        
def read_sigma_from_txt(filename):
    sigma_b = []
    sigma_m = []
    for line in open(filename,"r").readlines():
        b, m = map(float, line.split(","))
        sigma_b.append(b)
        sigma_m.append(m)
    return sigma_b, sigma_m


def main():
    no_bins=40           #int(sqrt(len(sigma_b)))
    sigma_b, sigma_m = read_sigma_from_txt("sigma_values.txt")
    plt.hist(sigma_b, bins=no_bins)
    plt.title("Sigma b values")
    plt.show()
    
    plt.hist(sigma_m,bins=no_bins)
    plt.title("Sigma m values")
    plt.show()
if __name__ == "__main__":
    main()