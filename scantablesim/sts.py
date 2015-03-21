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
    self.table_cells = [0 for i in range(0,self.cell_x)]
    self.camera_index = 0

  def action(self,action):
    """Execute an action with the virtual camera"""
    pass

  def cells_total(self):
    """How many cells(e.g. areas) are available on the table?"""
    pass

  def cells_discovered(self):
    """How many cells (e.g. areas) have been discovered/scanned by the camera?"""
    pass

  def cells_discovered_percentage(self):
    """cells_discovered / cells_total"""
    return self.cells_discovered / self.cells_total

  def cell_map(self):
    """Get the data structure behind the table cells"""
    return self.table_cells
