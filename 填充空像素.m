clc;
clear;
clc;
clear;
folder = 'D:\作物表型\冠层宽度\2024宁阳冠层宽度\P1after\';
files = dir(fullfile(folder, '*.tif'));
fileNames = {files(~[files.isdir]).name};
for idx=1:length(fileNames)
    rgbfile=fileNames{idx};
    inputpath  = [folder rgbfile];
    outname = ['modified_' rgbfile];  %存储位置和名字
    [rgb_SS,rgb_R] = geotiffread(inputpath);  %SS为tif数据的信息，是一个二维数组，R是tif数据的地理信息
    info = geotiffinfo(inputpath);  % 读取tif数据的地理信息，为后面导出为tif数据提供地理信息
    [rgbrows,rgbcols,dim]=size(rgb_SS);
    for i=2:rgbrows
        for j=2:rgbcols
            if rgb_SS(i,j,1)==255 || rgb_SS(i,j,2)==255 || rgb_SS(i,j,3)==255
                rgb_SS(i,j,:)=rgb_SS(i-1,j-1,:);
            end
        end
    end
    geotiffwrite(outname,rgb_SS, rgb_R, 'GeoKeyDirectoryTag', info.GeoTIFFTags.GeoKeyDirectoryTag, 'TiffType','bigtiff'); 
end
