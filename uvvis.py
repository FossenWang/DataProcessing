'''
处理紫外可见分光光度法的实验数据
'''

import numpy as np
import matplotlib.pyplot as plt

asc = open('F:\\Laboratory\\紫外数据\\20171010\\原.asc', 'r')

asc_line = '1'
while asc_line!='':
    asc_line = asc.readline()
    if(asc_line=='#DATA\n'):
        break

wave_length,absorbance = [],[]

asc_line = asc.readline()
while asc_line!='':
    asc_line = asc_line.strip('\n')
    wave_length.append(float(asc_line.split('\t')[0]))
    absorbance.append(float(asc_line.split('\t')[1]))
    asc_line = asc.readline()

x=np.array(wave_length)
y=np.array(absorbance)

plt.plot(x,y)
plt.show()
