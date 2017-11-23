'''
处理紫外可见漫反射光谱的实验数据
'''
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import linregress

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
        self.hvfr2_logi_fit = logistic_fit(self.hv, self.hvfr2)
        self.hvfr12_logi_fit = logistic_fit(self.hv, self.hvfr12)
        self.egd, self.kd, self.bd, self.rd = self.calculate_eg(self.hvfr2, self.hvfr2_logi_fit)
        self.egi, self.ki, self.bi, self.ri = self.calculate_eg(self.hvfr12, self.hvfr12_logi_fit)

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

    def calculate_eg(self, y, y_fit=0, fp=0, a=25):
        '''
        y_fit经过logistic拟合的y，对y_fit数值微分，求得微分最大值，取得该点的引索imdy
        分别取该点周围n个(5<=n<=50)元素进行线性拟合，返回斜率k，截距b,相关系数r和imdy
        '''
        if not fp:
            dy=num_differ(self.hv, y_fit)
            imdy=np.where(dy==max(dy))[0][0]
        else:
            absdif = np.fabs(self.hv-fp)
            imdy=np.where(absdif==min(absdif))[0][0]
        for i in range(a,1,-1):
            if (imdy-i)>=0 and (imdy+i)<len(self.hv):
                k, b, r, p, s = linregress(self.hv[(imdy-i):(imdy+i)], y[(imdy-i):(imdy+i)])
                if r>0.99:
                    break
        eg = -b/k
        return [eg, k, b, r]

def refit(drs, n, fp=0, a=25):
    '''
    根据输入的点x0和左右元素范围a重新拟合曲线，n为（hvfr）^n中的的指数n
    '''
    if n == 2:
        drs.egd, drs.kd, drs.bd, drs.rd = drs.calculate_eg(drs.hvfr2, fp=fp, a=a)
    elif n == 0.5:
        drs.egi, drs.ki, drs.bi, drs.ri = drs.calculate_eg(drs.hvfr12, fp=fp, a=a)
    else:
        print('please enter n=2 or n = 0.5')

def logistic_fit(x, y):
    '''
    拟合logistic函数,P(t)=KP_0exp(rt)/(K+P_0(exp(rt)-1)),P_0,为初值，K为终值
    '''
    def func(z, t, r):
        return (k*p*np.exp(r*z+t))/(k+p*(np.exp(r*z+t)-1))

    k = max(y)
    p = y[-1]
    i = np.where(y==k)[0][0]

    popt, pcov = curve_fit(func, x[i:], y[i:])
    return func(x, *popt)

def num_differ(x, y):
    '''
    numerical differentiation 数值微分
    参数为numpy.ndarray对象
    '''
    x1=np.append(x[1:], x[-1])
    x2=np.append(x[0], x[:-1])
    y1=np.append(y[1:], y[-1])
    y2=np.append(y[0], y[:-1])
    return (y1-y2)/(x1-x2)

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
        txt.write('samlpe:'+str(drs.name)+'\n')
        txt.write('direct band gap: wevelength='+str(1240/drs.egd)+'nm energy='+str(drs.egd)+'eV\n')
        txt.write('\tlinear fit coefficient: slope='+str(drs.kd)+' intercept='+str(drs.bd)+' r='+str(drs.rd))
        txt.write('\nindirect band gap: wevelength='+str(1240/drs.egi)+'nm energy='+str(drs.egi)+'eV\n')
        txt.write('\tlinear fit coefficient: slope='+str(drs.ki)+' intercept='+str(drs.bi)+' r='+str(drs.ri))
        txt.write('\ndatas:\n')
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
    fig.set_size_inches(12,5.2)
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    ax1.plot(drs.hv, drs.hvfr2, label='direct')
    ax1.plot([drs.egd, (max(drs.hvfr2)-drs.bd)/drs.kd], [0, max(drs.hvfr2)])
    ax1.set_xlabel('hv (eV)')
    ax1.set_ylabel(r'$(hv F(R))^2$')
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles, labels)
    ax1.text(drs.egd-0.25, max(drs.hvfr2)/2,
        (r'$\lambda$ = '+str(int(round(1240/drs.egd)))+' nm\n'+r'$E_g$ = '+str(round(drs.egd,2))+' eV'),
        horizontalalignment='right', verticalalignment='bottom')

    ax2.plot(drs.hv, drs.hvfr12, label='indirect')
    ax2.plot([drs.egi, (max(drs.hvfr12)-drs.bi)/drs.ki], [0, max(drs.hvfr12)])
    ax2.set_xlabel('hv (eV)')
    ax2.set_ylabel(r'$(hv F(R))^\frac{1}{2}$')
    handles, labels = ax2.get_legend_handles_labels()
    ax2.legend(handles, labels)
    ax2.text(drs.egi-0.25, max(drs.hvfr12)/2,
        (r'$\lambda$ = '+str(int(round(1240/drs.egi)))+' nm\n'+r'$E_g$ = '+str(round(drs.egi,2))+' eV'),
        horizontalalignment='right', verticalalignment='bottom')
    return fig
