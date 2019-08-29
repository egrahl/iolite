# coding: utf-8
import os
import os.path
import matplotlib.pyplot as plt
from math import sqrt
import numpy as np
import matplotlib


matplotlib.rcParams['font.sans-serif'] = "Arial"
# Then, "ALWAYS use sans-serif fonts"
matplotlib.rcParams['font.family'] = "sans-serif"


def write_list_pdb_id():
    '''Creates a list of pdb ids based on the PBD ids listed 
    in the file pdb_id_list.txt (all pdb_ids).

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
    list_pdb_id.sort()
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



def plot_histogram(sigma,no_bins,label):
    plt.hist(sigma, bins=no_bins)
    
    plt.title('Histogram ' + label +' values',fontsize=18)
    plt.xlabel(label+" (°)",fontsize=12)
    plt.ylabel("Occurence",fontsize=1)
    plt.show()

def plot_boxplot(sigma,label):
    plt.boxplot(sigma,labels=[label])
    plt.title("Boxplot for distribution of " + label,fontsize=18)
    plt.ylabel(label,fontsize=12)
    plt.show()

def border_values(sigma_list):
    low=np.percentile(sigma_list,20)
    medium=np.percentile(sigma_list,80)
    
    borders=[low,medium]
    return borders


def main():
    no_bins=50        
    sigma_b, sigma_m = read_sigma_from_txt("/dls/mx-scratch/gwx73773/data_files/sigma_values.txt")


    #plot histograms
    plot_histogram(sigma_b,no_bins,r'$\sigma_b$')
    plot_histogram(sigma_m,no_bins,r'$\sigma_m$')
    
    #plot boxplots
    # plot_boxplot(sigma_b,r'$\sigma_b$')
    # plot_boxplot(sigma_m,r'$\sigma_m$')

    
    
    
if __name__ == "__main__":
    main()
