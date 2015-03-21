# -*- coding: utf-8 -*-

# This library will provide a synthetic benchmark and playground
# for Machine Learning Algorithms.
# 
# It simulates a table, that can be scanned by a camera, that's pointing towards it.
# By selecting one of the available actions, you can 
# control that camera to scan a different area of the table
# You can get the ratio of scanned areas on the table, to check 
# how well you've discovered everything on the table.
#
# This provides an example scenario for a learning
# agent, that is supposed to find out
# the best action sequence, to scan the table in a minimum amount of time

# import Tkinter as Tk
from Tkinter import *
from thread import start_new_thread
import time
from sts import ScanTableSimulation, ScanTableAction
# import sts

# Tkinter doesn't like to be run
# in thread, so we have to move our magic 
# to a worker thread ...
def worker_thread(gui,sts):
    print "Started worker"
    while 1:
      print "Sleeping Worker"
      time.sleep(4)
      gui.w.itemconfig(gui.rect,fill="yellow") 

class GUI:
    def __init__(self, master):

        frame = Frame(master)
        frame.pack()

        self.button = Button(
            frame, text="QUIT", fg="red", command=frame.quit
            )
        self.button.pack(side=LEFT)

        self.hi_there = Button(frame, text="Hello", command=self.say_hi)
        self.hi_there.pack(side=LEFT)

        self.w = Canvas(frame, width=600, height=100)
        self.w.pack()
        self.rect = self.w.create_rectangle(50, 25, 150, 75, fill="blue")

    def say_hi(self):
        print "hi there, everyone!"
        self.w.itemconfig(self.rect,fill="red") 


root = Tk()
sts = ScanTableSimulation()
print len(sts.cell_map() )

gui = GUI(root)
start_new_thread(worker_thread,(gui,sts,))

root.mainloop()
root.destroy() 
