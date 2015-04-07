import abc
import numpy


class ActionBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def perform(self, environment):
        raise NotImplementedError()


class ScanTableAction(ActionBase):

    def perform(self, environment):
        old = environment.discovered_cells
        environment.scan_table()
        new = environment.discovered_cells
        fov_h, fov_w = environment.camera_fov
        return -1 + (2 / float((fov_h + 1)  * (fov_w + 1))) * (new - old)

    def __str__(self):
        return "Scan Table"


class MoveToAction(ActionBase):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def perform(self, environment):
        idx = numpy.asarray(environment.camera_index, dtype=int)
        environment.move_to(self.x, self.y)
        new_idx = numpy.asarray(environment.camera_index, dtype=int)
        max_idx = numpy.asarray(environment.cell_map.shape, dtype=int)
        max_norm = numpy.linalg.norm(max_idx)

        if (idx == new_idx).all():
            return -1
        else:
            return (1 / max_norm * numpy.linalg.norm(new_idx - idx)) * -1

    def __str__(self):
        return "Move To %s / %s" % (self.x, self.y)


class MoveStepsAction(MoveToAction):

    def perform(self, environment):
        x, y = environment.camera_index
        self.x += x
        self.y += y
        super(MoveStepsAction, self).perform(environment)


class MoveLeftAction(MoveStepsAction):
    def __init__(self):
        super(MoveLeftAction, self).__init__(0 , -1)

    def __str__(self):
        return "Move left"


class MoveRightAction(MoveStepsAction):
    def __init__(self):
        super(MoveRightAction, self).__init__(0, 1)

    def __str__(self):
        return "Move right"

class MoveUpAction(MoveStepsAction):
    def __init__(self):
        super(MoveUpAction, self).__init__(-1, 0)

    def __str__(self):
        return "Move up"


class MoveDownAction(MoveStepsAction):
    def __init__(self):
        super(MoveStepsAction, self).__init__(1 , 0)

    def __str__(self):
        return "Move down"
