from dxtbx.model.experiment_list import ExperimentListFactory
import matplotlib.pyplot as plt
import numpy as np
from timeit import default_timer as timer


def calculateRatio (res,intensity,startRes,endRes, boundary):
    indexstart =res.index(startRes)
    indexend = res.index(endRes)
    indexboundary = res.index(boundary)
    intensity_peak = (sum(intensity,indexstart)-sum(intensity,indexend+1))/(indexend-indexstart)
    intensity_bg = (sum(intensity,indexend)-sum(intensity,indexboundary+1))/(indexboundary-indexend)
    return (intensity_peak/intensity_bg)

start=timer()


experiments = ExperimentListFactory.from_json_file("datablock.json")
assert len(experiments) == 1

beam = experiments[0].beam
detector = experiments[0].detector
imageset = experiments[0].imageset

#help(imageset)

#print(dir(imageset))

panel = detector[0]

resolution_data = [0]                   #create a list for resolution data
intensity_data =[[0]]

#image=imageset.get_raw_data(0)[0]
#pixel=image[0,0]
#print(pixel)
#help(image)
#print(len(imageset))


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
      
#help(pixel)

del resolution_data[0]               # remove first line in resolution_data
del intensity_data[0]


# prepare the data for plotting

mean_int =[]

for i in range(len(resolution_data)):
    mean_int.append((sum(intensity_data[i]))/(len(intensity_data[i])))       #calculate the mean intensity for every single resolution

end=timer()
print('time used:', end-start)

#resolution_data= np.array(resolution_data)
#mean_int = np.array(mean_int)

#resMInt = np.stack((resolution_data,mean_int), axis =-1)
#print(resMInt)

plt.plot(resolution_data,mean_int)
plt.xlim(4.0, 1.3)                 #invert the x axis
#plt.ylim(0, 800)
plt.ylabel('Mean Intensity')
plt.xlabel('Resolution (A)')
plt.title('Mean intensity vs resolution')
plt.show()

"""
the ice-rings have to be detected by the program
--> get intensity at the common ice-ring resolutions (3.67 A, 2.25 A and 1.92 A) and calculate the difference in intensity 
compared to a 'slightly' (needs to be defined) lower or higher resolution
classify this difference as either detection of an ice-ring or not
one could also compare the absolute values of the derivatives (should be a significantly higher value at the ice-ring?)


"""
# calculate the intensity ratios; SOMETHING IS WRONG HERE!!!

ratio1 = calculateRatio(resolution_data, mean_int,3.65,3.69,3.90)
ratio2 = calculateRatio(resolution_data, mean_int,2.24,2.25,2.45)
ratio3 = calculateRatio(resolution_data, mean_int,1.91,1.93,2.00)

print(ratio1, ratio2, ratio3)

sumratios = ratio1 + ratio2 + ratio3
print(sumratios)