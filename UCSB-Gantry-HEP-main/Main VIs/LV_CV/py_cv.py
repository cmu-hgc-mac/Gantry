import numpy as np
import cv2 as cv2
method = cv2.TM_SQDIFF_NORMED

def test_im(loc):
    im = cv2.imread('off1.png')
    return str(np.shape(im))

def get_mm_per_pix():
    # diag = 0.2*np.sqrt(2) # in mm
    # xp = 597; yp = 251
    # xp = 260; yp = 257 (0.1 mm by 0.1 mm) (approx 0.4 mu/pixel)
    # return diag/np.sqrt(np.square(xp)+np.square(yp))
    return 0.200/470.7186

'''This fuction finds the "small" image in the "large" image. '''
def get_xp_yp(small, large):
    method = cv2.TM_SQDIFF_NORMED
    result = cv2.matchTemplate(small, large, method)    
    mn,_,mnLoc,_ = cv2.minMaxLoc(result)
    MPx,MPy = mnLoc
    return np.array([MPx, MPy]), mn 

'''"live" is the image as read from the camera in current time. "fid" refers to a cropped image of the fiducial. "saved" is an image for reference with the fiducial at the center of the screen. '''
def get_new_loc(loc):
    live = cv2.imread('LV_CV/save_im.png')
    saved = cv2.imread('LV_CV/ref2.png')
    # fid = cv2.imread('LV_CV/fidclose.png')
    fid = cv2.imread('LV_CV/fidcloseSq.png')
    live_co, minval = get_xp_yp(fid, live)
    save_co, minval_s = get_xp_yp(fid, saved)
    trows,tcols = fid.shape[:2]
    if minval < 0.08:
        return get_mm_per_pix()*(live_co-save_co)
    return np.array([-0.1, -0.1, -0.1, 0])
    return np.array([-0.1, 0.1, -86.235228, -8.7])
    # return np.array([781., -712., -0.235228, 0.])
    # return ch
    # return np.array([len(live)*1., len(live[0])*1., len(fid[0])*1., len(fid[1])*1.])
    # return(str(get_mu_per_p()*(live_co-save_co)))