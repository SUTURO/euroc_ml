__author__ = 'hansa'


from suturo_environment_msgs.srv import AddPointCloud
from suturo_manipulation_msgs.srv import MoveMastCam
import rospy


class GazeboActions(object):

    def __init__(self, minX, maxX, minY, maxY, stepsX=4, stepsY=2):
        self.__x_step = (maxX - minX) / stepsX
        self.__y_step = (maxY - minY) / stepsY
        self.__move_cam = rospy.ServiceProxy("/suturo/manipulation/move_mastcam", MoveMastCam)
        self.__add_pointcloud = rospy.ServiceProxy("/suturo/environment/add_point_cloud", AddPointCloud)

    def __move(self, x, y, env):
        env.pos_x += x
        env.pos_y += y
        if env.pos_x < env.configDict["minX"]:
            env.pos_x = env.configDict["minX"]
        elif env.pos_x > env.configDict["maxX"]:
            env.pos_x = env.configDict["maxX"]
        if env.pos_y < env.configDict["minY"]:
            env.pos_y = env.configDict["minY"]
        elif env.pos_y > env.configDict["maxY"]:
            env.pos_y = env.configDict["maxY"]


    def moveLeft(self, environment):
        self.__move(-self.__x_step, 0, environment)
        return -1

    def moveRight(self, env):
        self.__move(self.__x_step, 0, env)
        return -1

    def moveUp(self, env):
        self.__move(0, -self.__y_step, env)
        return -1

    def moveDown(self, env):
        self.__move(0, self.__y_step, env)
        return -1

    def scan(self, env):
        old = env.discovered_percentage
        # Move the cam
        if self.__move_cam(pan=env.pos_x, tilt=env.pos_y):
            # Scan the image and add to the point cloud
            self.__add_pointcloud(True)
            env.update_map()
            new = env.discovered_percentage
            return new - old