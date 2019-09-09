"""sigma_values.py collects the sigma values from a text file,
plots them as histograms and boxplots and calulates the boundaries
for the classification of other datasets. Additionally, it contains 
a function that collects the sigma values from the dials.integrate.log
files of several datasets.

"""
# coding: utf-8
import os
import os.path
import matplotlib.pyplot as plt
from math import sqrt
import numpy as np
import matplotlib


matplotlib.rcParams["font.sans-serif"] = "Arial"
# Then, "ALWAYS use sans-serif fonts"
matplotlib.rcParams["font.family"] = "sans-serif"


def write_list_pdb_id():
    """Creates a list of pdb ids based on the PBD ids listed 
    in the file pdb_id_list.txt (all pdb_ids).

    :returns: list_pdb_id
    """
    filein = open("PDB_id_list.txt", "r")

    list_pdb_id_d = []
    #read from txt file
    for line in filein.readlines():
        if not line.strip():
            continue
        else:
            list_pdb_id_d.append(line.rstrip())
    filein.close()
    list_pdb_id = list(set(list_pdb_id_d))
    list_pdb_id.sort()
    return list_pdb_id


def write_list_sigma(list_pdb_id):
    """
    This function reads sigma values from dials.integrate.log files
    and saves them in lists.

    :param list list_pdb_id: list of pdb_ids the sigma values are collected from
    
    :returns: list of sigma b values and list of sigma m values
    """
    #prepare lists
    list_sigma_b = []
    list_sigma_m = []
    path=os.getcwd()
    #loop through datasets
    for id in list_pdb_id:
        for file in os.listdir(os.path.join(os.getcwd(), id)):
            if file.endswith("dials.integrate.log"):
                os.chdir(id)
                with open("dials.integrate.log") as f:
                    f = f.readlines()
                #search sigma values in log file
                for line in f[:200]:

                    index_b = line.find("sigma b")
                    index_m = line.find("sigma m")
                    #add sigma values to lists
                    if index_b > (-1):
                        tokens = line.split(" ")
                        list_sigma_b.append(float(tokens[3]))

                    if index_m > (-1):
                        tokens = line.split(" ")
                        list_sigma_m.append(float(tokens[3]))

        os.chdir(path)

    return list_sigma_b, list_sigma_m


def read_sigma_from_txt(filename):
    """
    This function reads sigma values from a txt file 
    and saves them in lists.

    :param str filename: name of the txt file containing the sigma values

    :returns: the lists of the sigma values
    """
    #prepare lists
    sigma_b = []
    sigma_m = []

    #read sigma values from txt file
    for line in open(filename, "r").readlines():
        b, m = map(float, line.split(","))
        sigma_b.append(b)
        sigma_m.append(m)

    return sigma_b, sigma_m


def plot_histogram(sigma, no_bins, label):
    """
    This function plots a histogram of the distribution of sigma values.

    :param list sigma: the list of the sigma values
    :param int no_bins: number of bins of histogram
    :param str label: label of the histogram plot (sigma b or m)
    """
    plt.hist(sigma, bins=no_bins)

    plt.title("Distribution " + label + " values", fontsize=24)
    plt.xlabel(label + " (°)", fontsize=16)
    plt.ylabel("Occurence", fontsize=16)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.show()


def plot_boxplot(sigma, label):
    """
    This function plots a boxplot of the distribution of the sigma values.

    :param list sigma: the list of the sigma values
    :param str label: label of the histogram plot (sigma b or m)
    """
    plt.boxplot(sigma, labels=[label])
    plt.title("Boxplot for distribution of " + label, fontsize=18)
    plt.ylabel(label, fontsize=12)
    plt.show()


def boundary_values(sigma_list):
    """
    This function calculates the boundary values for the classification 
    based on a list of refernece sigma values.

    :param list sigma_list: list of reference sigma_values

    :returns: list of boundary values for classification
    """
    low = np.percentile(sigma_list, 20)
    medium = np.percentile(sigma_list, 80)

    boundaries = [low, medium]
    return boundaries


def write_boundaries_to_txt(filename, sigma_b_boundaries, sigma_m_boundaries):
    """
    This function writes the boundary values for the classification of the sigma
    values to a text file.

    :param str filename: name of the output file
    :param list sigma_b_boundaries: list containing the sigma b boundary values
    :param list sigma_m_boundaries: list containing the sigma m boundary values
    """
    with open(filename, "w") as outfile:
        for b, m in zip(sigma_b_boundaries, sigma_m_boundaries):
            outfile.write("%f, %f \n" % (b, m))


def main(no_bins):
    """
    This is the main function of sigma_values.py.

    :param int no_bins: number of bins for the histogram (default: 50)

    """
    sigma_b, sigma_m = read_sigma_from_txt(
        "/dls/science/users/gwx73773/iolite/share/sigma_values.txt"
    )
    #calculate boundary values
    sigma_b_boundaries = boundary_values(sigma_b)
    sigma_m_boundaries = boundary_values(sigma_m)
    #write_boundaries_to_txt("/dls/science/users/gwx73773/iolite/share/sigma_boundaries.txt",sigma_b_boundaries,sigma_m_boundaries)

    # plot histograms
    plot_histogram(sigma_b,no_bins,r'$\sigma_b$')
    plot_histogram(sigma_m,no_bins,r'$\sigma_m$')

    # plot boxplots
    plot_boxplot(sigma_b,r'$\sigma_b$')
    plot_boxplot(sigma_m,r'$\sigma_m$')

def run():
    """Allows sigma_values to be called from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="command line argument")

    parser.add_argument(
        "--num_bins",
        dest="no_bins",
        type=int,
        help="The number of bins of the histograms.",
        default=50,
    )
    
    args = parser.parse_args()
    main(args.no_bins)

if __name__ == "__main__":
    run()
