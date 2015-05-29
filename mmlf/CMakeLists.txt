cmake_minimum_required(VERSION 2.8.3)
project(mmlf_msgs)

## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS xyz)
## is used, also find other catkin packages
find_package(catkin REQUIRED 
  message_generation
  geometry_msgs
)

add_service_files(
  DIRECTORY
  srv
  FILES
  TransformerService.srv
)

## Generate added messages and services with any dependencies listed here
generate_messages(
  DEPENDENCIES
  geometry_msgs
)

catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES kinect_node_msgs
  CATKIN_DEPENDS message_runtime
#  DEPENDS system_lib
)

