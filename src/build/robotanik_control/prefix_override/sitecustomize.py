import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/aziz/Desktop/ros2v2/src/install/robotanik_control'
