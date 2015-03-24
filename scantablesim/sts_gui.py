from Tkinter import *
from sts import ScanTableSimulation, ScanTableAction
import sys

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
        self.last_action = Label(frame, text="Action: "+sts.last_action())
        self.total_cell_label.pack()
        self.discovered_cell_label.pack()
        self.last_action.pack()
        self.init_cells()
        self.update_timer()

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

    def update_timer(self):
      """update_timer will be called every 100 millseconds and update the GUI if something changed in self.sts"""
      if self.sts.update_occured():
        self.update()
        self.sts.reset_update_flag()

      self.frame.after(100,self.update_timer)
      pass

    def update(self):
      self.update_cells()
      self.total_cell_label.config(text = str( self.sts.cells_total() )+" cells total" )
      self.discovered_cell_label.config(text = str( self.sts.cells_discovered() )+" cells discovered")
      self.last_action.config(text="Action: "+self.sts.last_action())
      self.total_cell_label.pack()
      self.discovered_cell_label.pack()
      self.last_action.pack()


    def update_cells(self):
        """update the table cells in the gui according cell_map() from ScanTableSimulation"""
        # print "Updating cells in GUI"
        x = self.sts.cell_x
        self.table_cells = self.sts.cell_map()
        for i in range(0,x):
          if self.sts.camera_index == i:
            fill_color = "black"
          else:
            fill_color = self.get_fill_color_for_cell(self.table_cells[i])

          self.cell_canvas.itemconfig(self.rect[i],fill=fill_color) 
        # print " "
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
          if self.sts.camera_index == i:
            fill_color = "black"
          else:
            fill_color = self.get_fill_color_for_cell(self.table_cells[i])

          self.rect.append(self.cell_canvas.create_rectangle((i*cell_width)+ i*margin, 0, (i*cell_width)+i*margin+cell_width, 25, fill=fill_color))


