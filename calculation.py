''''
处理数据时常用的计算方法
'''
import numpy as np
from scipy import interpolate
from scipy.optimize import curve_fit
from matplotlib import cm, colors

def logistic_fit(x, y):
    '''
    拟合logistic函数,P(t)=KP_0exp(rt)/(K+P_0(exp(rt)-1)),P_0为初值，K为终值
    返回函数y=f(x)
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
    输入两数组x、y，返回数值微分结果dy/dx
    '''
    x1 = np.append(x[1:], x[-1])
    x2 = np.append(x[0], x[:-1])
    y1 = np.append(y[1:], y[-1])
    y2 = np.append(y[0], y[:-1])
    return (y1-y2)/(x1-x2)

def cmap_interpolation(colormap, n):
    '''
    第一个参数为matplotlib内建的colormap
    第二个参数是要提取的颜色个数
    使用分段插值法计算出对应的颜色
    返回含有n个颜色的列表
    '''
    if not isinstance(colormap, colors.Colormap):
        colormap = cm.get_cmap(colormap)

    if hasattr(colormap, 'colors'):
        # 将ListedColormap转化为LinearSegmentedColormap
        colormap = colors.LinearSegmentedColormap.from_list('', colormap.colors)

    cdict = colormap._segmentdata
    rgblist = []
    for key in sorted(cdict, reverse=True):
        positions = np.linspace(0, 1, n)
        values = []
        i = 0
        for position in positions:
            while 1:
                if cdict[key][i][0] <= position <= cdict[key][i+1][0]:
                    f = interpolate.interp1d(
                        [cdict[key][i][0], cdict[key][i+1][0]],
                        [cdict[key][i][2], cdict[key][i+1][1]]
                        )
                    values.append(f(position))
                    break
                elif i < len(cdict[key]):
                    i += 1
                else:
                    break
        rgblist.append(values)

    return [(rgblist[0][i], rgblist[1][i], rgblist[2][i]) for i in range(n)]

def get_color_list(color, n):
    '将颜色参数转化为颜色列表'
    colorlist = []
    if colors.is_color_like(color):
        # 给一个颜色则按透明度递减产生颜色列表
        color = colors.to_rgba(color)
        if n==1:
            return [color]
        alpha = np.linspace(color[3], 0.382, n)
        for i in range(n):
            colorlist.append((color[0], color[1], color[2], alpha[i]))
    else:
        if n <= len(color):
            # 颜色数大于曲线条数则取前n个
            colorlist = [colors.to_rgba(color[i]) for i in range(n)]
        else:
            # 颜色数小于曲线条数则转为LinearSegmentedColormap，再插值
            lscm = colors.LinearSegmentedColormap.from_list('', color)
            colorlist = cmap_interpolation(lscm, n)
    return colorlist
