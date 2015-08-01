#include </opt/euroc_c2s1/include/gazebo-2.2/gazebo/transport/transport.hh>
#include </opt/euroc_c2s1/include/gazebo-2.2/gazebo/msgs/msgs.hh>
#include </opt/euroc_c2s1/include/gazebo-2.2/gazebo/gazebo.hh>

#include <gazebo_msgs/ContactsState.h>
#include <gazebo_msgs/ContactState.h>

#include "ros/ros.h"

#include <iostream>
#include <sys/time.h>
#include <boost/unordered_map.hpp>

ros::Publisher pub;
std::vector<std::string> ignored_objects;
boost::unordered_map<std::string, long long> last_updated;
struct timeval tp;

using namespace std;

void callback(ConstContactsPtr &_msg)
{
  gazebo_msgs::ContactsState contactState;

  // contactState.state = 
  for (int i= 0; i < _msg->contact_size(); i++)
  {
    gazebo_msgs::ContactState state;
    state.collision1_name = _msg->contact(i).collision1();
    state.collision2_name = _msg->contact(i).collision2();
    contactState.states.push_back(state);
  }

  contactState.header.frame_id = "/map";

  gazebo::msgs::Time gz_time = _msg->time();
  contactState.header.stamp = ros::Time(gz_time.sec(), gz_time.nsec());
  pub.publish(contactState);
}

int main(int _argc, char *_argv[])
{

  ignored_objects.assign(_argv + 1, _argv + _argc);

  ros::init(_argc, _argv, "gazebo_contact_publisher");
  // std::cout << "0.\n";
  bool gazebo_started = false;
  while(!gazebo_started) 
  {
    gazebo_started = gazebo::load(_argc, _argv);
  }
  // std::cout << "gazebo started?" << a << "\n";

  ros::NodeHandle n;

  pub = n.advertise<gazebo_msgs::ContactsState>("/gazebo/contacts", 1000);

  ros::Rate loop_rate(10);

  // std::cout << "1.\n";
  gazebo::run();

  gazebo::transport::NodePtr node(new gazebo::transport::Node());
  node->Init();

  // gazebo::transport::SubscriberPtr sub = node->Subscribe("~/pose/info", callback);
  gazebo::transport::SubscriberPtr sub = node->Subscribe("~/physics/contacts", callback);
  //gazebo.msgs.Contacts
  //  /gazebo/task 1/physics/contacts
  //~/lwr_gripper/contacts
  std::cout << "gazebo_contact_publisher started.\n";
  ros::spin();

  gazebo::fini();
}
