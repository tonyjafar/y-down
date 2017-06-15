from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import pafy
import os
import platform
import pydub
import configparser
import multiprocessing
import youtube_dl


###################################################################################
# DO NOT USE TO DOWNLOAD ILLEGAL CONTENT , IT IS ONLY FOR DOWNLOADING FREE CONTENT#
###################################################################################


class YoutubeDownloader:
    def __init__(self, dir_name=None, config_file=None):
        self.dir_name = dir_name
        self.frame = Frame(root, height=25, relief=SUNKEN)
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

    def update_list(self, link):
        self.errors.append(link)

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
        self.frame.destroy()
        self.frame = Frame(root, height=25, relief=SUNKEN)
        self.frame.grid(row=3, columnspan=10, sticky="w")
        l = Label(self.frame, text='Downloading...', fg='blue')
        l.pack(fill=X, padx=5)
        my_links = {}
        self.read_config()
        if self.config_file:
            self.save_file()
        if self.dir_name and self.config_file:
            config = configparser.ConfigParser()
            config.read(self.config_file)
            for name, link in config['links'].items():
                my_links[name] = link
            if self.var.get() == 1:
                var = 1
            else:
                var = 0
            for name in my_links:
                self.q.put(my_links[name])
            for i in range(5):
                self.p = multiprocessing.Process(target=run, args=(self.q, self.dir_name, var, self.errors))
                self.p_l.append(self.p)
                self.p.start()
            root.after(500, self.process_queue)
        else:
            l.destroy()
            pass
        
    def process_queue(self):
        if not self.p.is_alive():
            for p in self.p_l:
                p.join()
            if len(self.errors) > 0:
                self.errors = list(self.errors)
                messagebox.showerror('Error', 'the following links failed\n%s' % self.errors)
                self.frame.destroy()
                self.frame = Frame(root, height=25, relief=SUNKEN)
                self.frame.grid(row=3, columnspan=10, sticky="w")
                l = Label(self.frame, text='Failed!!!', fg='red')
            else:
                self.frame.destroy()
                self.frame = Frame(root, height=25, relief=SUNKEN)
                self.frame.grid(row=3, columnspan=10, sticky="w")
                l = Label(self.frame, text='Success!!!', fg='green')
                l.pack(fill=X, padx=5)
                l.pack(fill=X, padx=5)
                self.b = Button(root, text='Open Folder', command=self.open_folder)
                self.b.grid(row=0, column=3, sticky='ws')
        else:
            root.after(500, self.process_queue)

    def download_url(self):
        try:
            if self.win:
                self.win.destroy()
            self.frame.destroy()
            self.frame = Frame(root, height=25, relief=SUNKEN)
            self.frame.grid(row=3, columnspan=10, sticky="w")
            l = Label(self.frame, text='Downloading...', fg='blue')
            l.pack(fill=X, padx=5)
            self.save_file()

            if self.dir_name:
                myUrl = e1.get()
                # get("1.0",'end-1c')
                video = pafy.new(myUrl)
                audio = video.audiostreams
                if self.var.get() == 1:
                    best = video.getbest()
                    best.download(filepath=self.dir_name)
                else:
                    for a in audio:
                        if a.extension == 'm4a':
                            myAudio = a
                            myAudio.download(filepath=self.dir_name)
                            os.chdir(self.dir_name)
                            old_name = video.title + '.m4a'
                            new_name = video.title + '.mp3'

                            wma = pydub.AudioSegment.from_file(old_name, "m4a")
                            os.chdir(self.dir_name)
                            wma.export(new_name, "mp3")
                            os.chdir(self.dir_name)
                            os.remove(old_name)
                l.destroy()
                l = Label(self.frame, text='Success!!', fg='green')
                l.pack(fill=X, padx=5)

                self.b = Button(root, text='Open Folder', command=self.open_folder)
                self.b.grid(row=0, column=3, sticky='ws')
            else:
                l.destroy()
                pass
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid URL")
            l.destroy()
            Label(self.frame, text='Failed!!', fg='red').pack(fill=X, padx=5)
        except:
            messagebox.showerror("Error", "Please check the URL and your Internet connection\n"
                                          "or ask the supplier for updated Version")
            l.destroy()
            Label(self.frame, text='Failed!!', fg='red').pack(fill=X, padx=5)


def run(q, dir_name, var, errors):
    while True:
        if q.empty():
            break
        else:
            url = q.get()
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
                            os.chdir(dir_name)
                            old_name = pafy.new(url, ydl_opts='-i').title + '.m4a'
                            new_name = video.title + '.mp3'
                            wma = pydub.AudioSegment.from_file(old_name, "m4a")
                            os.chdir(dir_name)
                            wma.export(new_name, "mp3")
                            os.chdir(dir_name)
                            os.remove(old_name)
            except:
                errors.append(url)


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
