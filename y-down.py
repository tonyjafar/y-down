from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import pafy
import os
import platform
import pydub
import configparser
import multiprocessing


###################################################################################
# DO NOT USE TO DOWNLOAD ILLEGAL CONTENT , IT IS ONLY FOR DOWNLOADING FREE CONTENT#
###################################################################################


class YoutubeDownloader:
    def __init__(self, dir_name=None, config_file=None):
        self.dir_name = dir_name
        self.frame = Frame(root, height=20, relief=SUNKEN)
        self.frame.grid(row=3, columnspan=10, sticky="w")
        self.var = IntVar()
        self.r1 = Radiobutton(root, text='Audio', variable=self.var, value=0)
        self.r1.grid(row=1, column=0, sticky='wn')
        self.r2 = Radiobutton(root, text='Video', variable=self.var, value=1)
        self.r2.grid(row=1, column=1, sticky='wn')
        self.b = None
        self.config_file = config_file
        self.errors = []
        self.win = None
        self.q = multiprocessing.Queue()
        self.p = multiprocessing.Process()
        self.p_l = []
        self.manager = multiprocessing.Manager()
        self.errors = self.manager.list()
        self.check_fun = None
        self.proc_frame = Frame(root, width=100, relief=SUNKEN)
        self.proc_frame.grid(row=4, columnspan=200, sticky='w')
        self.progress = ttk.Progressbar(self.proc_frame, orient="horizontal",
                                        length=700)
        self.progress.pack(fill=X, padx=5)
        self.error = False

    def open_folder(self):
        if platform.system() == 'Windows':
            os.startfile(self.dir_name)
        elif platform.system() == 'Linux':
            os.system('xdg-open "%s"' % self.dir_name)
        elif platform.system() == "Darwin":
            os.system('open "%s"' % self.dir_name)
        else:
            messagebox.showwarning("Warning", "your os is not supported")

    def save_file(self):
        self.dir_name = None
        folder = filedialog.askdirectory(initialdir=os.path.expanduser('~'))
        if folder:
            self.dir_name = folder
        else:
            if self.b:
                self.b.destroy()

    def read_config(self):
        self.config_file = None
        file = filedialog.askopenfilename(initialdir=os.path.expanduser('~'))
        if file:
            self.config_file = file
        else:
            if self.b:
                self.b.destroy()

    def ask_one_multi(self):
        self.win = Toplevel()
        self.win.wm_geometry('300x100')
        self.win.focus()
        self.win.title('What to do?')
        message = 'Download one or multi links'
        Label(self.win, text=message).pack()
        Button(self.win, text='One link', command=self.download_url).pack(side=LEFT)
        Button(self.win, text='Multi links', command=self.download_url_from_file).pack(side=RIGHT)

    def download_url_from_file(self):
        if self.win:
            self.win.destroy()
        self.error = False
        self.frame.destroy()
        self.frame = Frame(root, height=25, relief=SUNKEN)
        self.frame.grid(row=3, columnspan=10, sticky="w")
        l = Label(self.frame, text='Downloading...', fg='blue')
        l.pack(fill=X, padx=5)
        self.proc_frame.destroy()
        self.proc_frame = Frame(root, height=20, relief=SUNKEN)
        self.proc_frame.grid(row=4, columnspan=200, sticky='w')
        self.progress = ttk.Progressbar(self.proc_frame, orient="horizontal",
                                        length=700)
        self.progress.pack(fill=BOTH, padx=5)
        my_links = {}
        self.read_config()
        if self.config_file:
            self.save_file()
        if self.dir_name and self.config_file:
            del self.errors[:]
            self.errors = self.manager.list()
            self.check_fun = 1
            try:
                config = configparser.ConfigParser()
                config.read(self.config_file)
                for name, link in config['links'].items():
                    my_links[name] = link
            except:
                messagebox.showerror('Error', 'Please provide a correct file')
                self.frame.destroy()
                self.frame = Frame(root, height=25, relief=SUNKEN)
                self.frame.grid(row=3, columnspan=10, sticky="w")
                l = Label(self.frame, text='Failed!!!', fg='red')
                l.pack(fill=X, padx=5)
                self.error = True
            if not self.error:
                if self.var.get() == 1:
                    var = 1
                else:
                    var = 0
                for name in my_links:
                    self.q.put(my_links[name])
                for i in range(5):
                    self.p = multiprocessing.Process(target=run, args=(self.q, self.dir_name, var, self.errors,
                                                                       self.check_fun, my_links))
                    self.p_l.append(self.p)
                    self.p.start()
                self.progress.start()
                root.after(500, self.process_queue)
        else:
            l.destroy()
            pass

    def process_queue(self):
        if not self.p.is_alive():
            if self.check_fun == 0:
                self.p.join()
            else:
                for p in self.p_l:
                    p.join()
            self.q.put(self.dir_name)
            self.p = multiprocessing.Process(target=convert, args=(self.q,))
            self.p.start()
            if len(self.errors) > 0:
                self.errors = list(self.errors)
                if self.check_fun == 0:
                    self.progress.stop()
                    messagebox.showerror('Error', '%s' % self.errors[0])
                else:
                    self.progress.stop()
                    messagebox.showerror('Error', 'the following links failed\n%s' % self.errors)
                self.frame.destroy()
                self.frame = Frame(root, height=25, relief=SUNKEN)
                self.frame.grid(row=3, columnspan=10, sticky="w")
                l = Label(self.frame, text='Failed!!!', fg='red')
                l.pack(fill=X, padx=5)
            else:
                self.progress.stop()
                self.frame.destroy()
                self.frame = Frame(root, height=25, relief=SUNKEN)
                self.frame.grid(row=3, columnspan=10, sticky="w")
                l = Label(self.frame, text='Success!!!', fg='green')
                l.pack(fill=X, padx=5)
                self.b = Button(root, text='Open Folder', command=self.open_folder)
                self.b.grid(row=0, column=3, sticky='ws')
        else:
            root.after(500, self.process_queue)

    def download_url(self):
        if self.win:
            self.win.destroy()
        self.frame.destroy()
        self.frame = Frame(root, height=25, relief=SUNKEN)
        self.frame.grid(row=3, columnspan=10, sticky="w")
        l = Label(self.frame, text='Downloading...', fg='blue')
        l.pack(fill=X, padx=5)
        self.proc_frame.destroy()
        self.proc_frame = Frame(root, width=100, relief=SUNKEN)
        self.proc_frame.grid(row=4, columnspan=200, sticky='w')
        self.progress = ttk.Progressbar(self.proc_frame, orient="horizontal",
                                        length=700)
        self.progress.pack(fill=BOTH, padx=5)
        self.save_file()
        if self.var.get() == 1:
            var = 1
        else:
            var = 0
        if self.dir_name:
            del self.errors[:]
            self.errors = self.manager.list()
            self.check_fun = 0
            myUrl = e1.get()
            # get("1.0",'end-1c')
            self.q.put(myUrl)
            self.p = multiprocessing.Process(target=run, args=(self.q, self.dir_name, var, self.errors, self.check_fun))
            self.p_l.append(self.p)
            self.p.start()
            self.progress.start()
            root.after(500, self.process_queue)
        else:
            l.destroy()
            pass


def run(q, dir_name, var, errors, check_fun, my_links=None):
    while True:
        if q.empty():
            break
        else:
            url = q.get()
            if my_links:
                for key, value in my_links.items():
                    if url == value:
                        name = key
            try:
                video = pafy.new(url)
                audio = video.audiostreams
                if var == 1:
                    best = video.getbest()
                    best.download(filepath=dir_name)
                else:
                    for a in audio:
                        if a.extension == 'm4a':
                            myAudio = a
                        myAudio.download(filepath=dir_name)
            except ValueError:
                if check_fun == 0:
                    errors.append('Please insert a valid link')
                else:
                    errors.append(name)
            except:
                if check_fun == 0:
                    errors.append('Error occurred check Internet and/or folder permission.')
                else:
                    errors.append(name)


def convert(q):
    while True:
        if q.empty():
            break
        else:
            dir_name = q.get()
            for file in os.listdir(dir_name):
                file = os.path.join(dir_name, file)
                if os.path.isfile(file) and file.endswith("m4a"):
                    wma = pydub.AudioSegment.from_file(file, "m4a")
                    new_name = file.replace("m4a", "mp3")
                    wma.export(new_name, "mp3")
                    os.remove(file)

if __name__ == '__main__':
    multiprocessing.freeze_support()
    root = Tk()
    root.title('Youtube Downloader')
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(1, weight=1)

    menu = Menu(root)
    file_menu = Menu(menu, tearoff=0)
    about_menu = Menu(menu, tearoff=0)
    menu.add_cascade(label='File', menu=file_menu)
    menu.add_cascade(label='About', menu=about_menu)
    root.config(menu=menu)


    def display_about(event=None):
        messagebox.showinfo("About",
                            "Created by Tony Jafar\nMob:+49 (0)17663126527")


    def exit_app(event=None):
        if messagebox.askokcancel("Quit?", "Really quit?"):
            root.destroy()


    def select_all(event=None):
            e1.select_range(0, END)
            return "break"


    def download(event=None):
        myapp.download_url()
        return 'break'


    def download_from_file(event=None):
        myapp.download_url_from_file()
        return 'break'


    def ask_what_to_do(event=None):
        myapp.ask_one_multi()
        return 'break'

    file_menu.add_command(label='Download', accelerator='Control+D', command=download)
    file_menu.add_command(label='Insert Config File', accelerator='Control+I', command=download_from_file)
    about_menu.add_command(label='About', command=display_about)
    myapp = YoutubeDownloader()
    Label(root, text='Enter URL', fg='blue').grid(row=0, column=0, sticky='w')
    e1 = Entry(root, width=100)
    e1.grid(row=0, column=1, sticky='we')
    e1.focus()
    Button(root, text='File', command=myapp.download_url_from_file
           ).grid(row=0, column=2, sticky='ws')
    Button(root, text='Download', command=myapp.download_url
           ).grid(row=2, column=0, sticky='ws')
    Button(root, text='Exit', command=exit_app
           ).grid(row=2, column=1, sticky='ws')
    root.protocol('WM_DELETE_WINDOW', exit_app)
    e1.bind('<Control-A>', select_all)
    e1.bind('<Control-a>', select_all)
    e1.bind('<Control-D>', download)
    e1.bind('<Control-d>', download)
    e1.bind('<Control-I>', download_from_file)
    e1.bind('<Control-i>', download_from_file)
    e1.bind('<Return>', ask_what_to_do)
    root.mainloop()
