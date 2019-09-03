import os
import os.path
from scipy.stats import percentileofscore


class OverlapClassifier:

    def __init__(self,shoebox_count,input_directory,output_directory):
        """Initialising an overlap classifier.

        :param bool shoebox_count: Boolean that decides if the overlaps per
                                shoebox should be classified. (default=True)
        :param str input_directory: path to input directory (default=cwd)
        :param str output_directory: path to output directory (default=cwd)
        """
        self.shoebox_count=shoebox_count
        self.input_directory=input_directory
        self.output_directory=output_directory 

    def classify_overlap(self,overlap,overlap_list):
        """This function ranks the overlap ratio according to the distribution
        in the inputfile and labels the dataset.
        
        :param float overlap: overlap ratio
        :param list overlap_list: list containg reference overlap ratios

        :returns: rank and label of dataset
        """
        #get rank
        rank = percentileofscore(overlap_list, overlap)
        
        #get label
        if rank<20:
            label="low"
        elif rank<80:
            label="medium"
        else:
            label="high"

        return label, rank
    
    def write_output_file(self,output_name,label_t,rank_t, label_fg,rank_fg, label_bg,rank_bg,label_bg_fg, rank_bg_fg):
        """This function writes an outputfile in the
        output directory.

        :param str label_t: label for total overlaps
        :param float rank_t: rank of total overlaps
        :param str label_fg: label for foreground overlap
        :param float rank_fg: rank of foreground overlap
        :param str label_bg: label for background overlap
        :param float rank_bg: rank of background overlap
        :param str label__bg_fg: label for background/foreground overlap
        :param float rank_bg_fg: rank of background/foreground overlap
        """

        labels=[label_t, label_fg,label_bg,label_bg_fg]
        ranks=[rank_t,rank_fg,rank_bg,rank_bg_fg]
        text=["Label/rank of total overlap: ", "Label/rank of foreground overlap: ",
        "Label/rank of background overlap: ","Label/rank of background/foreground overlap: " ]
        out_name=self.output_directory+"/"+output_name
        print(out_name)
        with open(out_name, "w") as outfile:
            for t,l,r in zip(text,labels,ranks):
                outfile.write("%s, %s, %f\n" % (t,l,r))

    
    def write_overlap_lists_from_txt(self,filename):
        """
        This function reads the lists containg the overlap values
        from a txt file.

        :param str filename: nameof file containing the lists

        :returns: lists for total, bg, fg and bg_fg overlaps
        """
        
        filein = open(filename, "r")

        total = []
        fg = []
        bg = []
        bg_fg = []

        for line in filein.readlines():
            tokens = line.split(",")
            total.append(float(tokens[1]))
            fg.append(float(tokens[2]))
            bg.append(float(tokens[3]))
            bg_fg.append(float(tokens[4].rstrip()))
        filein.close()  

        return total, fg,bg,bg_fg

    def read_overlaps_of_dataset(self,filename):
        """This function reads the overlap values of the dataset
        that needs to be classified.

        :returns: total, fg, bg and bg_fg overlap values
        """
        
        filein=open(filename,"r")
        data=[]
        for line in filein.readlines():
            tokens=line.split(",")
            data.append(float(tokens[1]))

        return data[0],data[1],data[2],data[3]


    def main(self):
        """
        The main function of OverlapClassifier which labels and ranks the overlaps
        of the current dataset.
        """
        #decide which overlap kind will be classified
        if self.shoebox_count:
            list_file="/dls/science/users/gwx73773/iolite/share/count_overlaps_shoeboxes.txt"
            filename=self.input_directory+"/DEFAULT/NATIVE/SWEEP1/integrate/overlap_total_shoebox.txt"
            output_name="label_overlap_shoebox.txt"
        else:
            list_file="/dls/science/users/gwx73773/iolite/share/count_overlaps_pixel.txt"
            filename=self.input_directory+"/DEFAULT/NATIVE/SWEEP1/integrate/overlap_total_pixel.txt"
            output_name="label_overlap_pixel.txt"

        #get overlap values of the dataset
        total,fg,bg,bg_fg=self.read_overlaps_of_dataset(filename)
        #get reference overlap data
        total_l,fg_l,bg_l,bg_fg_l= self.write_overlap_lists_from_txt(list_file)
        
        #label and rank overlaps
        label_total,rank_total=self.classify_overlap(total,total_l)
        label_fg,rank_fg=self.classify_overlap(fg,fg_l)
        label_bg,rank_bg=self.classify_overlap(bg,bg_l)
        label_bg_fg,rank_bg_fg=self.classify_overlap(bg_fg,bg_fg_l)

        #write output file
        self.write_output_file(output_name,label_total,rank_total,label_fg,rank_fg,label_bg, rank_bg, label_bg_fg,rank_bg_fg)

    


def run():
    """Allows classify_overlap to be called from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="command line argument")

    parser.add_argument(
        "--shoebox_count",
        dest="shoebox_count",
        type=bool,
        help="The boolean that decides if the count per shoebox should be classified.",
        default=True,
    )
    parser.add_argument(
        "--pixel_count",
        dest="shoebox_count",
        help="Sets shoebox_count to false.",
        action='store_false',
    )
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
    
    overlap_classifier = OverlapClassifier(args.shoebox_count,args.input_directory,args.output_directory)
    overlap_classifier.main()


if __name__ == "__main__":
    run()
