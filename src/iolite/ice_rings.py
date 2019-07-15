from dxtbx.model.experiment_list import ExperimentListFactory
import matplotlib.pyplot as plt
import numpy as np
from timeit import default_timer as timer


filein=open("table.txt","r")

resolution_data = []
intensity_data = []

for line in filein.readlines():
    tokens = line.split(",")
    resolution_data.append(tokens[0])
    intensity_data.append(tokens[1])








#plot data
plt.plot(resolution_data,intensity_data)
#plt.xlim(max(resolution_data),min(resolution_data) )                 #invert the x axis
plt.ylabel('Mean Intensity')
plt.xlabel('Resolution')
plt.title('Mean intensity vs resolution')
plt.show()
