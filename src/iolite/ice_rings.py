from dxtbx.model.experiment_list import ExperimentListFactory
import matplotlib.pyplot as plt


experiments = ExperimentListFactory.from_json_file("datablock.json")
assert len(experiments) == 1

beam = experiments[0].beam
detector = experiments[0].detector
imageset = experiments[0].imageset

#help(imageset)

#print(dir(imageset))

panel = detector[0]

res_in = [[0]]                   #create array to store the resolution and intensity values

#image=imageset.get_raw_data(0)[0]
#pixel=image[0,0]
#print(pixel)
#help(image)
#print(len(imageset))


for n in range(1):    # len(imageset)
    image = imageset.get_raw_data(n)[0]         
  #  print(image.all()[0], image.all()[1])

    for y in range(image.all()[0]):       #going through all the pixels
        for x in range(image.all()[1]):
            pixel = image[y,x]
            
            resolution = round(panel.get_resolution_at_pixel(beam.get_s0(), (x,y)),3)
            
            intensity = pixel 
            print(resolution , pixel)      
        
            is_in_array = False

            for i in range(len(res_in)):
                if resolution == res_in[i][0]:
                    res_in[i].append(pixel)  
                    is_in_array = True
            if is_in_array == False:
                res_in.append([resolution,pixel]) 
                
#help(pixel)

del res_in[0]               # remove first line
res_in.sort()               # hopefully this sorts it only based on the resolution values, it will probably sort from low to high values, should that be the case?

# prepare the data for plotting
resolution_data = []
mean_int =[]

for i in range(len(res_in)):
    resolution_data.append(res_in[i][0])
    mean_int.append((sum(res_in[i][1:]))/(len(res_in[i])-1))        #calculate the mean intensity for every single resolution

plt.plot(resolution_data,mean_int)
plt.xlim(max(resolution_data), min(resolution_data))                 #invert the x axis
plt.ylabel('mean intensity')
plt.xlabel('resolution')
plt.title('Mean intensity against resolution')
plt.show()

"""
the ice-rings have to be detected by the program
--> get intensity at the common ice-ring resolutions (3.65 A, 2.25 A and 1.92 A) and calculate the difference in intensity 
compared to a 'slightly' (needs to be defined) lower or higher resolution
classify this difference as either detection of an ice-ring or not
one could also compare the absolute values of the derivatives (should be a significantly higher value at the ice-ring?)


"""