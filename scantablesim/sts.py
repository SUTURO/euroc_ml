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

import time
class ScanTableAction:
  """An action for the virtual camera"""

  MOVE_LEFT_BY_1    = 0
  MOVE_LEFT_BY_5    = 1
  MOVE_LEFT_BY_10   = 2
  MOVE_RIGHT_BY_1   = 3
  MOVE_RIGHT_BY_5   = 4
  MOVE_RIGHT_BY_10  = 5
  SCAN_TABLE        = 6


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
    self.action_delay_time = 1 # delay 1 sec by default, if enabled
    self.last_executed_action = -1
    self.observer = None 
    self.reset_update_flag()

  def update_occured(self):
    """Returns True, if the cells has been updated lately or the camera index changed and reset_update_flag() has not been called since then. Right now, this flag will be set everytime an action will be executed"""
    return self.state_update

  def reset_update_flag(self):
    """Reset the flag indicating cell changes to False"""
    self.state_update = False
    pass

  def reset_cells_and_camera(self):
    """docstring for reset_cells_and_camera"""
    # print "-------------Resetting STS---------------"
    # self.table_cells[0] = self.CELL_UNKNOWN
    self.table_cells = [self.CELL_UNKNOWN for i in range(0,self.cell_x)]
    # for a in self.table_cells:
    #   print(a)
    self.camera_index = 0 # Where is the camera looking at?
    self.state_update = True
    pass

  def set_observer(self,observer):
    """Set an observer. Most likely the GUI in our case"""
    self.observer = observer
    pass

  def update_observer(self):
    """Call the update method on the observer"""
    if self.observer is not None:
      self.observer.update()

    pass

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
      self.update_if_idx_valid(i,self.CELL_DISCOVERED)

  def map_action_id_to_str(self,aid):
    if aid == ScanTableAction.MOVE_LEFT_BY_1:
      return "ML1"
    if aid == ScanTableAction.MOVE_LEFT_BY_5:
      return "ML5"
    if aid == ScanTableAction.MOVE_LEFT_BY_10:
      return "ML10"
    if aid == ScanTableAction.MOVE_RIGHT_BY_1:
      return "MR1"
    if aid == ScanTableAction.MOVE_RIGHT_BY_5:
      return "MR5"
    if aid == ScanTableAction.MOVE_RIGHT_BY_10:
      return "MR10"
    if aid == ScanTableAction.SCAN_TABLE:
      return "ST"
    return "ERR"

  def last_action(self):
    """Get the last ScanTableAction, that has been passed to self.action"""
    if self.last_executed_action == ScanTableAction.MOVE_LEFT_BY_1:
      return "ML1"
    if self.last_executed_action == ScanTableAction.MOVE_LEFT_BY_5:
      return "ML5"
    if self.last_executed_action == ScanTableAction.MOVE_LEFT_BY_10:
      return "ML10"
    if self.last_executed_action == ScanTableAction.MOVE_RIGHT_BY_1:
      return "MR1"
    if self.last_executed_action == ScanTableAction.MOVE_RIGHT_BY_5:
      return "MR5"
    if self.last_executed_action == ScanTableAction.MOVE_RIGHT_BY_10:
      return "MR10"
    if self.last_executed_action == ScanTableAction.SCAN_TABLE:
      return "ST"
    return "ERR"

  def action(self,action):
    """Execute an action with the virtual camera"""
    print "Executing " + self.map_action_id_to_str(action) + "at camera="+str(self.camera_index)

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

    self.state_update = True
    self.last_executed_action = action
    if self.simulate_delay_in_action:
      time.sleep(self.action_delay_time)
    # self.update_observer()
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
