#include "ros/ros.h"
#include "suturo_perception_msgs/DeepMindInteraction.h"
#include <cstdlib>

int main(int argc, char **argv)
{
  ros::init(argc, argv, "DeepMindInteractionWrapper");

  ros::NodeHandle n;
  ros::ServiceClient client = n.serviceClient<suturo_perception_msgs::DeepMindInteraction>("/suturo/deepmind/interaction");
  suturo_perception_msgs::DeepMindInteraction srv;
  srv.request.action = 0;
  if (client.call(srv))
  {
    ROS_INFO("Reward: %ld", (long int)srv.response.reward);
  }
  else
  {
    ROS_ERROR("Failed to call service /suturo/deepmind/interaction");
    return 1;
  }

  return 0;
}