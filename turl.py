import tkinter as tk
from tkinter import scrolledtext
from tkinter import simpledialog
from tkinter import messagebox
from tkinter.filedialog import askopenfilename

import os, sys, subprocess, threading, fcntl

import platform

from time import sleep

root = tk.Tk()

output = None
file_button = None
file_text = None
start_button = None

turl = subprocess.Popen

turlpath = "./turl"
if platform.system() == "Windows":
    turlpath = "turl.exe"

filepath = ""

def choosefile():
    global filepath
    global start_button
    global file_text
    filetypes = (("Turl files", "*.turl"),
                ("All files", "*.*"))
    filepath = askopenfilename(filetypes=filetypes, initialdir="")
    if filepath == "":
        file_text.config(text = "No File Selected")
        start_button['state'] = tk.DISABLED
    else:
        file_text.config(text = os.path.basename(os.path.normpath(filepath)))
        start_button['state'] = tk.NORMAL 

debug = False

def debugtoggle():
    global debug
    debug = not debug

ready = False

start = False

def startturl():
    global start
    start = True

def turlmain():
    global turl
    global ready
    global debug
    global start
    global start_button
    while True:
        if start:
            start = False
            start_button["state"] = tk.DISABLED
            command = [turlpath,filepath]
            if debug:
                command = [turlpath,filepath,"debug"]
                turloutput("[Started Debug Turl Program]" + filepath + "\n")
            else:
                turloutput("[Started Turl Program]" + filepath + "\n")
            try:
                turl = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                ready = True
                while turl.poll() == None:
                    pass
                ready = False
            except FileNotFoundError:
                messagebox.showerror(title = "Turl Not Found!", message = "No Turl Executable Was Found in Current Directory!\nGet Turl from https://bit-turtle.github.io/turl.html")

            start_button["state"] = tk.NORMAL

tthread = threading.Thread(target=turlmain)
tthread.daemon = True
tthread.start()

def getoutput():
    while True:
        try:
            fcntl.fcntl(turl.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)        
            output = turl.stdout.read(1024)
            if output != None and output != "":
                turloutput(output.decode())
                done = False
            else:
                done = True
        except:
            pass


othread = threading.Thread(target=getoutput)
othread.daemon = True
othread.start()

def sendinput():
    global done
    global ready
    if ready:
        value = simpledialog.askstring("Enter Input", "Enter Input:")
        fcntl.fcntl(turl.stdin.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
        turloutput(value + "\n")
        done = False
        turl.stdin.write(value.encode()+b'\n')
        turl.stdin.flush()
    else:
        messagebox.showwarning(title = "No Turl Program Running", message = "There is no Turl Program running to take input")

def turloutput(text):
    global output
    output.insert(tk.END,text)
    output.yview(tk.END)
    root.update()

def clearoutput():
    global output
    output.delete("1.0", tk.END)
    output.yview(tk.END)
    root.update()

root.title("Turl GUI")
root.geometry("950x512")
root.resizable(False,False)
tk.Label(root, text = "Turl GUI!", font = "Helvetica 18 bold").grid(row = 0, column = 3, rowspan = 2)
output = scrolledtext.ScrolledText(root, wrap = tk.WORD, height = 20, width = 60)
output.grid(row = 2, column = 3)
file_button = tk.Button(root, text = "Choose File", command = choosefile)
file_button.grid(row = 0, column = 1)
file_text = tk.Label(root, text = "No File Selected", width = 15, height = 1)
file_text.grid(row = 0, column = 2)
start_button = tk.Button(root, text = "Run Program", command = startturl)
start_button.grid(row = 1, column = 1)
tk.Button(text = "Enter Input", command = sendinput).grid(row = 2, column = 1)
tk.Button(text = "Clear Output", command = clearoutput).grid(row = 2, column = 2)
tk.Checkbutton(root, text = "Debug Mode", command = debugtoggle).grid(row = 1, column = 2)
root.mainloop()
