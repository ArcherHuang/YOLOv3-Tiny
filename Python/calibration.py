import os, cv2, glob
import numpy as np
dataset_path = "DATASET PATH" # 路徑要修改
calib_batch_size = 10
inputsize = {'h': 416, 'c': 3, 'w': 416}

def convertimage(img, w, h, c):
    new_img = np.zeros((w, h, c))
    for idx in range(c):
        resize_img = img[:, :, idx]
        resize_img = cv2.resize(resize_img, (w, h), cv2.INTER_AREA)
        new_img[:, :, idx] = resize_img
    return new_img

# This function reads all images in dataset
# and return all images with the name of inputnode
def calib_input(iter):
    images = []
    #line = open(calibfile).readlines()
    line = glob.glob(dataset_path + "/*.png")
    for index in range(0, calib_batch_size):
        curline = line[iter * calib_batch_size + index]
        calib_image_name = curline.strip()
        image = cv2.imread(calib_image_name)
        image = convertimage(image, inputsize["w"], inputsize["h"], inputsize["c"])
        image = image / 255.0
        images.append(image)
    return{"yolov3-tiny/net1":images} #firstlayer 