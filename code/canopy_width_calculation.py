import os
import numpy as np
import random
import math
from scipy.spatial import distance_matrix
from queue import Queue
from osgeo import gdal
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from scipy.ndimage import morphology
import cv2
def cv_imread(file_path):
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return cv_img
thre = 0.10
line_k = 0

infolder = r'xxx'
insubfolders = os.listdir(infolder)
for curinsubfolder in insubfolders:
    curinfolder = os.path.join(infolder, curinsubfolder)
    mask_canopy_temporal_filename = os.path.join(curinfolder, 'mask_canopy_temporal_rgb.png')
    mask_canopy_temporal = cv_imread(mask_canopy_temporal_filename) / 255

    for curtime in ['0610', '0616', '0625', '0703', '0710', '0715', '0724', '0730']:
        plotCanopyWidths = []
        curfilename = curtime + '_mask_weed.png'
        cur_data_path = os.path.join(curinfolder, curfilename)
        # img = cv_imread(cur_data_path)
        img_bgr_data = cv_imread(cur_data_path)
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
        erode_mask_canopy_binary = morphology.binary_erosion(mask_canopy, selem)
        erode_mask_canopy = erode_mask_canopy_binary.astype(np.uint8) * 255
        cur_outfile = os.path.join(curinfolder, curfilename[:-4] + '_mask_binary_new.png')
        cv2.imencode('.png', erode_mask_canopy)[1].tofile(cur_outfile)  # 存储成功

        filled_image = morphology.binary_fill_holes(erode_mask_canopy_binary).astype(np.uint8) * 255
        cur_outfile = os.path.join(curinfolder, curfilename[:-4] + '_mask_binary_filled_new.png')
        cv2.imencode('.png', filled_image)[1].tofile(cur_outfile)  # 存储成功

        filled_image_edges = cv2.Canny(image=filled_image, threshold1=127, threshold2=127)
        cur_outfile = os.path.join(curinfolder, curfilename[:-4] + '_mask_binary_filled_edge_new.png')
        cv2.imencode('.png', filled_image_edges)[1].tofile(cur_outfile)  # 存储成功
        edge_rows, edge_cols = np.where(filled_image_edges > 0)
        out_img_bgr_data_edge = out_img_bgr_data.copy()
        out_img_bgr_data_edge[edge_rows, edge_cols, 0] = 0
        out_img_bgr_data_edge[edge_rows, edge_cols, 1] = 0
        out_img_bgr_data_edge[edge_rows, edge_cols, 2] = 255
        cur_outfile = os.path.join(curinfolder, curfilename[:-4] + '_mask_edge_new.png')
        cv2.imencode('.png', out_img_bgr_data_edge)[1].tofile(cur_outfile)  # 存储成功

        # 聚类
        canopy_rows, canopy_cols = np.where(filled_image > 0)
        mask_canopy_rgb = np.zeros([height, width, 3])
        mask_canopy_rgb_lines = np.zeros([height, width, 3])

        if len(canopy_rows) == 0:
            plotCanopyWidths.append(0)
        else:
            # 参数设置
            eps = 1  # 起始epsilon值
            min_samples = 2  # 最小样本数
            d_rate = 0.5  # epsilon增长率阈值
            max_iter = 100  # 最大迭代次数
            X = np.stack([canopy_rows, canopy_cols], axis=1)
            # 创建DSCAN实例
            dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean', algorithm='auto', leaf_size=30, p=2, n_jobs=1)
            # 执行聚类
            labels = dbscan.fit_predict(X)
            # 标签为-1的点是噪声点
            unique_labels = set(labels)
            colors = np.zeros([len(unique_labels), 3])
            for ci in range(len(unique_labels)):
                colors[ci, 0] = random.randint(0, 255)
                colors[ci, 1] = random.randint(0, 255)
                colors[ci, 2] = random.randint(0, 255)

            # 绘制结果
            for k, col in zip(unique_labels, colors):
                if k == -1:
                    # 黑色表示噪声
                    col = [0, 0, 0]
                class_member_mask = (labels == k)
                curobjects = X[class_member_mask]
                object_size, _ = curobjects.shape
                flag_weed = np.sum(mask_canopy_temporal[curobjects[:, 0], curobjects[:, 1]])  # 判断是不是杂草
                if object_size < 10 or flag_weed == 0:
                    continue
                mask_canopy_rgb[curobjects[:, 0], curobjects[:, 1]] = col[:3]
                mark_curobject = np.zeros(object_size)
                segmentedobjects = []
                for i in range(object_size):
                    if mark_curobject[i]:
                        continue
                    mark_curobject[i] = 1
                    cursegmentedobject = []
                    cursegmentedobject.append(curobjects[i, :])
                    cur_row = curobjects[i, 0]
                    for j in range(i + 1, object_size):
                        if mark_curobject[j]:
                            continue
                        if curobjects[j, 0] == cur_row:
                            mark_curobject[j] = 1
                            cursegmentedobject.append(curobjects[j, :])
                    segmentedobjects.append(cursegmentedobject)

                # 查看是否对每个分割对象细分
                fine_segmentedobjects = []
                for object in segmentedobjects:
                    object = np.stack(object, axis=0)
                    # 创建DSCAN实例
                    cur_dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean', algorithm='auto',
                                        leaf_size=30,
                                        p=2, n_jobs=1)
                    # 执行聚类
                    cur_labels = cur_dbscan.fit_predict(object)
                    cur_unique_labels = set(cur_labels)
                    for cur_k in cur_unique_labels:
                        if cur_k == -1:
                            continue
                        cur_class_member_mask = (cur_labels == cur_k)
                        fine_segmentedobjects.append(object[cur_class_member_mask])

                line_colors = np.zeros([len(fine_segmentedobjects), 3])
                for ci in range(len(fine_segmentedobjects)):
                    line_colors[ci, 0] = random.randint(0, 255)
                    line_colors[ci, 1] = random.randint(0, 255)
                    line_colors[ci, 2] = random.randint(0, 255)

                for i, object in enumerate(fine_segmentedobjects):
                    object = np.stack(object, axis=0)
                    mask_canopy_rgb_lines[object[:, 0], object[:, 1]] = line_colors[i]

                for object in fine_segmentedobjects:
                    distances_sp = distance_matrix(object, object)
                    maxWidth = np.max(distances_sp)
                    plotCanopyWidths.append(maxWidth)

        cur_outfile = os.path.join(curinfolder, curfilename[:-4] + '_plotCanopyWidths.txt')
        np.savetxt(cur_outfile,plotCanopyWidths,fmt='%5f ')
        cur_outfile = os.path.join(curinfolder, curfilename[:-4] + '_mask_rgb_lines_new.png')
        cv2.imencode('.png', mask_canopy_rgb_lines)[1].tofile(cur_outfile)  # 存储成功










