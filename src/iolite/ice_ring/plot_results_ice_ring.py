"""
plot_results_ice_rings is a program that can analyse the performance of the
IceRingClassifier. It takes the results ("results_number.txt") of the 
program test_ice-rings.py and calculates the values of the confusion matrix.
Additionally, it can produce plots that illustrate the performance of the 
classifier and a pie chart plot that shows the distribution of ice-rings over
the datasets.   
"""



import matplotlib.pyplot as plt
import numpy as np
import matplotlib

#the default sans-serif font is Arial
matplotlib.rcParams["font.sans-serif"] = "Arial"
# ALWAYS use sans-serif fonts
matplotlib.rcParams["font.family"] = "sans-serif"


def lists_from_txt(name):
    """
    This function extracts the columns in the results file
    and writes them as lists.

    :param str name: name of the results file

    :returns: lists of the actual labels of the dataset,
              the labels given by the ice-ring classifier,
              label if there are strong ice-rings
    """
    filein = open(name, "r")

    #prepare lists
    ir_present = []
    ir_detected = []
    strong_rings = []

    #read lists from the results file
    for line in filein.readlines():
        ir_p, ir_d, count_ir, strong = map(int, line.split(","))
        ir_present.append(ir_p)
        ir_detected.append(ir_d)
        strong_rings.append(strong)

    return ir_present, ir_detected, strong_rings


def bar_chart_conf_m(n_tp, n_tn, n_fp, n_fn):
    """
    This function plots the values of the confusion matrix as 
    a bar chart.

    :param int n_tp: number of true positives
    :param int n_tn: number of true negatives
    :param int n_fp: number of false positives
    :param int n_fn: number of false negatives
    """
    results = [n_tp, n_tn, n_fp, n_fn]
    x = np.arange(len(results))

    plt.bar(x, results)
    plt.xticks(
        x, ("true positive", "true negative", "false positive", "false negative")
    )
    plt.title("Classification results")
    plt.show()


def pie_chart_conf_m(tp, tn, fp, fn):
    """
    This function plots the values of the confusion matrix as 
    a pie chart.

    :param int tp: number of true positives
    :param int tn: number of true negatives
    :param int fp: number of false positives
    :param int fn: number of false negatives
    """
    results = [tp, tn, fp, fn]
    labels = "true positives", "true negatives", "false positives", "false negatives"

    fig1, ax1 = plt.subplots()
    ax1.pie(results, labels=labels, autopct="%1.1f%%", shadow=False, startangle=135)
    ax1.axis("equal")

    plt.show()


def pie_chart_strong_rings(tp, tn, fp, fn, sr):
    """
    This function plots the distribution of ice-rings over
    the 148 processed datasets as a pie chart.

    :param int tp: number of true positives
    :param int tn: number of true negatives
    :param int fp: number of false positives
    :param int fn: number of false negatives
    :param int sr: number of datasets with strong ice-rings
    """
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))

    non_detected = tn + fp
    weak_rings = tp + fn - sr
    data = [non_detected, sr, weak_rings]
    labels = ["no ice-rings", "strong ice-rings", "weak ice-rings"]
    explode = (0, 0.1, 0)

    def func(pct, allvals):
        absolute = int(pct / 100.0 * np.sum(allvals))
        return "{:.1f}%\n({:d} datasets)".format(pct, absolute)

    wedges, texts, autotexts = ax.pie(
        data, autopct=lambda pct: func(pct, data), textprops=dict(color="w")
    )

    ax.legend(wedges, labels, loc="center left",framealpha=0, bbox_to_anchor=(1, 0, 0.5, 1), fontsize=14)

    plt.setp(autotexts, size=12, weight="bold")

    ax.set_title("Distribution of ice-rings over datasets", fontsize=24)

    plt.show()
    


def bar_chart_stats(tp, tn, fp, fn):
    """
    This function calculates performance parameters of the 
    IceRingClassifier and plots them as a bar chart.

    :param int tp: number of true positives
    :param int tn: number of true negatives
    :param int fp: number of false positives
    :param int fn: number of false negatives
    """
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    tp_rate = tp / (tp + fn)
    fp_rate = fp / (fp + tn)
    specificity = 1 - fp_rate
    precision = tp / (tp + fp)
    prevalence = (tp + fn) / (tp + tn + fp + fn)

    data = [accuracy, tp_rate, specificity, precision]
    x = np.arange(len(data))

    plt.bar(x, data)
    plt.gca().set_yticklabels(
        ["{:.0f}%".format(x * 100) for x in plt.gca().get_yticks()]
    )
    plt.xticks(
        x, ("Accuracy", "True positive rate", "Specificity", "Precision"), fontsize=14
    )
    plt.title("Performance of ice-ring classifier", fontsize=24)
    plt.show()


def read_PDB_id():
    """This function reads the pdb ids from the file datasets.txt and writes them 
    to a list.
    
    :returns: list of pdb_ids
    """
    filein = open("/dls/mx-scratch/gwx73773/data_files/data_sets.txt", "r")
    pdb_ids = []
    for line in filein.readlines():
        if not line.strip():
            continue
        else:
            pdb_ids.append(line.rstrip())
    filein.close()

    return pdb_ids


def write_outfile(name, number, list):
    """
    This function writes a list to a text file.

    :param str name: name of the outputfile
    :param int number: number of the outputfile
    :param list list: the list that will be written into the output file
    """
    outfile_name = name + "_" + number + ".txt"
    with open(outfile_name, "w") as outfile:
        for l in list:
            outfile.write("%s\n" % l)


def main():
    """
    The main function of plot_results_ice_ring.py
    """
    #get number of attempt to open correct results file
    number = input("Number of attempt: ")
    input_file = "results_" + number + ".txt"

    #get data from results file
    ir_present, ir_detected, strong_rings = lists_from_txt(input_file)
    
    #prepare counts for values of confusion matrix
    n_tp = 0
    n_tn = 0
    n_fp = 0
    n_fn = 0
    n_sr = 0

    #read inlist of pdb_ids
    pdb_ids = read_PDB_id()
    
    #prepare lists for confusion matrix and strong rings (will hold pdb_ids)
    list_fn = []
    list_fp = []
    list_tp = []
    list_tn = []
    list_strong_rings = []

    #calculate values of conf. matrix +strong rings, looping through datasets
    for p, d, i, s in zip(ir_present, ir_detected, pdb_ids, strong_rings):
        if s == 1:
            n_sr += 1
            list_strong_rings.append(i)

        if p == 1 and d == 1:
            n_tp += 1
            list_tp.append(i)
        elif p == 1 and d == 0:
            n_fn += 1
            list_fn.append(i)
        elif p == 0 and d == 1:
            n_fp += 1
            list_fp.append(i)
        elif p == 0 and d == 0:
            n_tn += 1
            list_tn.append(i)

    # plot data
    pie_chart_conf_m(n_tp, n_tn, n_fp, n_fn)
    pie_chart_strong_rings(n_tp, n_tn, n_fp, n_fn, n_sr)
    bar_chart_stats(n_tp, n_tn, n_fp, n_fn)

    # print output and write output files
    print("The number of true positives is: ", n_tp)
    print("The number of true negatives is: ", n_tn)
    print("The number of false positives is: ", n_fp)
    print("The number of false negatives is: ", n_fn)

   
    #write output files
    write_outfile("false_positive", number, list_fp)
    write_outfile("false_negative", number, list_fn)
    write_outfile("true_positive", number, list_tp)
    write_outfile("true_negative", number, list_tn)
    write_outfile("strong_rings", number, list_strong_rings)


if __name__ == "__main__":
    main()
