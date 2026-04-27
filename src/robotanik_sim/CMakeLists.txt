cmake_minimum_required(VERSION 3.8)
project(robotanik_sim)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)

# Launch, URDF, world, map ve param dosyalarını share klasörüne kurar
install(DIRECTORY
  launch
  urdf
  worlds
  maps
  params
  DESTINATION share/${PROJECT_NAME}
)

# Python FSM node'unu ros2 run ile çalıştırılabilir hale getirir
install(PROGRAMS
  scripts/row_fsm.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
