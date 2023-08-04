cmake_minimum_required(VERSION 3.0.2)
project(record_tool)

find_package(catkin REQUIRED COMPONENTS
  std_msgs
  dbw_mkz_msgs
  sensor_msgs
  message_generation
)

add_service_files(DIRECTORY srv FILES Record.srv)

generate_messages(DEPENDENCIES
  std_msgs
)

catkin_package(INCLUDE_DIRS
  CATKIN_DEPENDS dbw_mkz_msgs sensor_msgs message_runtime std_msgs
)



