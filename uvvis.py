'''
处理紫外可见分光光度法的实验数据
'''
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

import calculation

CH = ['YouYuan', 'SimHei'] #中文字体幼圆

class UvvisData:
    '''
    紫外可见光谱数据，一份数据包含了波长数组、吸光度数组和数据名
    '''
    def __init__(self, wavelength_array, absorbance_array, name):
        self.wavelength_array = wavelength_array
        self.absorbance_array = absorbance_array
        self.name = name

    def __str__(self):
        return self.name

    def get_absorbance(self, wavelength=333):
        '''
        取出光谱数据中某一波长的吸光度
        '''
        if wavelength in self.wavelength_array:
            return self.absorbance_array[np.where(self.wavelength_array == wavelength)[0][0]]
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

    def __repr__(self):
        return self.name

def read_asc(file):
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

    return UvvisData(np.array(wavelength), np.array(absorbance), file.split('\\')[-1].split('.')[0])

def read_ascdir(filedir):
    '''
    读取给定目录中所有的asc文件，返回UvvisData的实例列表
    '''
    files = os.listdir(filedir)
    try:
        files = sorted(files, key=lambda x:int(x.split('.')[0]))
    except ValueError:
        files.sort()

    uvvis_datas = []
    for file in files:
        if file.endswith('.asc'):
            uvvis_datas.append(read_asc(filedir+'\\'+file))
    return uvvis_datas

def read_ccdatas(cc_filedir, wavelength=254):
    '''
    从文件夹中读取所有asc文件中的数据，并包装成ConcentrationChangeData的列表
    输入的文件夹路径下应该全为次级文件夹，次级文件夹名字将为曲线标签
    次级文件夹内装有asc文件，并且asc文件名为时间
    '''
    folders = os.listdir(cc_filedir)
    cc_datas = []
    for folder in folders:
        if '.' not in folder:
            cc_datas.append(
                get_concentration_change(
                    read_ascdir(cc_filedir+'\\'+folder),
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
        timelist.append(int(data.name))
    return ConcentrationChangeData(np.array(absorlist)/absorlist[0], timelist, name)

#def write_xlsx(cc_datas):

def draw_uvvis(uvvis_datas, color=None, colormap=None, font=None, legend_loc=None):
    '''
    输入二维列表并绘制出uv-vis图
    该列表第二维的元素也是一个列表，其中包含波长、吸光度的两个np数组
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111)
    if font:
        plt.rcParams['font.sans-serif'] = font

    n = len(uvvis_datas)
    if color:
        colorlist = []
        if colors.is_color_like(color):
            #给一个颜色则按透明度递减产生颜色列表
            color = colors.to_rgba(color)
            alpha = np.linspace(color[3], 0.382, n)
            for i in range(n):
                colorlist.append((color[0], color[1], color[2], alpha[i]))
        else:
            if n <= len(color):
                #颜色数大于曲线条数则直接应用
                colorlist = color
            else:
                #颜色数小于曲线条数则转为LinearSegmentedColormap，再插值
                lscm = colors.LinearSegmentedColormap.from_list('', color)
                colorlist = calculation.cmap_interpolation(lscm, n)
        ax.set_prop_cycle(color=colorlist)
    elif colormap:
        colorlist = calculation.cmap_interpolation(colormap, n)
        ax.set_prop_cycle(color=colorlist)

    for data in uvvis_datas:
        ax.plot(data.wavelength_array, data.absorbance_array, label=data.name)

    ax.set_xlabel('wavelength')
    ax.set_ylabel('absorbance')
    ax.set_title('UV-Vis')
    handles, labels = ax.get_legend_handles_labels()
    if legend_loc:
        ax.legend(handles, labels, loc=legend_loc)
    else:
        ax.legend(handles, labels)
    return fig

def draw_concentration_change(cc_datas, font=None, legend_loc=None, ylim=(-0.1, 1.1), **kwargs):
    '''
    传入ConcentrationChangeData实例的列表
    绘制物质浓度-时间图
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111)
    if font:
        plt.rcParams['font.sans-serif'] = font
    #color循环为默认风格的循环
    ax.set_prop_cycle(marker=['o', 'v', 's', 'p', 'h', '*', 'D', 'P', 'X', '8'],
                      color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'])

    for c_change in cc_datas:
        ax.plot(c_change.time_array, c_change.c_array, label=c_change.name, **kwargs)

    ax.set_ylim(ylim[0], ylim[1])
    ax.set_xlabel('Time (min)')
    ax.set_ylabel(r'$C/C_0$')
    handles, labels = ax.get_legend_handles_labels()
    if legend_loc:
        ax.legend(handles, labels, loc=legend_loc)
    else:
        ax.legend(handles, labels)
    return fig
