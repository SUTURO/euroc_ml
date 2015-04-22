from Tkinter import *


class GUI:
    CANVAS_WIDTH = 600
    CANVAS_HEIGHT = 600

    def __init__(self, master, env):
        self.env = env
        self.frame = master
        frame = Frame(master)
        frame.pack()

        self.button = Button(
            frame, text="QUIT", fg="red", command=frame.quit
            )
        self.button.pack(side=LEFT)

        self.hi_there = Button(frame, text="Hello", command=self.say_hi)
        self.hi_there.pack(side=LEFT)
        self.discovered_cell_label = Label(frame, text="%f%% cells discovered" % env.discovered_percentage)
        self.discovered_cell_label.pack()
        self.init_cells()
        self.update_timer()

    def say_hi(self):
        print "hi there, everyone!"
        self.cell_canvas.itemconfig(self.rect[0],fill="red") 

    def get_fill_color_for_cell(self, cell_value):
        fill_color = "blue"
        if not cell_value:
          fill_color = "white"
        elif cell_value:
          fill_color = "green"
        return fill_color

    def update_timer(self):
        """update_timer will be called every 100 millseconds and update the GUI if something changed in self.sts"""
        self.update()
        self.frame.after(100,self.update_timer)

    def update(self):
        self.update_cells()
        self.discovered_cell_label.config(text="%.2f%% cells discovered" % self.env.discovered_percentage)
        self.discovered_cell_label.pack()

    def update_cells(self):
        """update the table cells in the gui according cell_map() from ScanTableSimulation"""
        # print "Updating cells in GUI"
        rows, cols = self.env.cell_map.shape
        self.table_cells = self.env.cell_map
        for x in range(rows):
            for y in range(cols):
                if self.env.camera_at_position(x, y):
                    fill_color = "black"
                else:
                    fill_color = self.get_fill_color_for_cell(self.table_cells[x,y])
                self.cell_canvas.itemconfig(self.rect[x][y],fill=fill_color)

    def init_cells(self):
        self.cell_canvas = Canvas(self.frame, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT)
        self.cell_canvas.pack()

        # Get the dimensions of the table and calculate the box sizes
        rows, cols = self.env.cell_map.shape
        margin = 2 # margin between cells
        cell_width  = (self.CANVAS_WIDTH  / cols ) - margin
        cell_height = 25  # (self.CANVAS_HEIGHT / rows ) - margin
        self.rect = []
        self.table_cells = self.env.cell_map

        for y in range(rows):
            row = []
            for x in range(cols):
                if self.env.camera_at_position(x, y):
                    fill_color = "black"
                else:
                    fill_color = self.get_fill_color_for_cell(self.table_cells[y,x])
                row.append(self.cell_canvas.create_rectangle((x * cell_width) + x * margin, y * cell_height + y * margin, (x * cell_width)+ x * margin + cell_width, y * cell_height + y * margin + cell_height, fill=fill_color))
            self.rect.append(row)

