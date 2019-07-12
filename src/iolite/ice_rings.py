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






"""
def calculateRatio (res,intensity,startRes,endRes, boundary):
    indexstart =res.index(startRes)
    indexend = res.index(endRes)
    indexboundary = res.index(boundary)
    intensity_peak = sum(intensity[indexstart:(indexend+1)])/(indexend-indexstart+1)
    intensity_bg = sum(intensity[indexend:(indexboundary+1)])/(indexboundary-indexend+1)
    return (intensity_peak/intensity_bg)

start=timer()


experiments = ExperimentListFactory.from_json_file("datablock.json")
assert len(experiments) == 1

beam = experiments[0].beam
detector = experiments[0].detector
imageset = experiments[0].imageset


panel = detector[0]




xy_data = []
res_index_l = []
resolution_data = []

image1 = imageset.get_raw_data(0)[0]

for y in range(image1.all()[0]):       #going through all the pixels
        for x in range(image1.all()[1]):
            xy_data.append([x,y])
            resolution = round(panel.get_resolution_at_pixel(beam.get_s0(), (x,y)),2)
           
            try:
                index= resolution_data.index(resolution)
            except ValueError:
                resolution_data.append(resolution)
                index= resolution_data.index(resolution) 
            
            res_index_l.append(index)


end=timer()
print(xy_data)
print('time taken:', (end-start))

intensity_data = [[None]]*len(resolution_data)


for n in range(1):   # len(imageset) 
    image = imageset.get_raw_data(n)[0]         
    for i in range(100):           #len(xy_data)
        pixel = image[xy_data[i][1],xy_data[i][0]]
        print(pixel)
        res_index = res_index_l[i]
        print(res_index)
        #if intensity_data[res_index]==None:
        #    intensity_data[res_index] =[pixel]
        #else:    
            #intensity_data[res_index].append(pixel)   
      
#print(intensity_data)

resolution_data = [0]                   #create a list for resolution data
intensity_data =[[0]]



for n in range(1):   # len(imageset) 
    image = imageset.get_raw_data(n)[0]         
  #  print(image.all()[0], image.all()[1])

    for y in range(image.all()[0]):       #going through all the pixels
        for x in range(image.all()[1]):
           
            #resolution = round(panel.get_resolution_at_pixel(beam.get_s0(), (x,y)),3)
            resolution = round(panel.get_resolution_at_pixel(beam.get_s0(), (x,y)),2)
            if resolution <= 4.00:
                pixel = image[y,x]
                # print(resolution , pixel)   
                try:
                    index= resolution_data.index(resolution)
                    intensity_data[index].append(pixel)
                except ValueError:
                    resolution_data.append(resolution)
                    intensity_data.append([pixel])   
      


del resolution_data[0]               # remove first line in resolution_data
del intensity_data[0]


# prepare the data for plotting

mean_int =[]

for i in range(len(resolution_data)):
    mean_int.append((sum(intensity_data[i]))/(len(intensity_data[i])))       #calculate the mean intensity for every single resolution


#resolution_data= np.array(resolution_data)
#mean_int = np.array(mean_int)

#resMInt = np.stack((resolution_data,mean_int), axis =-1)
#print(resMInt)



# calculate the intensity ratios

ratio1 = calculateRatio(resolution_data, mean_int,3.65,3.69,3.90)
ratio2 = calculateRatio(resolution_data, mean_int,2.24,2.25,2.45)
ratio3 = calculateRatio(resolution_data, mean_int,1.91,1.93,2.00)

print(ratio1, ratio2, ratio3)

sumratios = ratio1 + ratio2 + ratio3
print(sumratios)


end=timer()
print('time used:', end-start)
"""

#plot data
plt.plot(resolution_data,intensity_data)
#plt.xlim(max(resolution_data),min(resolution_data) )                 #invert the x axis
plt.ylabel('Mean Intensity')
plt.xlabel('Resolution')
plt.title('Mean intensity vs resolution')
plt.show()
