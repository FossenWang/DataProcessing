'''
以uvvis为核心的一个简单的GUI界面程序
'''
from os import startfile
from collections import Counter
from re import split
import tkinter as tk
import tkinter.messagebox
from tkinter.filedialog import askdirectory, askopenfilenames
import matplotlib.pyplot as plt
import uvvis

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        master.title('Uvvis')
        master.geometry('480x480')
        self.pack()
        self.create_widgets()
        self.home_page()

    def create_widgets(self):
        self.up_frame = tk.Frame(self)
        self.up_frame.pack(side='top')
        self.down_frame = tk.Frame(self)
        self.down_frame.pack(side='top', pady = 10)
        self.dirbtn_frame = tk.Frame(self.up_frame)
        self.dirlist_frame = tk.Frame(self.up_frame)
        self.listbtn_frame = tk.Frame(self.dirlist_frame)
        self.listbtn_frame.pack(pady=10)

        self.title_label = tk.Label(self.up_frame, wraplength=300, font=('Microsoft YaHei', 12))
        self.title_label.pack(side='top', pady=20)
        self.dir_label = tk.Label(self.up_frame, text='')
        self.args_label = tk.Label(self.up_frame, text='请输入其他参数', height=2, anchor='s')
        self.args_entry = tk.Entry(self.up_frame, width=50, justify='center')
        self.wavelength_label = tk.Label(self.up_frame, text='请输入特征波长(nm)', height=2, anchor='s')
        self.wavelength_entry = tk.Entry(self.up_frame, width=50, justify='center')

        self.first_button = tk.Button(self.down_frame)
        self.first_button.pack(side='left', padx=10)
        self.second_button = tk.Button(self.down_frame)
        self.second_button.pack(side='left', padx=10)
        self.return_button = tk.Button(self.down_frame, text='返回', command=self.home_page)
        self.select_button = tk.Button(self.dirbtn_frame, text='选择文件夹', command=self.select_dir)
        self.select_button.pack(side='left', padx=10)
        self.open_button = tk.Button(self.dirbtn_frame, text='打开文件夹', command=self.open_dir)
        self.open_button.pack(side='left', padx=10)
        self.add_button = tk.Button(self.listbtn_frame , text='添加')
        self.add_button.pack(side='left', padx=10)
        self.delete_button = tk.Button(self.listbtn_frame, text='删除', command=self.delete_items)
        self.delete_button.pack(side='left', padx=10)
        self.manual_button = tk.Button(self, text='使用手册', command=self.manual)

        self.y_scrollbar = tk.Scrollbar(self.dirlist_frame, orient='vertical')
        self.y_scrollbar.pack(side='right', fill='y')
        self.x_scrollbar = tk.Scrollbar(self.dirlist_frame, orient='horizontal')
        self.x_scrollbar.pack(side='bottom', fill='x')
        self.dir_listbox = tk.Listbox(self.dirlist_frame, height=5, width=48, \
        selectmode='extended', yscrollcommand=self.y_scrollbar.set, xscrollcommand=self.x_scrollbar.set)
        self.dir_listbox.pack()
        self.y_scrollbar.config(command=self.dir_listbox.yview)
        self.x_scrollbar.config(command=self.dir_listbox.xview)

    def add_ascfiles(self):
        files = askopenfilenames()
        if not files:
            return
        items = [self.dir_listbox.get(i) for i in range(self.dir_listbox.size())]
        for f in files:
            if f.endswith('.asc'):
                if f not in items:
                    self.dir_listbox.insert('end', f)

    def add_dir(self):
        try:
            cc_filedir = self.dir_label['text']
            if not cc_filedir:
                raise ValueError('请选择文件夹')
            wavelength = float(self.wavelength_entry.get())
            add_item = str(wavelength)+' | '+cc_filedir
            items = [self.dir_listbox.get(i) for i in range(self.dir_listbox.size())]
            for i in items:
                if i == add_item:
                    return
            self.dir_listbox.insert('end', add_item)
        except Exception as e:
            tk.messagebox.showerror(title='Error', message=str(e))

    def delete_items(self):
        i = self.dir_listbox.curselection()
        while i:
            self.dir_listbox.delete(i[0])
            i = self.dir_listbox.curselection()

    def clean_listbox(self):
        self.dir_listbox.selection_set(0, 'end')
        self.delete_items()

    def select_dir(self):
        self.dir_label['text'] = askdirectory()

    def open_dir(self):
        dirc = self.dir_label['text']
        if not dirc:
            tk.messagebox.showerror(title='Error', message='请选择文件夹')
        else:
            startfile(dirc)

    def manual(self):
        startfile('manual.docx')

    def clean_page(self):
        self.dir_label.pack_forget()
        self.args_label.pack_forget()
        self.args_entry.pack_forget()
        self.wavelength_label.pack_forget()
        self.wavelength_entry.pack_forget()
        self.return_button.pack_forget()
        self.dirbtn_frame.pack_forget()
        self.manual_button.pack_forget()
        self.dirlist_frame.pack_forget()

    def home_page(self):
        self.clean_page()

        self.title_label['text'] = '处理Uvvis数据\n请选择要绘制的曲线类型'
        self.first_button['text'] = '吸光度-波长曲线'
        self.first_button['command'] = self.uvvis_page
        self.second_button['text'] = '浓度变化曲线'
        self.second_button['command'] = self.c_change_page
        self.manual_button.pack(side='bottom', pady=50)

    def uvvis_page(self):
        self.clean_page()
        self.clean_listbox()

        self.title_label['text'] = '绘制Uvvis吸光度-波长曲线'
        self.first_button['text'] = '绘图'
        self.first_button['command'] = self.show_uvvis
        self.second_button['text'] = '导出数据'
        self.second_button['command'] = self.write_uvvis_datas
        self.add_button['command'] = self.add_ascfiles

        self.dirlist_frame.pack(side='top')
        self.args_label.pack(side='top')
        self.args_entry.pack(side='top')
        self.dir_label.pack(side='top', pady=10)
        self.dirbtn_frame.pack(side='top')
        self.return_button.pack(side='left', padx=10)

    def c_change_page(self):
        self.clean_page()
        self.clean_listbox()

        self.title_label['text'] = '绘制浓度变化曲线'
        self.first_button['text'] = '绘图'
        self.first_button['command'] = self.show_cc_figure
        self.second_button['text'] = '导出数据'
        self.second_button['command'] = self.write_cc_datas
        self.add_button['command'] = self.add_dir

        self.dir_label.pack(side='top')
        self.dirbtn_frame.pack(side='top')
        self.wavelength_label.pack(side='top')
        self.wavelength_entry.pack(side='top')
        self.dirlist_frame.pack(side='top')
        self.args_label.pack(side='top')
        self.args_entry.pack(side='top')
        self.return_button.pack(side='left', padx=10)

    def read_ascfiles(self):
        ascfiles = [self.dir_listbox.get(i) for i in range(self.dir_listbox.size())]
        if not ascfiles:
            raise ValueError('请添加asc文件')
        uvvis_datas, splitnames, lens = [], [], []
        for f in ascfiles:
            uvvis_datas.append(uvvis.read_asc(f))
            splitnames.append(split(r'/|\\', f.replace('.asc', '')))
            lens.append(len(splitnames[-1]))
        n = len(ascfiles)
        loop = max(lens)
        for i in range(-1,-loop-1,-1):
            names = ['-'.join(sn[i:]) for sn in splitnames]
            c = Counter(names)
            if len(c) == n:
                # 所有名字只出现过一次，即不同名
                for j in range(n):
                    uvvis_datas[j].name = names[j]
                break
        return uvvis_datas

    def show_uvvis(self):
        try:
            kwargs = input_args(self.args_entry.get())
            uvvis_datas = self.read_ascfiles()
            uvvis.draw_uvvis(uvvis_datas, **kwargs)
            plt.show()
        except Exception as e:
            tk.messagebox.showerror(title='Error', message=str(e))

    def write_uvvis_datas(self):
        try:
            ascdir = self.dir_label['text']
            if not ascdir:
                raise ValueError('请选择文件夹')
            if ascdir[-1] not in ['\\', '/']:
                ascdir += '/'
            xlsx_path = ascdir + 'uvvis_datas.xlsx'
            uvvis_datas = self.read_ascfiles()
            uvvis.write_xlsx(xlsx_path, uvvis_datas)
            tk.messagebox.showinfo(title='Sucess', message='数据已保存至:'+xlsx_path)
        except Exception as e:
            tk.messagebox.showerror(title='Error', message=str(e))

    def read_ccdatas(self):
        cc_datas = []
        items = [self.dir_listbox.get(i) for i in range(self.dir_listbox.size())]
        if not items:
            raise ValueError('请添加asc文件夹')
        for i in items:
            wave, file_dir = i.split(' | ')
            cc_datas.append(uvvis.get_concentration_change(
                uvvis.read_ascdir(file_dir), float(wave), split(r'/|\\', file_dir)[-1]))
        return cc_datas

    def show_cc_figure(self):
        try:
            kwargs = input_args(self.args_entry.get())
            cc_datas = self.read_ccdatas()
            uvvis.draw_concentration_change(cc_datas, **kwargs)
            plt.show()
        except Exception as e:
            tk.messagebox.showerror(title='Error', message=str(e))

    def write_cc_datas(self):
        try:
            cc_filedir = self.dir_label['text']
            if not cc_filedir:
                raise ValueError('请选择文件夹')
            if cc_filedir[-1] not in ['\\', '/']:
                cc_filedir += '/'
            xlsx_path = cc_filedir + 'cc_datas.xlsx'
            cc_datas = self.read_ccdatas()
            uvvis.write_xlsx(xlsx_path, cc_datas)
            tk.messagebox.showinfo(title='Sucess', message='数据已保存至:'+xlsx_path)
        except Exception as e:
            tk.messagebox.showerror(title='Error', message=str(e))

def input_args(s=''):
    l = {}
    exec('kwargs=dict(%s)' % s, globals(), l)
    return l['kwargs']

root = tk.Tk()
app = Application(master=root)
app.mainloop()
