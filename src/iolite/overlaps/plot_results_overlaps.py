"""
This program can plot the results of overlapping_spots.py.
It can plot the results of one dataset (command line: --single (default))
as overlaps per resolution bin. Additionally, it can plot the results of 
multiple datasets (command line: --multiple) as histograms and boxplots.
Both overlaps per pixel (command line: --pixel (default)) and per 
shoebox (command line: --shoebox) can be plotted.
"""
# coding: utf-8
import matplotlib.pyplot as plt
import numpy as np
import os
import os.path
import matplotlib
from math import sqrt

#change plotting font to Arial
matplotlib.rcParams["font.sans-serif"] = "Arial"
# Then, "ALWAYS use sans-serif fonts"
matplotlib.rcParams["font.family"] = "sans-serif"


def plot_histogram(list, num_bins, title_plot, xlabel):
    """
    This function plots a histogram of a list according to the given number of 
    bins with a given title and x-label.

    :param list list: list that will be plotted as a histogram
    :param int num_bins: number of bins of histogram
    :param str title_plot: title of the histogram plot
    :param str xlabel: x-label of the plot                    
    """
    plt.hist(list, bins=num_bins)
    plt.title(title_plot, fontsize=24)
    plt.xlabel(xlabel, fontsize=16)
    plt.ylabel("Occurence", fontsize=16)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.show()


def plot_boxplot(list, labels, title_plot, ylabel):
    """
    This function plots a boxplot of a list with a given title and y-label.

    :param list list: list that will be plotted as a boxplot
    :param str labels: label that specifies the kind of overlap
    :param str title_plot: title of the boxplot
    :param str ylabel: y-label of the plot                    
    """
    plt.boxplot(list, labels=labels)
    plt.ylabel(ylabel, fontsize=12)
    plt.title(title_plot, fontsize=18)
    plt.show()


def read_lists_total(filename):
    """
    This function reads lists of the overlap values of multiple 
    datasets. 

    :param str filename: name of the txt file that contains the data

    :returns: lists of total, foreground, background and background/foreground
               overlap
    """
    filein = open(filename, "r")
    
    #prepare lists
    total = []
    fg = []
    bg = []
    bg_fg = []

    #read in the data into lists
    for line in filein.readlines():
        tokens = line.split(",")
        total.append(float(tokens[1]))
        fg.append(float(tokens[2]))
        bg.append(float(tokens[3]))
        bg_fg.append(float(tokens[4].rstrip()))
    filein.close()

    return total, fg, bg, bg_fg


def border_values(overlap_list):
    """
    This function calculates the border values of the overlaps
    for the classification.

    :param list overlap_list: the list containing the overlap data

    :returns: list containing the border values
    """
    low = np.percentile(overlap_list, 25)
    medium = np.percentile(overlap_list, 75)
    high = medium + 1.5 * (medium - low)

    borders = [low, medium, high]
    return borders


def read_lists_resolution(overlap_kind):
    """
    This function reads the overlap data per resolution bins from a txt file.

    :param bool overlap_kind: defines if data for overlap per pixel is read

    :returns: lists of overlap data of total(foreground), total(background), 
              foreground, background, foreground/background,
              background/foreground per resolution bin
    """
    #prepare lists that will hold overlap data
    resolution = []
    total_f = []
    total_b = []
    fg = []
    bg = []
    fg_bg = []
    bg_fg = []

    path = os.getcwd()

    #read data for overlaps per pixel
    if overlap_kind:
        inputfile = "overlap_lists.txt"
        for file in os.listdir(path):
            #get old version of txt filename
            if file == "overlap_lists_corrected.txt":
                inputfile = file
        #read in overlap data from the txt file
        for line in open(inputfile).readlines():
            r, t, f, b, bf = map(float, line.split(","))
            resolution.append(r)
            total_f.append(t)
            fg.append(f)
            bg.append(b)
            bg_fg.append(bf)
        total_b = total_f
        fg_bg = bg_fg
    #read data for overlaps per reflection/shoebox
    else:
        inputfile = "overlap_lists_shoebox.txt"
        #read in overlap data from the txt file
        for line in open(inputfile).readlines():
            r, tf, tb, f, b, fb, bf = map(float, line.split(","))
            resolution.append(r)
            total_f.append(tf)
            total_b.append(tb)
            fg.append(f)
            bg.append(b)
            fg_bg.append(fb)
            bg_fg.append(bf)

    return resolution, total_f, total_b, fg, bg, fg_bg, bg_fg


def plot_overlaps_resolution(resolution, data, title, ylabel):
    """ 
    This function plots a bar chart of overlaps per resolution bin
    with given data, title and y-label.

    :param list resolution: list of resolution data (1/d^2)
    :param list data: list of overlap data per resolution bin
    :param str title: the title of the bar chart
    :param str ylabel: the y-label of the plot
    """
    #get the x-axis in d
    index = np.arange(len(resolution))
    d = list(map(lambda x: "%.2f" % (1 / sqrt(x)), resolution))
    
    plt.bar(index, data)
    plt.xlabel(r"resolution ($\AA$)", fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.yticks(fontsize=8)
    plt.xticks(index, d, fontsize=8, ha="right", rotation=45)
    plt.title(title, fontsize=18)
    plt.show()


def plot_stacked_bar_chart(resolution, bg, fg, bg_fg, pdb_id, ylabel, kind_bf_overlap):
    """
    This function plots a stacked bar chart of the overlaps per resolution bin.

    :param list resolution: list of the resolution data (1/d^2)
    :param list bg: list of background overlaps per resolution bin
    :param list fg: list of foreground overlaps per resolution bin
    :param list bg_fg: list of background/foreground overlaps per resolution bin
    :param str pdb_id: pdb id of the dataset that is plotted
    :param str ylabel: the y-label of the plot
    :param str kind_bf_overlap: the string that specifies which kind of 
                                background/foreground overlap is plotted
    """
    #set x-axislabelling as resolution in d
    index = np.arange(len(resolution))
    d = list(map(lambda x: "%.2f" % (1 / sqrt(x)), resolution))

    p1 = plt.bar(index, bg)
    p2 = plt.bar(index, fg, bottom=bg)
    p3 = plt.bar(index, bg_fg, bottom=np.array(bg) + np.array(fg))

    plt.xlabel(r"resolution ($\AA$)", fontsize=16)
    plt.ylabel(ylabel, fontsize=16)
    plt.yticks(fontsize=12)
    plt.xticks(index, d, fontsize=12, ha="right", rotation=45)
    plt.title(
        "Ratio overlaps against resolution bins \n (total divided into its components) of "
        + pdb_id,
        fontsize=24,
    )
    plt.legend(
        (p1[0], p2[0], p3[0]),
        ("background overlap", "foreground overlap", kind_bf_overlap),framealpha=0
    )
    plt.show()


def get_pdb_id():
    """
    This function gets the pdb-id of the dataset.

    :returns: pdb-id
    """
    path = os.getcwd()
    tokens = path.split("/")
    id = ""
    for t in tokens:
        if t.startswith("DEFAULT"):
            id = tokens[tokens.index(t) - 1]

    return id


def define_label(overlap_kind):
    """
    This function sets the overlap label.

    :param bool overlap_kind: the boolean that determines if the overlap
                              is per pixel or shoebox

    :returns: overlap label
    """
    if overlap_kind:
        ylabel = "overlap ratio per pixel"
    else:
        ylabel = "overlap ratio per shoebox"

    return ylabel


def define_title(overlap_kind):
    """
    This function sets the specification of the title of the plots.

    :param bool overlap_kind: the boolean that determines if the overlap
                              is per pixel or shoebox
    :returns: title
    """
    if overlap_kind:
        title = "per pixel"
    else:
        title = "per shoebox"

    return title


def plot_overall_results(overlap_kind):
    """
    This function plots the results of multiple datasets.

    :param bool overlap_kind: the boolean that determines if the overlap
                              is per pixel or shoebox
    """
    #set name of output file
    if overlap_kind:
        filename = "count_overlaps_pixel.txt"
    else:
        filename = "count_overlaps_shoebox.txt"
    
    #get the data of the overlaps from a txt file
    total, fg, bg, bg_fg = read_lists_total(filename)
    
    #define labels, title, number of resolution bins
    label = define_label(overlap_kind)
    title = define_title(overlap_kind)
    num_bins = len(total)
    
    # plot histograms
    plot_histogram(total, num_bins, "Distribution of total overlaps " + title, label)
    plot_histogram(fg, num_bins, "Distribution of foreground overlap " + title, label)
    plot_histogram(bg, num_bins, "Distribution of background overlaps " + title, label)
    plot_histogram(
        bg_fg,
        num_bins,
        "Distribution of background/foreground overlaps " + title,
        label,
    )

    #prepare data for boxplots
    data = [total, fg, bg, bg_fg]
    labels = ["total", "foreground", "background", "background/foreground"]

    #plot the boxplots
    plot_boxplot(total, ["total"], "Boxplot for total overlaps " + title, label)
    plot_boxplot(fg, ["foreground"], "Boxplot for foreground overlaps " + title, label)
    plot_boxplot(bg, ["background"], "Boxplot for background overlaps " + title, label)
    plot_boxplot(
        bg_fg,
        ["background/foreground"],
        "Boxplot for background/foreground overlaps " + title,
        label,
    )
    plot_boxplot(data, labels, "Boxplots for all overlaps " + title, label)


def plot_results_dataset(overlap_kind):
    """
    This function plots the results of one datasets.

    :param bool overlap_kind: the boolean that determines if the overlap
                              is per pixel or shoebox
    """
    #get pdb id, label, title
    pdb_id = get_pdb_id()
    label = define_label(overlap_kind)
    title = define_title(overlap_kind)

    #get data from the txt file
    resolution, total_f, total_b, fg, bg, fg_bg, bg_fg = read_lists_resolution(
        overlap_kind
    )

    #plot overlaps per resolution bin
    plot_overlaps_resolution(
        resolution,
        fg,
        "Ratio of foreground overlap " + title + " against resolution of " + pdb_id,
        label,
    )
    plot_overlaps_resolution(
        resolution,
        bg,
        "Ratio of background overlap " + title + " against resolution of " + pdb_id,
        label,
    )
    plot_overlaps_resolution(
        resolution,
        bg_fg,
        "Ratio of background/foreground overlap "
        + title
        + " against resolution of "
        + pdb_id,
        label,
    )
    plot_stacked_bar_chart(
        resolution, bg, fg, bg_fg, pdb_id, label, "background/foreground overlap"
    )
    #for overlaps per pixel
    if overlap_kind:
        plot_overlaps_resolution(
            resolution,
            total_f,
            "Ratio of total overlap " + title + " against resolution of " + pdb_id,
            label,
        )
    #for overlaps per shoebox
    else:
        plot_overlaps_resolution(
            resolution,
            total_f,
            "Ratio of total overlap "
            + title
            + " (considering foreground/background)\n against resolution of "
            + pdb_id,
            label,
        )
        plot_overlaps_resolution(
            resolution,
            total_b,
            "Ratio of total overlap "
            + title
            + " (considering background/foreground)\n  against resolution of "
            + pdb_id,
            label,
        )
        plot_overlaps_resolution(
            resolution,
            fg_bg,
            "Ratio of foreground/background overlap "
            + title
            + " against resolution of "
            + pdb_id,
            label,
        )
        plot_stacked_bar_chart(
            resolution, bg, fg, fg_bg, pdb_id, label, "foreground/background overlap"
        )


def main(single_dataset,pixel):
    """
    The main function of plot_results_overlaps.

    :param bool single_dataset: if True, results for one dataset are plotted,
                                if False, results of multiple datasets are 
                                plotted (default=True)
    :param bool pixel: if True, results per pixel are plotted,
                       if False, results per shoebox are plotted (default=True)
    """
    if single_dataset:
        plot_results_dataset(pixel)
    else:
        plot_overall_results(pixel)


def run():
    """Allows plot_results_overlaps to be called from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="command line argument")

    parser.add_argument(
        "--single",
        dest="single_dataset",
        type=bool,
        help="The boolean that decides that the data of one dataset is plotted.",
        default=True,
    )
    parser.add_argument(
        "--multiple",
        dest="single_dataset",
        help="Sets single_dataset to false.",
        action='store_false',
       
    )
    parser.add_argument(
        "--pixel",
        dest="pixel",
        type=bool,
        help="The boolean that decides that the results per pixel is plotted.",
        default=True,
    )
    parser.add_argument(
        "--shoebox",
        dest="pixel",
        help="Sets pixel to false.",
        action='store_false',
       
    )



    args = parser.parse_args()
    main(args.single_dataset,args.pixel)
if __name__ == "__main__":
    run()
