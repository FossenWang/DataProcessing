'命令行版程序，已弃用'
import traceback
import matplotlib.pyplot as plt
import uvvis

DIVIDELINE = '\n'+'—'*30+'\n'

def main():
    try:
        n = 0
        while n not in ['1', '2', 'q']:
            n = input('\n处理紫外数据\n请选择要绘制的曲线类型：\n1、吸光度-波长曲线\n2、浓度变化曲线\n输入q退出\n')
            if n == '1':
                handle_uvvis()
            elif n == '2':
                handle_concentration_change()
            elif n == 'q':
                return 0
    except Exception:
        print(traceback.format_exc())

    print(DIVIDELINE)
    s = input('\n按回车键继续处理紫外数据 | 输入 q 退出\n')
    if s == 'q':
        return 0
    else:
        print(DIVIDELINE)
        return 1

def handle_uvvis():
    ascdir = input('\n请输入文件夹路径\n')
    kwargs = input_args("\n请输入其他参数\n例：color='r', colormap='autumn', font=None, legend_loc=None\n")
    uvvis_datas = uvvis.read_ascdir(ascdir)
    uvvis.draw_uvvis(uvvis_datas, **kwargs)
    plt.show()

def handle_concentration_change():
    cc_filedir = input('\n请输入文件夹路径\n')
    wavelength = int(input('\n请输入特征波长\n'))
    kwargs = input_args("\n请输入其他参数\n例：font=['YouYuan'],legend_loc=(0,0),ylim=(-0.1,1.1)\n")
    cc_datas = uvvis.read_ccdatas(cc_filedir, wavelength=wavelength)
    uvvis.draw_concentration_change(cc_datas, **kwargs)
    plt.show()
    if not cc_filedir.endswith('\\'):
        cc_filedir += '\\'
    xlsx_path = cc_filedir + 'rusult.xlsx'
    if input('\n是否保存数据？（y/n）\n') == 'y':
        uvvis.write_xlsx(xlsx_path, cc_datas)
        print('\n已保存至：%s\n' % xlsx_path)

def input_args(s=''):
    l = {}
    exec('kwargs=dict(%s)' % input(s), globals(), l)
    return l['kwargs']


if __name__ == "__main__":
    while main():
        pass
