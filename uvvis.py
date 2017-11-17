'''
处理紫外可见分光光度法的实验数据
'''

import os
import numpy as np
import matplotlib.pyplot as plt

def readasc(file):
    '''
    读取一个asc文件，返回一个列表，其中包含波长、吸光度的两个np数组
    '''
    with open(file, 'r') as asc:
        ascline = '1'
        while ascline != '':
            ascline = asc.readline()
            if ascline == '#DATA\n':
                break
        wavelength, absorbance = [], []
        ascline = asc.readline()
        while ascline != '':
            ascline = ascline.strip('\n')
            wavelength.append(float(ascline.split('\t')[0]))
            absorbance.append(float(ascline.split('\t')[1]))
            ascline = asc.readline()

    x_wavelength = np.array(wavelength)
    y_absorbance = np.array(absorbance)
    return [x_wavelength, y_absorbance]

def readascdir(filedir):
    '''
    读取给定目录中所有的asc文件
    '''
    files = os.listdir(filedir)
    xylist = []
    for file in files:
        if file.endswith('.asc'):
            xylist.append(readasc(filedir+'\\'+file))
    return xylist

def drawuvvis(xylist):
    '''
    输入二维列表，第二维的元素是一个列表，其中包含波长、吸光度的两个np数组
    绘制出uv-vis图
    '''
    for xyarray in xylist:
        if len(xyarray) == 2:
            plt.plot(xyarray[0], xyarray[1])
        else:
            print('列表大小不对，应只有2个元素')
    plt.show()
