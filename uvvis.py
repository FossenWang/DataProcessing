'''
处理紫外可见分光光度法的实验数据
'''

import os
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.font_manager import FontProperties

font = ['YouYuan', 'DejaVu Sans']

class UvvisData:
    '''
    紫外可见光谱数据，一份数据包含了波长数组、吸光度数组和数据名
    '''
    def __init__(self, wavelength_array, absorbance_array, name):
        self.wavelength_array = wavelength_array
        self.absorbance_array = absorbance_array
        self.name = name

    def get_absorbance(self, wavelength=333):
        '''
        取出光谱数据中某一波长的吸光度
        '''
        if wavelength in self.wavelength_array:
            return self.absorbance_array[np.argwhere(self.wavelength_array == wavelength)[0][0]]
        else:
            print('输入波长范围应在{}~{}nm内'.format(self.wavelength_array[-1], self.wavelength_array[0]))

class ConcentrationChangeData:
    '''
    根据吸光度变化计算得到物质浓度变化
    包含物质浓度比例（C/C0）数组、时间数组的数据
    '''
    def __init__(self, c_array, time_array, name):
        self.c_array = c_array
        self.time_array = time_array
        self.name = name

def readasc(file):
    '''
    读取一个asc文件，返回UvvisData的实例
    文件名为样品的浓度变化对应的时间
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
    return UvvisData(x_wavelength, y_absorbance, file.split('\\')[-1].split('.')[0])

def readascdir(filedir):
    '''
    读取给定目录中所有的asc文件，返回UvvisData的实例列表
    '''
    files = os.listdir(filedir)
    uvvis_datas = []
    for file in files:
        if file.endswith('.asc'):
            uvvis_datas.append(readasc(filedir+'\\'+file))
    return uvvis_datas

def readccdatas(cc_filedir, wavelength=254):
    '''
    从文件夹中读取所有asc文件中的数据，并包装成ConcentrationChangeData的列表
    输入的文件夹路径下应该全为次级文件夹，次级文件夹名字将为曲线标签
    次级文件夹内装有asc文件，并且asc文件名为时间
    '''
    folders = os.listdir(cc_filedir)
    cc_datas = []
    for folder in folders:
        cc_datas.append(
            get_concentration_change(
                readascdir(cc_filedir+'\\'+folder),
                wavelength,
                folder))
    return cc_datas

def get_concentration_change(uvvis_datas, wavelength=333, name=''):
    '''
    传入UvvisData列表和相应的时间以及特征波长
    得到浓度变化的数据
    '''
    absorlist = []
    timelist = []
    for data in uvvis_datas:
        absorlist.append(data.get_absorbance(wavelength))
        timelist.append(data.name)
    return ConcentrationChangeData(np.array(absorlist)/absorlist[0], timelist, name)

def draw_uvvis(uvvis_datas):
    '''
    输入二维列表并绘制出uv-vis图
    该列表第二维的元素也是一个列表，其中包含波长、吸光度的两个np数组
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.rcParams['font.sans-serif'] = font

    for data in uvvis_datas:
        ax.plot(data.wavelength_array, data.absorbance_array, label=data.name)

    ax.set_xlabel('wavelength')
    ax.set_ylabel('absorbance')
    ax.set_title('UV-Vis')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels)
    return fig

def draw_concentration_change(cc_datas):
    '''
    传入ConcentrationChangeData实例的列表
    绘制物质浓度-时间图
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.rcParams['font.sans-serif'] = font
    #color循环为默认风格的循环
    ax.set_prop_cycle(marker=['o', 'v', 's', 'p', 'h', '*', 'D', 'P', 'X', '8'],
                      color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'])

    for c_change in cc_datas:
        ax.plot(c_change.time_array, c_change.c_array, label=c_change.name)

    ax.set_xlabel('Time (min)')
    ax.set_ylabel(r'$C/C_0$')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels)
    return fig
