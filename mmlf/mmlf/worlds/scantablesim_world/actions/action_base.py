import abc


class ActionBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __call__(self, environment):
        pass

class SimSimAction(object):

    actions = ["left", "right", "up", "down", "scan"]

    def __init__(self):
        # self.__pan_step = (maxPan - minPan) / stepsX
        # self.__tilt_step = (maxTilt - minTilt) / stepsY
        # self.__minPan = minPan
        # self.__maxPan = maxPan
        # self.__minTilt = minTilt
        # self.__maxTilt = maxTilt
        # self.__move_cam = rospy.ServiceProxy("/suturo/manipulation/move_mastcam", MoveMastCam)
        # self.__add_pointcloud = rospy.ServiceProxy("/suturo/environment/add_point_cloud", AddPointCloud)
        self.old_scan = 0
        self.min_n = 5
        self.moves = 1

    def performAction(self, action, env):
        if action == "left":
            return self.moveLeft(env)
        elif action == "right":
            return self.moveRight(env)
        elif action == "up":
            return self.moveUp(env)
        elif action == "down":
            return self.moveDown(env)
        elif action == "scan":
            return self.scan(env)
        # elif action == "turbo":
        #     return self.turboMode(env)

    # def __init__(self):
    #     self.min_n = 2
    #     self.moves = 1
    #     self.old_scan = 0

    def moveLeft(self, env):
        n = self.min_n
        if env.currentState["isTurbo"]:
            n = 10
        (x,y) = env.camera_index
        self.move_to(x-n, y+n,env )
        self.moves += 0
        return -self.moves

    def moveRight(self, env):
        n = self.min_n
        if env.currentState["isTurbo"]:
            n = 10
        (x,y) = env.camera_index
        self.move_to(x-n, y+n,env )
        self.moves += 0
        return -self.moves

    def moveUp(self, env):
        n = self.min_n
        if env.currentState["isTurbo"]:
            n = 10
        (x,y) = env.camera_index
        self.move_to(x+n, y+n,env )
        self.moves += 0
        return -self.moves

    def moveDown(self, env):
        n = self.min_n
        if env.currentState["isTurbo"]:
            n = 10
        (x,y) = env.camera_index
        self.move_to(x-n, y-n,env )
        self.moves += 0
        return -self.moves

    def turboMode(self, env):
        env.currentState["isTurbo"] = int(not env.currentState["isTurbo"])
        return -1

    def scan(self, env):
        self.moves = 1
        return self.scan_table2(env)

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
        self.old_scan = env.discovered_percentage
        curr_x, curr_y = env.camera_index
        fov_width, fov_height = env.configDict["camera_fov_width"], env.configDict["camera_fov_height"]
        scanned = env.cell_map[curr_x, curr_y]
        for x in range(curr_x - fov_height, curr_x + 1 + fov_height):
            for y in range(curr_y - fov_width+abs(curr_x-x), curr_y + 1 + fov_width-abs(curr_x-x)):
                # if env.update_if_valid(x, y, True) and curr_x == x and curr_y == y:
                #     scanned = True
                env.update_if_valid(x, y, True)


                    # scanned += 1.

        r = env.discovered_percentage - self.old_scan
        scanned = not scanned and env.cell_map[curr_x, curr_y]
        # if r > 0:
        #     print r
        return 1 if scanned else -1
        # return 10 if r > 5. else -8
        # self.disc = env.discovered_percentage
        # if env.discovered_percentage > 0:
        #     print r
        # return r
