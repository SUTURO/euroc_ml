extern "C"
{
    #include "lua.h"
    #include "lualib.h"
    #include "lauxlib.h"
    
    #include "ros/ros.h"
    
    //#include "suturo_perception_msgs/
}

#include <iostream>

extern "C" int asdf(lua_State* L)
{
    lua_pushnumber(L, 32);
    lua_pushnumber(L, 47);
    return 2;
}

extern "C" int callService(lua_State* L)
{
    char *fakeargv[] = { NULL };
    int fakeargc = 1;
    ros::init(argc, argv, "dpeclientlib");
    
    ros::NodeHandle n;
    //ros::ServiceClient client = n.serviceClient<beginner_tutorials::AddTwoInts>("add_two_ints");
}
