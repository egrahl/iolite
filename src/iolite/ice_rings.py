from dxtbx.model.experiment_list import ExperimentListFactory
import matplotlib.pyplot as plt


experiments = ExperimentListFactory.from_json_file("datablock.json")
assert len(experiments) == 1

beam = experiments[0].beam
detector = experiments[0].detector
imageset = experiments[0].imageset


panel = detector[0]

res_in = [[0]]                   #create default array to store the resolution and intensity values

for n in range(number_of_images):
    for x in range(image_width):       #going through all the pixels
        for y in range(image_length):
            resolution = panel.get_resolution_at_pixel(beam.get_s0(), (x,y))
            #print("Resolution at pixel (0,0) = %f" % resolution)
            intensity = 0       #some function to determine the intensity of the pixel 
        
            is_in_array = False

            for i in res_in:
                if intensity == res_in[i][0]:
                    res_in[i].append(intensity)  
                    is_in_array = True
            if is_in_array == False:
                res_in.append([resolution,intensity])

del res_in[0]               # remove default first line
res_in.sort()               # hopefully this sorts it only based on the resolution values, it will probably sort from low to high values, should that be the case?

# prepare the data for plotting
resolution_data = []
mean_int =[]

for i in res_in:
    resolution_data.append(res_in[i][0])
    mean_int.append((sum(res_in[i][1:]))/(len(res_in[i])-1))        #calculate the mean intensity for every single resolution

plt.plot(resolution_data,mean_int)
plt.xlim(max(resolution_data), min(resolution_data))                 #invert the x axis
plt.ylabel('mean intensity')
plt.xlabel('resolution')
plt.title('Mean intensity against resolution')
plt.show()

