import tkinter as tk
import tkinter.messagebox
from tkinter.filedialog import askdirectory
import matplotlib.pyplot as plt
import uvvis

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        master.title('Uvvis')
        master.geometry('480x300')
        self.pack()
        self.create_widgets()
        self.home_page()

    def create_widgets(self):
        self.up_frame = tk.Frame(self)
        self.down_frame = tk.Frame(self)

        self.title_label = tk.Label(self.up_frame, wraplength=300, font=('Microsoft YaHei', 12))
        self.dir_label = tk.Label(self.up_frame, text='选择文件夹')
        self.args_label = tk.Label(self.up_frame, text='请输入其他参数', height=2, anchor='s')
        self.args_entry = tk.Entry(self.up_frame, width=50, justify='center')
        self.wavelength_label = tk.Label(self.up_frame, text='请输入特征波长(nm)', height=2, anchor='s')
        self.wavelength_entry = tk.Entry(self.up_frame, width=50, justify='center')

        self.first_button = tk.Button(self.down_frame)
        self.second_button = tk.Button(self.down_frame)
        self.return_button = tk.Button(self.down_frame, text='返回', command=self.home_page)
        self.dir_button = tk.Button(self.up_frame, text='选择文件夹', command=self.select_dir)

        self.up_frame.pack(side='top')
        self.down_frame.pack(side='bottom', ipady = 10)

        self.title_label.pack(side='top', pady=20)
        self.first_button.pack(side='left', padx=10)
        self.second_button.pack(side='left', padx=10)

    def select_dir(self):
        self.dir_label['text'] = askdirectory()

    def clean_page(self):
        self.dir_label.pack_forget()
        self.args_label.pack_forget()
        self.args_entry.pack_forget()
        self.wavelength_label.pack_forget()
        self.wavelength_entry.pack_forget()
        self.return_button.pack_forget()
        self.dir_button.pack_forget()

    def home_page(self):
        self.clean_page()

        self.title_label['text'] = '处理Uvvis数据\n请选择要绘制的曲线类型'
        self.first_button['text'] = '吸光度-波长曲线'
        self.first_button['command'] = self.uvvis_page
        self.second_button['text'] = '浓度变化曲线'
        self.second_button['command'] = self.c_change_page

    def uvvis_page(self):
        self.clean_page()

        self.title_label['text'] = '绘制Uvvis吸光度-波长曲线'
        self.first_button['text'] = '绘图'
        self.first_button['command'] = self.show_uvvis
        self.second_button['text'] = '导出数据'
        self.second_button['command'] = self.write_uvvis_datas
        self.dir_label.pack(side='top')
        self.dir_button.pack(side='top')
        self.args_label.pack(side='top')
        self.args_entry.pack(side='top')
        self.return_button.pack(side='left', padx=10)

    def c_change_page(self):
        self.clean_page()

        self.title_label['text'] = '绘制浓度变化曲线'
        self.first_button['text'] = '绘图'
        self.first_button['command'] = self.show_cc_figure
        self.second_button['text'] = '导出数据'
        self.second_button['command'] = self.write_cc_datas

        self.dir_label.pack(side='top')
        self.dir_button.pack(side='top')
        self.wavelength_label.pack(side='top')
        self.wavelength_entry.pack(side='top')
        self.args_label.pack(side='top')
        self.args_entry.pack(side='top')
        self.return_button.pack(side='left', padx=10)

    def show_uvvis(self):
        try:
            ascdir = self.dir_label['text']
            kwargs = input_args(self.args_entry.get())
            uvvis_datas = uvvis.read_ascdir(ascdir)
            uvvis.draw_uvvis(uvvis_datas, **kwargs)
            plt.show()
        except Exception as e:
            tk.messagebox.showerror(title='Error', message=str(e))

    def write_uvvis_datas(self):
        try:
            ascdir = self.dir_label['text']
            if ascdir[-1] not in ['\\', '/']:
                ascdir += '/'
            xlsx_path = ascdir + 'uvvis_datas.xlsx'
            uvvis_datas = uvvis.read_ascdir(ascdir)
            uvvis.write_xlsx(xlsx_path, uvvis_datas)
            tk.messagebox.showinfo(title='Sucess', message='数据已保存至:'+xlsx_path)
        except Exception as e:
            tk.messagebox.showerror(title='Error', message=str(e))

    def show_cc_figure(self):
        try:
            cc_filedir = self.dir_label['text']
            wavelength = int(self.wavelength_entry.get())
            kwargs = input_args(self.args_entry.get())
            cc_datas = uvvis.read_ccdatas(cc_filedir, wavelength=wavelength)
            uvvis.draw_concentration_change(cc_datas, **kwargs)
            plt.show()
        except Exception as e:
            tk.messagebox.showerror(title='Error', message=str(e))

    def write_cc_datas(self):
        try:
            wavelength = int(self.wavelength_entry.get())
            cc_filedir = self.dir_label['text']
            if cc_filedir[-1] not in ['\\', '/']:
                cc_filedir += '/'
            xlsx_path = cc_filedir + 'cc_datas.xlsx'
            cc_datas = uvvis.read_ccdatas(cc_filedir, wavelength=wavelength)
            uvvis.write_xlsx(xlsx_path, cc_datas)
            tk.messagebox.showinfo(title='Sucess', message='数据已保存至:'+xlsx_path)
        except Exception as e:
            tk.messagebox.showerror(title='Error', message=str(e))

def input_args(s=''):
    l = {}
    exec('kwargs=(lambda **k:k)(%s)' % s, globals(), l)
    return l['kwargs']

root = tk.Tk()
app = Application(master=root)
app.mainloop()
