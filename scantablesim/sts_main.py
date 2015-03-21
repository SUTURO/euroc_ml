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
      time.sleep(1)
      sts.action(ScanTableAction.MOVE_RIGHT_BY_5)
      sts.action(ScanTableAction.SCAN_TABLE)
      gui.update()
      # gui.cell_canvas.itemconfig(gui.rect[0],fill="yellow") 
      

class GUI:
    CANVAS_WIDTH = 600
    CANVAS_HEIGHT = 600

    def __init__(self, master, sts):
        self.sts = sts
        self.frame = master
        frame = Frame(master)
        frame.pack()

        self.button = Button(
            frame, text="QUIT", fg="red", command=frame.quit
            )
        self.button.pack(side=LEFT)

        self.hi_there = Button(frame, text="Hello", command=self.say_hi)
        self.hi_there.pack(side=LEFT)
        self.total_cell_label = Label(frame, text=str( sts.cells_total() )+" cells total" )
        self.discovered_cell_label = Label(frame, text=str( sts.cells_discovered() )+" cells discovered")
        self.total_cell_label.pack()
        self.discovered_cell_label.pack()
        self.init_cells()


    def say_hi(self):
        print "hi there, everyone!"
        self.cell_canvas.itemconfig(self.rect[0],fill="red") 

    def get_fill_color_for_cell(self, cell_value):
        fill_color = "blue"
        if cell_value == ScanTableSimulation.CELL_UNKNOWN:
          fill_color = "white"
        if cell_value == ScanTableSimulation.CELL_DISCOVERED:
          fill_color = "green"
        return fill_color

    def update(self):
      self.update_cells()
      self.total_cell_label.config(text = str( sts.cells_total() )+" cells total" )
      print sts.cells_discovered()
      self.discovered_cell_label.config(text = str( sts.cells_discovered() )+" cells discovered")

    def update_cells(self):
        """update the table cells in the gui according cell_map() from ScanTableSimulation"""
        x = self.sts.cell_x
        for i in range(0,x):
          fill_color = self.get_fill_color_for_cell(self.table_cells[i])
          self.cell_canvas.itemconfig(gui.rect[i],fill=fill_color) 
        pass

    def init_cells(self):
        self.cell_canvas = Canvas(self.frame, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT)
        self.cell_canvas.pack()

        # Get the dimensions of the table and calculate the box sizes
        x = self.sts.cell_x
        y = self.sts.cell_y
        margin = 2 # margin between cells
        cell_width  = (self.CANVAS_WIDTH  / x ) - margin 
        cell_height = (self.CANVAS_HEIGHT / y ) - margin
        self.rect = []
        self.table_cells = self.sts.cell_map()

        for i in range(0,x):
          fill_color = self.get_fill_color_for_cell(self.table_cells[i])
  
          self.rect.append(self.cell_canvas.create_rectangle((i*cell_width)+ i*margin, 0, (i*cell_width)+i*margin+cell_width, 25, fill=fill_color))



root = Tk()
sts = ScanTableSimulation()
print len(sts.cell_map() )

gui = GUI(root,sts)
start_new_thread(worker_thread,(gui,sts,))

root.mainloop()
root.destroy() 
