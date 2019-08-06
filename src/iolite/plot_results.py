import matplotlib.pyplot as plt
import numpy as np


def lists_from_txt(name):
    filein = open(name, "r")

    ir_present = []
    ir_detected = []
    strong_rings = []

    for line in filein.readlines():
        ir_p, ir_d, count_ir, strong = map(int, line.split(","))
        ir_present.append(ir_p)
        ir_detected.append(ir_d)
        strong_rings.append(strong)

    return ir_present, ir_detected, strong_rings


def bar_chart_conf_m(n_tp, n_tn, n_fp, n_fn):
    results = [n_tp, n_tn, n_fp, n_fn]
    x = np.arange(len(results))

    plt.bar(x, results)
    plt.xticks(
        x, ("true positive", "true negative", "false positive", "false negative")
    )
    plt.show()


def pie_chart_conf_m(tp, tn, fp, fn):
    results = [tp, tn, fp, fn]
    labels = "true positives", "true negatives", "false positives", "false negatives"

    fig1, ax1 = plt.subplots()
    ax1.pie(results, labels=labels, autopct="%1.1f%%", shadow=False, startangle=135)
    ax1.axis("equal")

    plt.show()


def pie_chart_strong_rings(tp, tn, fp, fn, sr):
    non_detected = tn + fp + fn
    weak_rings = tp + fn - sr
    data = [non_detected, sr, weak_rings]
    labels = "no ice-rings", "strong ice-rings", "weak ice-rings"
    explode = (0, 0.1, 0)
    fig1, ax1 = plt.subplots()
    ax1.pie(
        data,
        labels=labels,
        shadow=False,
        explode=explode,
        labeldistance=1.1,
        startangle=90,
    )
    ax1.axis("equal")
    plt.show()


def bar_chart_stats(tp, tn, fp, fn):
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    tp_rate = tp / (tp + fn)
    fp_rate = fp / (fp + tn)
    specificity = 1 - fp_rate
    precision = tp / (tp + fp)
    prevalence = (tp + fn) / (tp + tn + fp + fn)

    data = [accuracy, tp_rate, specificity, precision]
    x = np.arange(len(data))

    plt.bar(x, data)
    plt.xticks(x, ("accuracy", "true positive rate", "specificity", "precision"))
    plt.show()


def read_PDB_id():
    filein = open("data_sets.txt", "r")
    pdb_ids = []
    for line in filein.readlines():
        if not line.strip():
            continue
        else:
            pdb_ids.append(line.rstrip())
    filein.close()

    return pdb_ids


def write_outfile(name, number, list):
    outfile_name = name + "_" + number + ".txt"
    with open(outfile_name, "w") as outfile:
        for l in list:
            outfile.write("%s\n" % l)


def main():
    number = input("Number of attempt: ")
    input_file = "results_" + number + ".txt"
    ir_present, ir_detected, strong_rings = lists_from_txt(input_file)
    n_tp = 0
    n_tn = 0
    n_fp = 0
    n_fn = 0
    n_sr = 0
    pdb_ids = read_PDB_id()
    list_fn = []
    list_fp = []
    list_tp = []
    list_tn = []
    list_strong_rings = []

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

    print(list_strong_rings)
    print(list_fn)
    print(list_fp)

    write_outfile("false_positive", number, list_fp)
    write_outfile("false_negative", number, list_fn)
    write_outfile("true_positive", number, list_tp)
    write_outfile("true_negative", number, list_tn)
    write_outfile("strong_rings", number, list_strong_rings)


if __name__ == "__main__":
    main()
