import os
import os.path
from sigma_values import read_sigma_from_txt
import scipy
import scipy.stats
from scipy.stats import percentileofscore


class SigmaClassifier:
    def __init__(self):
        pass

 
    def extract_sigma_values(self, path):
        dest_file=os.path.join(path, "DEFAULT/NATIVE/SWEEP1/integrate/dials.integrate.log")
        entries=os.listdir(path)
        for e in entries:
            if e=="dials.integrate.log":
                dest_file="dials.integrate.log"
        with open(
            dest_file
        ) as f:
            f = f.readlines()

            for line in f[:200]:

                index_b = line.find("sigma b")
                index_m = line.find("sigma m")
                if index_b > (-1):
                    tokens = line.split(" ")
                    sigma_b = float(tokens[3])

                if index_m > (-1):
                    tokens = line.split(" ")
                    sigma_m = float(tokens[3])

        return sigma_b, sigma_m

    def classify_sigma(self, sigma, sigma_list):
        rank = percentileofscore(sigma_list, sigma)
        if rank<20:
            label="low"
        elif rank<80:
            label="medium"
        else:
            label="high"

        return label, rank

    def write_output_file(self, label_b,rank_b, label_m, rank_m):
        labels = [label_b,rank_b, label_m,rank_m]
        text = ["Classification of sigma b: ", "Rank of sigma b: ", "Classification of sigma m: ", "Rank of sigma m: "]
        with open("label_sigma.txt", "w") as outfile:
            for t, l in zip(text, labels):
                outfile.write("%s %s\n" % (t, l))

    

    def main(self):
        path=os.getcwd()
        sigma_b_list, sigma_m_list = read_sigma_from_txt(
            "/dls/science/users/gwx73773/iolite/share/sigma_values.txt"
        )
       
        sigma_b, sigma_m = self.extract_sigma_values(path)
        label_b, rank_b = self.classify_sigma(sigma_b, sigma_b_list)
        label_m, rank_m = self.classify_sigma(sigma_m, sigma_m_list)
        self.write_output_file(label_b,rank_b,label_m,rank_m)
        return label_b, rank_b, label_m, rank_m


def run():
    """Allows classify_sigma to be called from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="command line argument")

    sigma_classifier = SigmaClassifier()
    sigma_classifier.main()


if __name__ == "__main__":
    run()
