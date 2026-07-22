import os
import numpy as np
import random
import math
from scipy.spatial import distance_matrix
from queue import Queue
from osgeo import gdal
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from scipy.ndimage import morphology, binary_erosion, binary_fill_holes
import cv2

def cv_imread(file_path):
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return cv_img

thre = 0.1

infolder = r'I:\宋明轩2024\新专利\跑代码'
outfolder = r'I:\宋明轩2024\新专利\跑代码'  # 为outfolder指定一个有效的输出路径

if not os.path.exists(outfolder):
    os.mkdir(outfolder)

insubfolders = os.listdir(infolder)
for cursubfolder in insubfolders:
    cur_insubfolder = os.path.join(infolder, cursubfolder)
    mask_canopy_temporal_filename = os.path.join(cur_insubfolder, 'mask_canopy_temporal_rgb.png')
    mask_canopy_temporal = cv_imread(mask_canopy_temporal_filename) / 255

    subfolder_outpath = os.path.join(outfolder, cursubfolder)
    if not os.path.exists(subfolder_outpath):
        os.mkdir(subfolder_outpath)

    for curtime in ['0610', '0616', '0625', '0703', '0710', '0715', '0724', '0730']:
        cur_img_path = os.path.join(cur_insubfolder, curtime + '.tif')
        img_bgr_data = cv_imread(cur_img_path)

        cur_outfile = os.path.join(subfolder_outpath, curtime + '.png')
        cv2.imencode('.png', img_bgr_data)[1].tofile(cur_outfile)

        out_img_bgr_data = img_bgr_data.copy()
        im_Blue_img_arr = img_bgr_data[:, :, 0] / 255.0  # B
        im_Green_img_arr = img_bgr_data[:, :, 1] / 255.0  # G
        im_Red_img_arr = img_bgr_data[:, :, 2] / 255.0  # R
        esp = 1e-8
        im_b_img_arr = im_Blue_img_arr / (im_Blue_img_arr + im_Green_img_arr + im_Red_img_arr + esp)
        im_g_img_arr = im_Green_img_arr / (im_Blue_img_arr + im_Green_img_arr + im_Red_img_arr + esp)
        im_r_img_arr = im_Red_img_arr / (im_Blue_img_arr + im_Green_img_arr + im_Red_img_arr + esp)
        veg_index_map = 2 * im_g_img_arr - im_r_img_arr - im_b_img_arr
        rows, cols = np.where(veg_index_map > thre)
        mask_canopy = np.zeros(veg_index_map.shape)
        height, width = mask_canopy.shape
        mask_canopy[rows, cols] = 1
        selem = np.ones((3, 3), np.uint8)
        erode_mask_canopy_binary = binary_erosion(mask_canopy, selem)
        erode_mask_canopy = erode_mask_canopy_binary.astype(np.uint8) * 255
        cur_outfile = os.path.join(subfolder_outpath, curtime + '_mask_binary.png')
        cv2.imencode('.png', erode_mask_canopy)[1].tofile(cur_outfile)

        filled_image = binary_fill_holes(erode_mask_canopy_binary).astype(np.uint8) * 255
        cur_outfile = os.path.join(subfolder_outpath, curtime + '_mask_binary_filled.png')
        cv2.imencode('.png', filled_image)[1].tofile(cur_outfile)

        filled_image_edges = cv2.Canny(image=filled_image, threshold1=127, threshold2=127)
        cur_outfile = os.path.join(subfolder_outpath, curtime + '_mask_binary_filled_edge.png')
        cv2.imencode('.png', filled_image_edges)[1].tofile(cur_outfile)
        edge_rows, edge_cols = np.where(filled_image_edges > 0)
        out_img_bgr_data_edge = out_img_bgr_data.copy()
        out_img_bgr_data_edge[edge_rows, edge_cols, 0] = 0
        out_img_bgr_data_edge[edge_rows, edge_cols, 1] = 0
        out_img_bgr_data_edge[edge_rows, edge_cols, 2] = 255
        cur_outfile = os.path.join(subfolder_outpath, curtime + '_mask_edge.png')
        cv2.imencode('.png', out_img_bgr_data_edge)[1].tofile(cur_outfile)

        # 聚类
        canopy_rows, canopy_cols = np.where(filled_image > 0)
        mask_weed = np.zeros([height, width])
        # 参数设置
        eps = 1  # 起始epsilon值
        min_samples = 2  # 最小样本数
        d_rate = 0.5  # epsilon增长率阈值
        max_iter = 100  # 最大迭代次数

        X = np.stack([canopy_rows, canopy_cols], axis=1)
        if X.shape[0] < 1:
            continue
        # 创建DBSCAN实例
        dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean', algorithm='auto', leaf_size=30, p=2,
                        n_jobs=1)
        # 执行聚类
        labels = dbscan.fit_predict(X)
        # 标签为-1的点是噪声点
        unique_labels = set(labels)

        # 绘制结果
        for k in unique_labels:
            class_member_mask = (labels == k)
            curobjects = X[class_member_mask]
            object_size, _ = curobjects.shape
            flag_weed = np.sum(mask_canopy_temporal[curobjects[:, 0], curobjects[:, 1]])  # 判断是不是杂草
            if k == -1 or object_size < 10 or flag_weed == 0:
                # 黑色表示噪声
                mask_weed[curobjects[:, 0], curobjects[:, 1]] = 1

        weed_rows, weed_cols = np.where(mask_weed == 1)
        out_img_bgr_data[weed_rows, weed_cols, 0] = 0
        out_img_bgr_data[weed_rows, weed_cols, 1] = 0
        out_img_bgr_data[weed_rows, weed_cols, 2] = 255
        cur_outfile = os.path.join(subfolder_outpath, curtime + '_mask_weed.png')
        cv2.imencode('.png', out_img_bgr_data)[1].tofile(cur_outfile)


 #腐蚀填充


