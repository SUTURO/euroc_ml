cmake_minimum_required(VERSION 2.8.3)
project(suturo_learning)

find_package(catkin REQUIRED rosprolog knowrob_common knowrob_mongo)

catkin_package(
	    DEPENDS knowrob_common
		    knowrob_mongo
)
