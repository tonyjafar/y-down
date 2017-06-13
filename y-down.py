from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import pafy
import os
import platform
import pydub
import configparser
import threading
import time
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

    def download_url_from_file(self):
        try:
            self.frame.destroy()
            self.frame = Frame(root, height=25, relief=SUNKEN)
            self.frame.grid(row=3, columnspan=10, sticky="w")
            l = Label(self.frame, text='Downloading...', fg='blue')
            l.pack(fill=X, padx=5)
            my_links = {}
            self.read_config()
            self.save_file()
            threads = []

            if self.dir_name and self.config_file:
                config = configparser.ConfigParser()
                config.read(self.config_file)
                for name, link in config['links'].items():
                    my_links[name] = link
                for name in my_links:
                    t = ThreadedTask(my_links[name], self.dir_name)
                    threads += [t]
                    t.start()
                for x in threads:
                    x.join()
                while True:
                    if t.is_alive():
                        time.sleep(1)
                    else:
                        break
                if len(self.errors) > 0:
                    messagebox.showerror("Error", "the following links failed\n%s" % self.errors)
                    l.destroy()
                    Label(self.frame, text='Failed!!', fg='red').pack(fill=X, padx=5)
                else:
                    l.destroy()
                    l = Label(self.frame, text='Success!!', fg='green')
                    l.pack(fill=X, padx=5)

                    self.b = Button(root, text='Open Folder', command=self.open_folder)
                    self.b.grid(row=0, column=3, sticky='ws')
            else:
                l.destroy()
                pass
        except:
            messagebox.showerror("Error", "Please check the Config file and your Internet connection\n"
                                          "or ask the supplier for updated Version")
            l.destroy()
            Label(self.frame, text='Failed!!', fg='red').pack(fill=X, padx=5)

    def download_url(self):
        try:
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
                            if platform.system() == 'Windows':
                                os.rename(old_name, new_name)
                            else:
                                wma = pydub.AudioSegment.from_file(old_name, "m4a")
                                os.chdir(self.dir_name)
                                wma.export(new_name, "mp3")
                                os.chdir(self.dir_name)
                                os.remove(old_name)
                l.destroy()
                l = Label(self.frame, text='Success!!', fg='green')
                l.pack(fill=X, padx=5)

                self.b = Button(root, text='Open Folder', command=self.open_folder)
                self.b.grid(row=0, column=2, sticky='ws')
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


class ThreadedTask(threading.Thread):
    def __init__(self, url, dir_name):
        threading.Thread.__init__(self)
        self.url = url
        self.dir_name = dir_name

    def run(self):
        try:
            video = pafy.new(self.url)
            audio = video.audiostreams
            for a in audio:
                if a.extension == 'm4a':
                    myAudio = a
                    myAudio.download(filepath=self.dir_name)
                    os.chdir(self.dir_name)
                    old_name = video.title + '.m4a'
                    new_name = video.title + '.mp3'
                    if platform.system() == 'Windows':
                        os.rename(old_name, new_name)
                    else:
                        wma = pydub.AudioSegment.from_file(old_name, "m4a")
                        os.chdir(self.dir_name)
                        wma.export(new_name, "mp3")
                        os.chdir(self.dir_name)
                        os.remove(old_name)
        except Exception:
            myapp.update_list(self.url)

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


file_menu.add_command(label='Download', accelerator='Control+D', command=download)
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
e1.bind('<Return>', download)
root.mainloop()

