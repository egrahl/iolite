import os
import os.path
from src.iolite.sigma.sigma_values import read_sigma_from_txt
import scipy
import scipy.stats
from scipy.stats import percentileofscore


class SigmaClassifier:
    """
    This class reads out sigma values from dials.integrate.log files, classifies
    and ranks these values, and writes an outputfile containing these labels.
    
    Requires pre-processing with xia2.
    """
    def __init__(self,input_directory,output_directory):
        """Initialising the classifier with input and output directory.
        
        :param str input_directory: path to input directory (default: cwd)
        :param str output_directory: path to output directory (default: cwd)
        """
        self.input_directory=input_directory
        self.output_directory=output_directory

    def extract_sigma_values(self, path):
        """
        This function extracts the sigma values from the dials.integrate.log 
        file that is in the directory.

        :param str path: path to the directory containing the log file

        :returns: sigma_b and sigma_m
        """
        dest_file=os.path.join(path, "DEFAULT/NATIVE/SWEEP1/integrate/dials.integrate.log")
        
        #checking if log file was copied and is therefore directly in directory
        entries=os.listdir(path)
        for e in entries:
            if e=="dials.integrate.log":
                dest_file="dials.integrate.log"
        
        #read sigma values from log file
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
        """This function ranks the sigma value according to the distribution
        in sigma_values.txt and labels the dataset.
        
        :param float sigma: sigma value of dataset
        :param list sigma_list: list containg reference sigma values

        :returns: rank and label of dataset
        """
        #get rank
        rank = percentileofscore(sigma_list, sigma)
        
        #get label
        if rank<20:
            label="low"
        elif rank<80:
            label="medium"
        else:
            label="high"

        return label, rank

    def write_output_file(self, label_b,rank_b, label_m, rank_m):
        """This function writes an outputfile label_sigma.txt in the
        output directory.

        :param str label_b: label for sigma b value
        :param float rank_b: rank of sigma b value
        :param str label_m: label for sigma m value
        :param float rank_m: rank of sigma m value
        """

        labels = [label_b,rank_b, label_m,rank_m]
        text = ["Classification of sigma b: ", "Rank of sigma b: ", "Classification of sigma m: ", "Rank of sigma m: "]
        name_outfile=self.output_directory+"/label_sigma.txt"
        with open(name_outfile, "w") as outfile:
            for t, l in zip(text, labels):
                outfile.write("%s %s\n" % (t, l))

    

    def main(self):
        """
        The main program of SigmaClassifier that extracts the sigma
        values from the log file, classifies them and writes an
        output file with the labels.

        :returns: list containing the classifications
        """
        path=self.input_directory
        sigma_b_list, sigma_m_list = read_sigma_from_txt(
            "/dls/science/users/gwx73773/iolite/share/sigma_values.txt"
        )
       
        sigma_b, sigma_m = self.extract_sigma_values(path)

        #classify sigma values
        label_b, rank_b = self.classify_sigma(sigma_b, sigma_b_list)
        label_m, rank_m = self.classify_sigma(sigma_m, sigma_m_list)
        
        #write output file
        self.write_output_file(label_b,rank_b,label_m,rank_m)

        #write classifications to list
        data=[label_b,rank_b,label_m,rank_m]

        return data


def run():
    """Allows classify_sigma to be called from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="command line argument")

    parser.add_argument(
        "--input_directory",
        dest="input_directory",
        type=str,
        help="Path to the input directory.",
        default=os.getcwd(),
    )
    parser.add_argument(
       "--output_directory",
        dest="output_directory",
        type=str,
        help="Path to the output directory.",
        default=os.getcwd(),
    )

    args = parser.parse_args()
    sigma_classifier = SigmaClassifier(args.input_directory,args.output_directory)
    sigma_classifier.main()


if __name__ == "__main__":
    run()
