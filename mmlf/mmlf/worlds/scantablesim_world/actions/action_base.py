import abc


class ActionBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __call__(self, environment):
        pass

class SimSimAction(object):

    def __init__(self):
        pass

    def moveLeft(self, env):
        env.move_to(self.pos_x, self.pos_y)
        pass

    def moveRight(self, env):
        pass

    def moveUp(self, env):
        pass

    def moveDown(self, env):
       pass

    def scan(self, env):
        pass