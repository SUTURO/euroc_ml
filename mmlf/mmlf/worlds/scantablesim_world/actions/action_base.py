import abc


class ActionBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __call__(self, environment):
        pass

class SimSimAction(object):

    def __init__(self):
        self.min_n = 2
        self.moves = 1

    def moveLeft(self, env):
        n = self.min_n
        if env.currentState["isTurbo"]:
            n = 10
        (x,y) = env.camera_index
        self.move_to(x, y-n,env )
        self.moves += 0
        return -self.moves

    def moveRight(self, env):
        n = self.min_n
        if env.currentState["isTurbo"]:
            n = 10
        (x,y) = env.camera_index
        self.move_to(x, y+n,env )
        self.moves += 0
        return -self.moves

    def moveUp(self, env):
        n = self.min_n
        if env.currentState["isTurbo"]:
            n = 10
        (x,y) = env.camera_index
        self.move_to(x+n, y,env )
        self.moves += 0
        return -self.moves

    def moveDown(self, env):
        n = self.min_n
        if env.currentState["isTurbo"]:
            n = 10
        (x,y) = env.camera_index
        self.move_to(x-n, y,env )
        self.moves += 0
        return -self.moves

    def turboMode(self, env):
        env.currentState["isTurbo"] = int(not env.currentState["isTurbo"])
        return -1

    def scan(self, env):
        self.moves = 1
        return self.scan_table2(env)
        pass

    def move_to(self, x, y, env):
        x = max(0, min(x,env.configDict["rows"]-1))
        y = max(0, min(y,env.configDict["columns"]-1))
        # if x >= 0 and y >= 0 and x < env.configDict["rows"] and y < env.configDict["columns"]:
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

    def scan_table2(self,env):
        curr_x, curr_y = env.camera_index
        fov_width, fov_height = env.configDict["camera_fov_width"], env.configDict["camera_fov_height"]
        scanned = 0
        for x in range(curr_x - fov_height, curr_x + 1 + fov_height):
            for y in range(curr_y - fov_width+abs(curr_x-x), curr_y + 1 + fov_width-abs(curr_x-x)):
                if env.update_if_valid(x, y, True):
                    scanned += 1
        return scanned
