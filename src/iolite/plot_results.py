import matplotlib.pyplot as plt
import numpy as np 

def lists_from_txt(name):
    filein=open(name,"r")

    ir_present = []
    ir_detected = []

    for line in filein.readlines():
        tokens = line.split(",")
        ir_present.append(float(tokens[0]))
        ir_detected.append(float(tokens[1].rstrip()))
    filein.close()
    return ir_present, ir_detected

def bar_chart(n_tp,n_tn,n_fp,n_fn):
    results=[n_tp,n_tn,n_fp,n_fn]
    x = np.arange(4)

    plt.bar(x, results)
    plt.xticks(x, ('true positive', 'true negative', 'false positive', 'false negative'))
    plt.show()

def read_PDB_id():
    filein=open("data_sets.txt","r")
    pdb_ids = []
    for line in filein.readlines():
        if not line.strip():
            continue
        else: pdb_ids.append(line.rstrip())
    filein.close()
    
    return pdb_ids

def write_outfile(name,number,list):
    outfile_name= name+"_"+number+".txt"
    with open(outfile_name, "w") as outfile:
        for l in list:
            outfile.write("%s\n" % l)
      


def main():
    number = input("Number of attempt: ")
    input_file = "results_"+number+".txt"
    ir_present, ir_detected = lists_from_txt(input_file)
    n_tp=0
    n_tn=0
    n_fp=0
    n_fn=0
    pdb_ids = read_PDB_id()
    list_fn= []
    list_fp = []
    list_tp=[]
    list_tn=[]

    for p, d, i in zip(ir_present,ir_detected,pdb_ids):
        if p==1 and d==1:
            n_tp +=1
            list_tp.append(i)
        elif p==1 and d==0:
            n_fn +=1
            list_fn.append(i)
        elif p==0 and d==1:
            n_fp +=1
            list_fp.append(i)
        elif p==0 and d==0:
            n_tn +=1
            list_tn.append(i)
    print("The number of true positives is: ",n_tp)
    print("The number of true negatives is: ",n_tn)
    print("The number of false positives is: ",n_fp)
    print("The number of false negatives is: ",n_fn)
    bar_chart(n_tp,n_tn,n_fp,n_fn)

    
    print(list_fn)
    print(list_fp)

    write_outfile("false_positive",number,list_fp)
    write_outfile("false_negative",number,list_fn)
    write_outfile("true_positive",number,list_tp)
    write_outfile("true_negative",number,list_tn)

   

    



if __name__ == "__main__":
    main()