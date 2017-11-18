'''
处理污染物降解数据
'''

#import numpy as np
import matplotlib.pyplot as plt


def drawdegra(absorbance, time, label):
    '''
    绘制污染物降解图
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(time, absorbance, label=label)
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('absorbance')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels)
    return fig
