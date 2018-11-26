import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import cv2

# curve detection
def curvature_detection(img, old_l_samples=[], old_r_samples=[], img_c=None):
    threshold = 100
    stride_height = 50
    window_height = 100
    window_width = 50
    img_height = img.shape[0]
    img_width = img.shape[1]

    if (len(old_l_samples) == 0) | (len(old_r_samples) == 0):
        old_samples_provided = False
        print("detecting left and peak from current image")
        lp, rp = peak_detection(img)
        lane_widths = [rp - lp] * int((img_height / stride_height) + 1)
    else:
        old_samples_provided = True
        lp = old_l_samples[0, 0]
        rp = old_r_samples[0, 0]
        lane_widths = old_r_samples[:, 0] - old_l_samples[:, 0]
        
    # result
    l_samples = []
    r_samples = []

    # window sliding
    i = 0
    for window_y_end in range(img_height, stride_height, -stride_height):
        window_y_start = window_y_end - window_height
        
        # histogram for entire horizon of current window slide
        histogram = np.sum(img[window_y_start:window_y_end, int(window_width / 2) : -int(window_width / 2)], axis=0)

        # calculate convolution by sliding window accross the horizon
        window = np.ones(window_width)
        conv = np.convolve(window, histogram)
                
        # left window based on previous left peak
        window_l_start = int(lp - (window_width / 2))
        window_l_end = window_l_start + window_width

        # right window based on previous right peak
        window_r_start = int(rp - (window_width / 2))
        window_r_end = window_r_start + window_width

        # new left and right peaks
        l_found = sum(conv[window_l_start:window_l_end]) > threshold
        r_found = sum(conv[window_r_start:window_r_end]) > threshold

        if r_found & l_found:
            lp = argmax(conv[window_l_start:window_l_end]) + window_l_start
            rp = argmax(conv[window_r_start:window_r_end]) + window_r_start 
        else:
            if l_found:
                lp = argmax(conv[window_l_start:window_l_end]) + window_l_start
                rp = min(lp + lane_widths[i], img_width)    
            if r_found:
                rp = argmax(conv[window_r_start:window_r_end]) + window_r_start 
                lp = max(rp - lane_widths[i], 0)

        # draw left window on output image (green if found, red otherwise)
        if type(img_c) is np.ndarray:
            l_window_color = [0,255,0] if l_found else [255, 0, 0]
            cv2.rectangle(img_c, (window_l_start, window_y_start), (window_l_end, window_y_end), l_window_color, 2)
            r_window_color = [0,255,0] if l_found else [255, 0, 0]
            cv2.rectangle(img_c, (window_r_start, window_y_start), (window_r_end, window_y_end), r_window_color, 2)

        l_samples.append([lp, window_y_end])
        r_samples.append([rp, window_y_end])
        
        window_width = window_width + 10
        i = i + 1
        
    l_samples = np.array(l_samples)
    r_samples = np.array(r_samples)
    #normalize_samples(l_samples, r_samples)
    
    if old_samples_provided:
        all_l_samples = np.concatenate((l_samples, old_l_samples))
        all_r_samples = np.concatenate((r_samples, old_r_samples))
    else:
        all_l_samples = l_samples
        all_r_samples = r_samples
        
    l_fit = np.polyfit(all_l_samples[:,1], all_l_samples[:,0], 2)
    r_fit = np.polyfit(all_r_samples[:,1], all_r_samples[:,0], 2)
    
    # Define conversions in x and y from pixels space to meters
    xm_per_pix = 3.7/700 # meters per pixel in x dimension
    ym_per_pix = 30/720 # meters per pixel in y dimension

    # Fit new polynomials to x,y in world space
    l_fit_r = np.polyfit(all_l_samples[:,1]*ym_per_pix, all_l_samples[:,0]*xm_per_pix, 2)
    r_fit_r = np.polyfit(all_r_samples[:,1]*ym_per_pix, all_r_samples[:,0]*xm_per_pix, 2)
    
    return l_samples, r_samples, l_fit, r_fit, l_fit_r, r_fit_r