'''
处理紫外可见漫反射光谱的实验数据
'''
import os
import numpy as np
import matplotlib.pyplot as plt

class UvvisDrsData:
    '''
    紫外可见漫反射光谱数据，一份数据包含了波长数组、反射率数组和数据名
    '''
    def __init__(self, wavelength_array, reflectance_array, name):
        self.wavelength_array = wavelength_array
        self.reflectance_array = reflectance_array
        self.name = name
        self.hv = self.calculate_hv(wavelength_array)
        self.fr = self.calculate_fr()
        self.hvfr2 = self.calculate_hvfr2()
        self.hvfr12 = self.calculate_hvfr12()

    def calculate_hv(self, wavelength_array):
        '''
        hv=hc/λ=1240/λ
        用该式将波长换算成能量hv
        '''
        return 1240/wavelength_array

    def calculate_fr(self):
        '''
        Kubelka–Munk absorption function: F(R) = (1-R)^2/(2R)
        用上式计算出F(R)的值，其中R为reflectance
        '''
        return ((1-self.reflectance_array)**2)/(2*self.reflectance_array)

    def calculate_hvfr2(self):
        '''
        计算(hvF(R))^2
        '''
        return (self.hv*self.fr)**2

    def calculate_hvfr12(self):
        '''
        计算(hvF(R))^1/2
        '''
        return (self.hv*self.fr)**0.5


def read_raw(file):
    '''
    读取存有DRS数据的txt文件
    '''
    with open(file, 'r') as txt:
        txtline = '1'
        while txtline != '':
            txtline = txt.readline()
            if txtline == '"波长(nm)","T%"\n':
                break
        wavelength, reflectance_array = [], []
        txtline = txt.readline()
        while txtline != '':
            txtline = txtline.strip('\n')
            wavelength.append(float(txtline.split(',')[0]))
            reflectance_array.append(float(txtline.split(',')[1]))
            txtline = txt.readline()

    return UvvisDrsData(np.array(wavelength), np.array(reflectance_array)/100, file.split('\\')[-1].split('.')[0])

def write_drs(drs):
    '''
    将数据写入至txt文件
    '''
    with open(drs.name+'_result.txt', 'w') as txt:
        txt.write('wavelength\tR\thv\tF(R)\t(hvF(R))^2\t(hvF(R))^1/2\n')
        for data in zip(drs.wavelength_array, drs.reflectance_array, drs.hv, drs.fr, drs.hvfr2, drs.hvfr12):
            line = ''
            for each in data:
                line = line + str(each) + '\t'
            txt.write(line[:-1] + '\n')

def draw_hvfr(drs):
    '''
    传入UvvisDrsData实例
    绘制(hvF(R))^2-hv图和(hvF(R))^1/2-hv图
    '''
    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    ax1.set_title(drs.name)
    ax1.plot(drs.hv, drs.hvfr2, label='direct')
    ax1.set_xlabel('hv (eV)')
    ax1.set_ylabel(r'$(hv F(R))^2$')
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles, labels)

    ax2.plot(drs.hv, drs.hvfr12, label='indirect')
    ax2.set_xlabel('hv (eV)')
    ax2.set_ylabel(r'$(hv F(R))^\frac{1}{2}$')
    handles, labels = ax2.get_legend_handles_labels()
    ax2.legend(handles, labels)
    return fig
