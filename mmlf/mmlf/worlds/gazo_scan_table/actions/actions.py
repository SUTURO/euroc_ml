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
        self.__move_cam = rospy.ServiceProxy("/suturo/manipulation/move_mastcam", MoveMastCam)
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
        env.pan += x
        env.tilt += y
        if env.pan < self.__minPan:
            env.pan = self.__minPan
        elif env.pan > self.__maxPan:
            env.pan = self.__maxPan

        if env.tilt < self.__minTilt:
            env.tilt = self.__minTilt
        elif env.tilt > self.__maxTilt:
            env.tilt = self.__maxTilt
        env.update_index()
        #self.__move_cam(pan=env.pan, tilt=env.tilt)

    def moveLeft(self, environment):
        self.__move(-self.__pan_step, 0, environment)
        return -1
    moveLeft.name = "Move Left"

    def moveRight(self, env):
        self.__move(self.__pan_step, 0, env)
        return -1
    moveRight.name = "Move Right"

    def moveUp(self, env):
        self.__move(0, -self.__tilt_step, env)
        return -1
    moveUp.name = "Move Up"

    def moveDown(self, env):
        self.__move(0, self.__tilt_step, env)
        return -1
    moveDown.name = "Move Down"

    def scan(self, env):
        old = env.discovered_percentage
        # Move the cam
        if self.__move_cam(pan=env.pan, tilt=env.tilt):
            # Scan the image and add to the point cloud
            self.__add_pointcloud(scenecam=True)
            env.update_map()
            new = env.discovered_percentage
            diff = int(new) - int(old)
            if diff <= 3:
                return -10
            else:
                return 10
    scan.name = "Scan"
