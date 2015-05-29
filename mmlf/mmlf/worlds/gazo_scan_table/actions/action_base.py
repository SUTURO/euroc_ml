import abc


class ActionBase(object):
    __metaclass__ = abc.ABCMeta

    name = None

    @abc.abstractmethod
    def __call__(self, environment):
        pass