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

# class ScanTableAction(object):
class ScanTableAction:
  """An action for the virtual camera"""

  MOVE_LEFT_BY_1    = 1
  MOVE_LEFT_BY_5    = 2
  MOVE_LEFT_BY_10   = 3
  MOVE_RIGHT_BY_1   = 4
  MOVE_RIGHT_BY_5   = 5
  MOVE_RIGHT_BY_10  = 6
  SCAN_TABLE        = 7


class ScanTableSimulation(object):
  """Main class for the simulation"""
  CELL_UNKNOWN = 0
  CELL_DISCOVERED = 1

  def __init__(self):
    super(ScanTableSimulation, self).__init__()
    self.cell_x = 50 # make fifty cells in the x direction
                     # maybe everything will be extended with 2 dimensions
    self.cell_y = 1 # make fifty cells in the x direction
                     # maybe everything will be extended with 2 dimensions
    self.table_cells = [self.CELL_UNKNOWN for i in range(0,self.cell_x)]
    self.camera_index = 0 # Where is the camera looking at?
    self.camera_fov_width = 2 # How many pixels can the camera see to the left and right? 
                              # A value of 2 means, that it can see the pixel 
                              # at self.camera_index and 2 pixels left plus 2 pixel right from it
    self.simulate_delay_in_action = False
    self.action_delay_time = 0

  def set_simulate_delay_in_action(self, b):
    self.simulate_delay_in_action = b

  def set_action_delay_time_in_s(self, s):
    self.action_delay_time = s

  def update_if_idx_valid(self,idx,value):
    """Write a value into self.table_cells[idx], if the idx is in bounds"""
    if idx in range(0,len(self.table_cells)):
        self.table_cells[idx] = value
    pass

  def scan_table(self):
    """Execute the SCAN_TABLE action. Should be execute from action()"""
    # Always scan the the camera focus
    self.update_if_idx_valid(self.camera_index, self.CELL_DISCOVERED)

    # Discover to the left
    for i in range(self.camera_index - self.camera_fov_width, self.camera_index):
      self.update_if_idx_valid(i,self.CELL_DISCOVERED)

    # Discover to the right
    for i in range(self.camera_index+1, self.camera_index + 1 + self.camera_fov_width):
      print "update" + str(i)
      self.update_if_idx_valid(i,self.CELL_DISCOVERED)


  def action(self,action):
    """Execute an action with the virtual camera"""
    if action == ScanTableAction.SCAN_TABLE:
      self.scan_table()
    elif action == ScanTableAction.MOVE_LEFT_BY_1:
      if self.camera_index >= 1:
        self.camera_index -= 1
    elif action == ScanTableAction.MOVE_LEFT_BY_5:
      if self.camera_index >= 5:
        self.camera_index -= 5
    elif action == ScanTableAction.MOVE_LEFT_BY_10:
      if self.camera_index >= 10:
        self.camera_index -= 10
    elif action == ScanTableAction.MOVE_RIGHT_BY_1:
      if self.camera_index < self.cell_x-1:
        self.camera_index += 1
    elif action == ScanTableAction.MOVE_RIGHT_BY_5:
      if self.camera_index < self.cell_x-5:
        self.camera_index += 5
    elif action == ScanTableAction.MOVE_RIGHT_BY_10:
      if self.camera_index < self.cell_x-10:
        self.camera_index += 10
    if self.simulate_delay_in_action:
      time.sleep(self.action_delay_time)
    pass

  def cells_total(self):
    """How many cells(e.g. areas) are available on the table?"""
    return len(self.table_cells)

  def cells_discovered(self):
    """How many cells (e.g. areas) have been discovered/scanned by the camera?"""
    discovered = 0
    for c in self.table_cells:
      if c == self.CELL_DISCOVERED:
        discovered += 1
    return discovered

  def cells_discovered_percentage(self):
    """cells_discovered / cells_total"""
    return self.cells_discovered / self.cells_total

  def cell_map(self):
    """Get the data structure behind the table cells"""
    return self.table_cells
