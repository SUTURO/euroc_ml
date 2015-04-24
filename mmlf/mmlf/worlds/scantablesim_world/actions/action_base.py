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
        (x,y) = env.camera_index
        self.move_to(x, y-1,env )
        pass

    def moveRight(self, env):
        (x,y) = env.camera_index
        self.move_to(x, y+1,env )
        pass

    def moveUp(self, env):
        (x,y) = env.camera_index
        self.move_to(x+1, y,env )
        pass

    def moveDown(self, env):
        (x,y) = env.camera_index
        self.move_to(x-1, y,env )
        pass

    def scan(self, env):
        return self.scan_table(env)
        pass

    def move_to(self, x, y, env):
        if x >= 0 and y >= 0 and x < env.configDict["rows"] and y < env.configDict["columns"]:
            env.pos_x = x
            env.pos_y = y

    def scan_table(self,env):
        curr_x, curr_y = env.pos_x, env.pos_y
        fov_width, fov_height = env.configDict["camera_fov_width"], env.configDict["camera_fov_height"]
        scanned = 0
        for x in range(curr_x - fov_height, curr_x + 1 + fov_height):
            for y in range(curr_y - fov_width, curr_y + 1 + fov_width):
                if env.update_if_valid(x, y, True):
                    scanned += 1
        return scanned

    # def scan_table2(self,env):
    #     cam_height =
    #     pass
