import numpy as np
#import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from PIL import Image
import sys
from math import radians

def cropper(img, position, theta):
    if position == 0:
        cropped_image = img.crop((1175, 400, 1400, 1400))
        psi = -90
    else:
        psi = 90
        # camera was consistently translated differently for pos 2, so crop bounds changed
        cropped_image = img.crop((1175, 500, 1400, 1500))
    processed = cropped_image.rotate(psi, expand=True)
    return processed

def rgb2gray(rgb):
    if rgb.ndim == 3:
        r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray/255
    elif np.any(rgb>1): 
        return gray/255

def nib_to_num(im, plot):
    x = np.sum(1-rgb2gray(im),axis=0)
    peaks, other = find_peaks(x, height=60, distance = 100) # points which are peaks
    h = np.array(other['peak_heights']) # array containing the heights of all peaks
    if len(h) > 5:
        #tf = np.where(h < np.mean([np.min(h), np.max(h)]), True, False)
        top5 = np.argsort(h)[-5:]
        tf = np.ones(len(h), dtype=bool)
        tf[top5] = False
        ind = np.where(tf == True)[0]
        p = np.array([int(4-len(np.where(tf[0:t] == False)[0])) for t in ind])
        if np.any(p < 0): return -1
        number = np.sum(2**p)
    else: number = 0; tf = np.zeros(len(h)).astype(bool)
    #if plot ==1:
    #    plt.plot(x)
    #    plt.plot(peaks, x[peaks], "x")
    #    plt.plot(peaks[tf], x[peaks][tf], "o", color='red')
    #    plt.xlabel('length'); plt.ylabel('sum of color_vals')
    #    plt.show()
    #    plt.close()
    return number

def read_sensor_ID(filepath, position, theta):
    if filepath.endswith != '/':
        filepath += '/'
    ID = 0
    for i in range(0,6):
        image = Image.open(filepath + f'temp{i}.bmp')
        cropped = cropper(image, position, theta)
        im = np.array(cropped)
        #plt.imshow(im, cmap='gray', vmin = 0, vmax = 1);
        #plt.show()
        #plt.close()
        digit = nib_to_num(im, plot=0)
        ID = ID*10 + digit
    return str(ID)

# currently the theta input is not used
# if debugging and plots wanted, uncomment plt lines in read_sensor_ID() and set plot = 1

#print(read_sensor_ID("temp", 2, 91))

