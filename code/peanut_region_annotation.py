import os
import numpy as np
import random
import math
from scipy.spatial import distance_matrix
from queue import Queue
from osgeo import gdal
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import cv2
def cv_imread(file_path):
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return cv_img

thre = 0.10
infolder = r'xxx'
insubfolders = os.listdir(infolder)

for cursubfolder in insubfolders:

    cur_insubfolder = os.path.join(infolder, cursubfolder)
    if 'HN' in cursubfolder:
        height = 1378
        width = 771
    elif 'LN' in cursubfolder:
        height = 839
        width = 567
    mask_canopy_temporal = np.ones([height, width])
    for curtime in ['0610', '0616', '0625', '0703', '0710', '0715', '0724', '0730']:
        cur_img_path = os.path.join(cur_insubfolder, curtime + '.tif')
        img_bgr_data = cv_imread(cur_img_path)
        im_Blue_img_arr = img_bgr_data[:, :, 0] / 255.0  # B
        im_Green_img_arr = img_bgr_data[:, :, 1] / 255.0  # G
        im_Red_img_arr = img_bgr_data[:, :, 2] / 255.0  # R
        esp = 1e-8
        im_b_img_arr = im_Blue_img_arr / (im_Blue_img_arr + im_Green_img_arr + im_Red_img_arr + esp)
        im_g_img_arr = im_Green_img_arr / (im_Blue_img_arr + im_Green_img_arr + im_Red_img_arr + esp)
        im_r_img_arr = im_Red_img_arr / (im_Blue_img_arr + im_Green_img_arr + im_Red_img_arr + esp)
        veg_index_map = 2 * im_g_img_arr - im_r_img_arr - im_b_img_arr
        rows, cols = np.where(veg_index_map > thre)
        cur_mask_canopy = np.zeros(veg_index_map.shape)
        cur_mask_canopy[rows, cols] = 1
        mask_canopy_temporal = np.multiply(cur_mask_canopy, mask_canopy_temporal)

    mask_canopy_temporal = mask_canopy_temporal * 255
    cur_outfile = os.path.join(os.path.join(infolder, cur_insubfolder), 'mask_canopy_temporal_rgb.png')
    cv2.imencode('.png', mask_canopy_temporal)[1].tofile(cur_outfile)  # 存储成功



