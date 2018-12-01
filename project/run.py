import matplotlib.pyplot as plt
import glob
import os
import initialize as init
import processIMG as process
import numpy as np

def run_set(dir_in, image_format='png'):
    """ run lane detection on all images in input folder with declared image formation, `image_format` is png by default. This function will write output lane, area, region image in created output folder """
    
    prev_left = []
    prev_right = []

    # run lane detection on set of images
    input = glob.glob(dir_in + '*.' + image_format)
    images, binary_img, warped_images, peaks, M = init.find_lane_set(input)
    dir_out = dir_in + "out"
    if not os.path.isdir(dir_out): os.makedirs(dir_out)
    print("**->>> Input directory:   " + dir_in)
    print("**->>> Output directory:  " + dir_out)
    print("-")

    for i in range(len(images)):
        im = images[i]
        warped = warped_images[i]
        peak = peaks[i]
        area, lane, region = process.processIMG_set(im, warped, peak, prev_left, prev_right, M)
        
        half = warped[int(warped.shape[0] / 2):, :]
        [lp, rp] = peak
        mid = int(warped.shape[1] / 2)
        
        f, (ax1) = plt.subplots(1, 1, figsize=(6, 4))
        ax1.plot(np.sum(half, axis=0))
        ax1.plot(np.ones(mid) + lp, np.arange(mid) / 1.8)
        ax1.plot(np.ones(mid) + rp, np.arange(mid) / 1.8)
        ax1.set_title('Histogram of Binary Warped Image')
        plt.savefig(dir_out + "/" + str(i+1) + "_hist.png")
        plt.close()

        binary_out = dir_out + "/" + str(i+1) + "_binary.png"
        plt.imsave(binary_out, binary_img[i], cmap='gray')

        warped_out = dir_out + "/" + str(i+1) + "_warped.png"
        plt.imsave(warped_out, warped_images[i], cmap='gray')

        area_out = dir_out + "/" + str(i+1) + "_area.png"
        plt.imsave(area_out,area)

        lane_out = dir_out + "/" + str(i+1) + "_lane.png"
        plt.imsave(lane_out,lane)

        region_out = dir_out + "/" + str(i+1) + "_region.png"
        plt.imsave(region_out,region)

        print(" *** Images Processed: " + str(i+1) + " *** ")

    print("** ---- done ---- **")

def run_single(im, plot=0):
    """ Run lane detection on single image"""
    print("** ---- start process on single image --- **")
 
    area, lane, region = process.processIMG(im)

    if plot: 
        # visualize results 
        plt.subplots(4, 1, figsize=(12, 8))

        plt.subplot(221)
        plt.imshow(im)
        plt.title("Image")

        plt.subplot(222)
        plt.imshow(lane, cmap='gray')
        plt.title("Lane")

        plt.subplot(223)
        plt.imshow(area, cmap='gray')
        plt.title("Area")

        plt.subplot(224)
        plt.imshow(region, cmap='gray')
        plt.title("Region")

        plt.show()
    print("*** --- done --- ***")
    return area