import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/ossama/Desktop/ROBOTICS/panda_ws/install/panda'
