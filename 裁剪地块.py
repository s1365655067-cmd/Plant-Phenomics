import shapefile
from shapely.geometry import Polygon, Point
import os
import numpy as np
import argparse
from osgeo import gdal
import cv2

# 保存带中文的图片
def cv_imwrite(file_path,img):
    cv2.imencode('.tiff', img)[1].tofile(file_path)

inputfolder = r'F:\2025年花生\P1株高\0716\p1071612mrtk开旁向70航向80\result'
ShpData_path = r'F:\2025年花生\plotboundary-无误\plotboundaryLN\plotboundary.shp'
outfolder = r'F:\2025年花生\P1株高\2025p10813\result裁剪'

files = os.listdir(inputfolder)
for curfile in files:
    ptype = None
    if 'HN' in curfile:
        ptype = 'HN'
    elif 'LN' in curfile:
        ptype = 'LN'

    Outfolder = os.path.join(outfolder, curfile[9:13])
    # Outfolder = curfile[9:13]
    if not os.path.exists(Outfolder):
        os.makedirs(Outfolder)

    multiband_img_file = os.path.join(inputfolder, curfile)
    multiband_src_img = gdal.Open(multiband_img_file, gdal.GA_ReadOnly)
    blue_im_data_arr = multiband_src_img.GetRasterBand(1).ReadAsArray()
    green_im_data_arr = multiband_src_img.GetRasterBand(2).ReadAsArray()
    red_im_data_arr = multiband_src_img.GetRasterBand(3).ReadAsArray()
    # 读取地理转换信息
    geo_transform = multiband_src_img.GetGeoTransform()
    min_x = geo_transform[0]
    max_y = geo_transform[3]
    grid_width = multiband_src_img.GetGeoTransform()[1]
    grid_height = abs(multiband_src_img.GetGeoTransform()[5])
    del multiband_src_img
    img_bgr_data = np.stack([blue_im_data_arr, green_im_data_arr, red_im_data_arr], axis=2)
    del blue_im_data_arr, green_im_data_arr, red_im_data_arr
    ShpData = shapefile.Reader(ShpData_path)
    for shprec in ShpData.shapeRecords():
        shp = shprec.shape
        rec = shprec.record
        if ptype not in rec.plotID:
            continue
        points = np.stack(shp.points)
        data_rc = []  # 存储转换后的数据
        for x, y in points:
            row = int((float(max_y) - float(y)) / grid_height)
            column = int((float(x) - float(min_x)) / grid_width)
            data_rc.append((row, column))  # 添加转换后的数据到列表中

        data_rc_poly = Polygon(data_rc)
        data_rc = np.stack(data_rc, axis=0)
        min_data_rc = np.min(data_rc, axis=0)
        max_data_rc = np.max(data_rc, axis=0)

        bgr_data_rc_roi = img_bgr_data.copy()[min_data_rc[0]:max_data_rc[0], min_data_rc[1]:max_data_rc[1], :]
        rgb_data_rc_roi = cv2.cvtColor(bgr_data_rc_roi, cv2.COLOR_BGR2RGB)
        out_rgb_img_file_path = os.path.join(Outfolder, 'rgb_' + rec.plotID + '.tif')
        cv_imwrite(out_rgb_img_file_path, rgb_data_rc_roi)
        # cv2.imwrite(out_rgb_img_file_path, rgb_data_rc_roi)  # 保存为tif格式，并添加压缩参数

# #单波段
# import shapefile
# from shapely.geometry import Polygon, Point
# import os
# import numpy as np
# from osgeo import gdal
# import cv2
#
#
# # 保存带中文的图片
# def cv_imwrite(file_path, img):
#     cv2.imencode('.tiff', img)[1].tofile(file_path)
#
#
# inputfolder = r'F:\2025年花生\P1株高\p1062512mrtk关7080改\减法'
# ShpData_path = r'F:\2025年花生\plotboundary-无误\plotboundaryLN\plotboundary.shp'
# outfolder = r'F:\2025年花生\P1株高\p1062512mrtk关7080改\裁剪后'
#
# files = os.listdir(inputfolder)
# for curfile in files:
#     ptype = None
#     if 'HN' in curfile:
#         ptype = 'HN'
#     elif 'LN' in curfile:
#         ptype = 'LN'
#
#     Outfolder = os.path.join(outfolder, curfile[9:13])
#     if not os.path.exists(Outfolder):
#         os.makedirs(Outfolder)
#
#     multiband_img_file = os.path.join(inputfolder, curfile)
#     multiband_src_img = gdal.Open(multiband_img_file, gdal.GA_ReadOnly)
#
#     if multiband_src_img is None:
#         print(f"Error: Could not open file {multiband_img_file}")
#         continue
#
#     # 只读取一个波段（比如第1个波段）
#     band1_im_data_arr = multiband_src_img.GetRasterBand(1).ReadAsArray()
#
#     # 读取地理转换信息
#     geo_transform = multiband_src_img.GetGeoTransform()
#     min_x = geo_transform[0]
#     max_y = geo_transform[3]
#     grid_width = geo_transform[1]
#     grid_height = abs(geo_transform[5])
#     del multiband_src_img
#
#     ShpData = shapefile.Reader(ShpData_path)
#     for shprec in ShpData.shapeRecords():
#         shp = shprec.shape
#         rec = shprec.record
#         if ptype not in rec.plotID:
#             continue
#
#         points = np.stack(shp.points)
#         data_rc = []  # 存储转换后的数据
#         for x, y in points:
#             row = int((max_y - float(y)) / grid_height)
#             column = int((float(x) - min_x) / grid_width)
#             data_rc.append((row, column))  # 添加转换后的数据到列表中
#
#         data_rc_poly = Polygon(data_rc)
#         data_rc = np.stack(data_rc, axis=0)
#         min_data_rc = np.min(data_rc, axis=0)
#         max_data_rc = np.max(data_rc, axis=0)
#
#         # 获取ROI区域（单波段数据）
#         band1_data_rc_roi = band1_im_data_arr[min_data_rc[0]:max_data_rc[0], min_data_rc[1]:max_data_rc[1]]
#
#         out_img_file_path = os.path.join(Outfolder,  rec.plotID + '.tif')
#         cv_imwrite(out_img_file_path, band1_data_rc_roi)
#
#     print(f"Processing completed for {curfile}")






