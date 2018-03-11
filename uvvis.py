'''
处理紫外可见分光光度法的实验数据
'''
import os, xlsxwriter, re
from itertools import cycle
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt

import calculation

CH = ['YouYuan', 'SimHei'] #中文字体幼圆
D_MARKERS = ['o', 'v', 's', 'p', 'h', '*', 'D', 'P', 'X', '8']
D_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

class UvvisData:
    '''
    紫外可见光谱数据，一份数据包含了波长数组、吸光度数组和数据名
    '''
    def __init__(self, wavelength_array, absorbance_array, name):
        self.wavelength_array = wavelength_array
        self.absorbance_array = absorbance_array
        self.name = name

    def __repr__(self):
        return 'UvvisData:'+self.name

    def get_absorbance(self, wavelength):
        '''
        取出光谱数据中某一波长的吸光度
        '''
        if wavelength in self.wavelength_array:
            return self.absorbance_array[np.where(self.wavelength_array == wavelength)[0][0]]
        else:
            raise ValueError('{} | 输入波长范围应在{}~{}nm内'.format(wavelength, self.wavelength_array[-1], self.wavelength_array[0]))

class ConcentrationChangeData:
    '''
    根据吸光度变化计算得到物质浓度变化
    包含物质浓度比例（C/C0）数组、时间数组的数据
    '''
    def __init__(self, absor_array, time_array, name, init_absor=None, wavelength=0):
        if init_absor:
            self.init_absor = init_absor
        else:
            self.init_absor = absor_array[0]
        self.c_array = absor_array/self.init_absor
        self.time_array = time_array
        self.name = name
        self.wavelength = wavelength

    def __repr__(self):
        return 'ConcentrationChangeData:'+self.name

def read_asc(asc_file):
    '''
    读取一个asc文件，返回UvvisData的实例
    文件名为样品的浓度变化对应的时间
    '''
    if not asc_file.endswith('.asc'):
        return
    with open(asc_file, 'r') as asc:
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
    name = re.split(r'/|\\', asc_file.replace('.asc', ''))[-1]
    return UvvisData(np.array(wavelength), np.array(absorbance), name)

def read_ascdir(filedir):
    '''
    读取给定目录中所有的asc文件，返回UvvisData的实例列表
    '''
    files = os.listdir(filedir)
    y = ''
    ascfiles = []
    for f in files:
        if f.endswith('.asc'):
            if f == 'y.asc':
                y = 'y.asc'
            else:
                ascfiles.append(f)
    try:
        ascfiles = sorted(ascfiles, key=lambda x:int(x.split('.')[0]))
    except ValueError:
        ascfiles.sort()
    if y:ascfiles.insert(0,y)

    uvvis_datas = []
    for f in ascfiles:
        if f.endswith('.asc'):
            uvvis_datas.append(read_asc(filedir+'\\'+f))
    return uvvis_datas

def read_ccdatas(cc_filedir, wavelength):
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

def get_concentration_change(uvvis_datas, wavelength, name=''):
    '''
    传入UvvisData列表和相应的时间以及特征波长
    得到浓度变化的数据
    '''
    absorlist = []
    timelist = []
    init_absor = None
    for data in uvvis_datas:
        if data.name == 'y':
            init_absor = data.get_absorbance(wavelength)
        else:
            absorlist.append(data.get_absorbance(wavelength))
            try:
                timelist.append(int(data.name))
            except ValueError as e:
                print(e,'\n文件名应为整数\n')
                raise e
    return ConcentrationChangeData(np.array(absorlist), timelist, name, init_absor, wavelength)

def write_xlsx(file_path, datas):
    '将数据写入至excel表格'
    if isinstance(datas[0], ConcentrationChangeData):
        write_cc_datas(file_path, datas)
    elif isinstance(datas[0], UvvisData):
        write_uvvis_datas(file_path, datas)
    else:
        raise TypeError('Must UvvisData or ConcentrationChangeData')

def write_cc_datas(file_path, cc_datas):
    '将cc_datas数据写入至excel表格'
    wb = xlsxwriter.Workbook(file_path)
    ws = wb.add_worksheet()
    center = wb.add_format({'align': 'center'})
    n = 1
    for data in cc_datas:
        ws.merge_range('A%d:C%d'%(n,n), data.name)
        n+=1
        ws.merge_range('A%d:B%d'%(n,n), 'initial_absorbance')
        ws.write('C%d'%n, data.init_absor)
        n+=1
        ws.merge_range('A%d:B%d'%(n,n), 'wavelength')
        ws.write('C%d'%n, data.wavelength)
        n+=1
        ws.write_row('A%d'%n, ['time', 'C/C0', 'absorbance'])
        n+=1
        ws.write_column('A%d'%n, data.time_array)
        ws.write_column('B%d'%n, data.c_array)
        ws.write_column('C%d'%n, data.c_array*data.init_absor)
        n+=len(data.time_array)+3
    ws.set_column('A:A', 10, center)
    ws.set_column('B:C', 20, center)
    wb.close()

def write_uvvis_datas(file_path, uvvis_datas):
    '将uvvis_datas数据写入至excel表格'
    wb = xlsxwriter.Workbook(file_path)
    center = wb.add_format({'align': 'center'})
    c = Counter([
        (data.wavelength_array[0], data.wavelength_array[-1], len(data.wavelength_array)) 
        for data in uvvis_datas])
    if len(c)==1:
        ws1 = wb.add_worksheet('combined')
        n = 0
        ws1.write(0,n, 'name→')
        ws1.write(1,n, 'nm')
        ws1.write_column(2,n, uvvis_datas[0].wavelength_array)
        n+=1
        for data in uvvis_datas:
            ws1.write_column(0,n, [data.name, 'A'])
            ws1.write_column(2,n, data.absorbance_array)
            n+=1
        ws1.set_column(0,n, 10, center)
    else:
        ws2 = wb.add_worksheet('separated')
        n = 0
        for data in uvvis_datas:
            ws2.write_row(0,n, ['name', data.name])
            ws2.write_row(1,n, ['nm', 'A'])
            ws2.write_column(2,n, data.wavelength_array)
            ws2.write_column(2,n+1, data.absorbance_array)
            n+=3
        ws2.set_column(0,n, 10, center)
    wb.close()

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
        ax.set_prop_cycle(color=calculation.get_color_list(color, n))
    elif colormap:
        ax.set_prop_cycle(color=calculation.cmap_interpolation(colormap, n))

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

def draw_concentration_change(cc_datas, color=None, colormap=None, font=None, legend_loc=None, ylim=(-0.1, 1.1), **kwargs):
    '''
    传入ConcentrationChangeData实例的列表
    绘制物质浓度-时间图
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111)
    if font:
        plt.rcParams['font.sans-serif'] = font

    # 设置循环风格
    n = len(cc_datas)
    if color:
        m_cycle = cycle(D_MARKERS)
        markers = [m_cycle.__next__() for i in range(n)]
        colorlist = calculation.get_color_list(color, n)
    elif colormap:
        m_cycle = cycle(D_MARKERS)
        markers = [m_cycle.__next__() for i in range(n)]
        colorlist = calculation.cmap_interpolation(colormap, n)
    else:
        markers = D_MARKERS
        colorlist = D_COLORS
    ax.set_prop_cycle(marker=markers, color=colorlist)

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
