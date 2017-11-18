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
    return [x_wavelength, y_absorbance, file.split('\\')[-1]]

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

def getabsor(xylist, wavelength=333):
    '''
    取出光谱图中某一波长的吸光度
    '''
    absorbance = []

    if len(xylist) > 3:
        for xy in xylist:
            if len(xy) == 3:
                absorbance.append(xy[1][np.argwhere(xy[0] == wavelength)[0][0]])
            else:
                print('列表结构不对，应为2维列表，且第二维的列表包含2个np数组和一个字符串')
    elif len(xylist) == 3:
        absorbance.append(xylist[1][np.argwhere(xy[0] == wavelength)])
    else:
        print('列表结构不对，应为2维列表，且第二维的列表包含2个np数组和一个字符串')

    return absorbance

def drawuvvis(xylist):
    '''
    输入二维列表并绘制出uv-vis图
    该列表第二维的元素也是一个列表，其中包含波长、吸光度的两个np数组
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111)

    if len(xylist) > 3:
        for xy in xylist:
            if len(xy) == 3:
                ax.plot(xy[0], xy[1], label=xy[2])
            else:
                print('列表结构不对，应为2维列表，且第二维的列表包含2个np数组和一个字符串')
    elif len(xylist) == 3:
        ax.plot(xylist[0], xylist[1], label=xy[2])
    else:
        print('列表结构不对，应为2维列表，且第二维的列表包含2个np数组和一个字符串')

    ax.set_xlabel('wavelength')
    ax.set_ylabel('absorbance')
    ax.set_title('UV-Vis')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels)
    return fig
