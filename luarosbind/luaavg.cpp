/*
 * g++ luaavg.cpp -llua5.1 -lluabind -I/usr/include/lua5.1 -c -fPIC -o luaavg.o
 * g++ -shared -Wl,-soname,luaavg.so -o luaavg.so luaavg.o -lc -llua5.1 -lluabind
 * 
 * print(package.loadlib("./luaavg.so", "init"))
 * package.loadlib("./luaavg.so", "init")()
 * 
 * print(package.loadlib("./luaavg.so", "asdf")())
 */

extern "C"
{
    #include "lua.h"
    #include "lualib.h"
    #include "lauxlib.h"
}

#include <iostream>
#include <luabind/luabind.hpp>

void greet()
{
    std::cout << "hello world!\n";
}

extern "C" int init(lua_State* L)
{
    using namespace luabind;
    
    std::cout << "init 1!\n";

    luabind::open(L);
    
    std::cout << "init 2!\n";

    module(L)
    [
        def("greetasdf", &greet)
    ];
    
    std::cout << "init 3!\n";

    return 0;
}

extern "C" int asdf(lua_State* L)
{
    lua_pushnumber(L, 32);
    lua_pushnumber(L, 47);
    return 2;
}
