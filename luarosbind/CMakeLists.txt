cmake_minimum_required(VERSION 2.8.3)
project(luarosbind)

find_package(catkin REQUIRED
            roscpp
            )

find_package(Lua51)

catkin_package(
)

include_directories(
  ${catkin_INCLUDE_DIRS}
  ${LUA_INCLUDE_DIR}
)

add_library(dperos
  src/dperoslib.cpp
)

add_executable(roswrap
  src/roswrap.cpp
)
target_link_libraries(roswrap ${catkin_LIBRARIES})
add_dependencies(roswrap suturo_perception_msgs_gencpp)