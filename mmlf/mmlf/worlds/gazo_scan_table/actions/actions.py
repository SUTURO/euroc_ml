__author__ = 'hansa'


from suturo_environment_msgs.srv import AddPointCloud
from suturo_manipulation_msgs.srv import MoveMastCam
import rospy


class GazeboActions(object):

    actions = ["left", "right", "up", "down", "scan"]

    def __init__(self, minPan, maxPan, minTilt, maxTilt, stepsX=4, stepsY=2):
        self.__pan_step = (maxPan - minPan) / stepsX
        self.__tilt_step = (maxTilt - minTilt) / stepsY
        self.__minPan = minPan
        self.__maxPan = maxPan
        self.__minTilt = minTilt
        self.__maxTilt = maxTilt
        self.oldy = -1
        self.oldx = -1
        self.move_cam = rospy.ServiceProxy("/suturo/manipulation/move_mastcam", MoveMastCam)
        self.__add_pointcloud = rospy.ServiceProxy("/suturo/environment/add_point_cloud", AddPointCloud)

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

    def __move(self, x, y, env):
        reward = -1
        env.pan += x
        env.tilt += y
        if env.pan < self.__minPan:
            env.pan = self.__minPan
            reward = -1
        elif env.pan > self.__maxPan:
            env.pan = self.__maxPan
            reward = -1
        if env.tilt < self.__minTilt:
            env.tilt = self.__minTilt
            reward = -1
        elif env.tilt > self.__maxTilt:
            env.tilt = self.__maxTilt
            reward = -1
        self.move_cam(pan=env.pan, tilt=env.tilt)
        env.update_index()
        return reward

    def moveLeft(self, environment):
        return self.__move(-self.__pan_step, 0, environment)
    moveLeft.name = "Move Left"

    def moveRight(self, env):
        return self.__move(self.__pan_step, 0, env)
    moveRight.name = "Move Right"

    def moveUp(self, env):
        return self.__move(0, -self.__tilt_step, env)
    moveUp.name = "Move Up"

    def moveDown(self, env):
        return self.__move(0, self.__tilt_step, env)
    moveDown.name = "Move Down"

    def scan(self, env):
        old = env.discovered_percentage
        x,y = env.camera_index
        # Scan the image and add to the point cloud\
        # Move the cam
        if self.oldx ==x and self.oldy == y:
            return -10
        elif self.move_cam(pan=env.pan, tilt=env.tilt):
            r = 20 if not env.currentState["isScanned"] else -10
            env.environmentLog.info("state: %s, Scanned: %d, x: %d, y: %d" % (str(env.currentState), r, x, y))
            self.__add_pointcloud(scenecam=True)
            env.update_map()
            self.oldx, self.oldy = x,y
            return r
        return -10
            #          new = env.discovered_percentage
            #           diff = int(new) - int(old)
            #if diff <= 3:
        #                return -8
        #            else:
        #                return 10
    scan.name = "Scan"
