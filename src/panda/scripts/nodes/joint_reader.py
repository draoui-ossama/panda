import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math


class JointReader(Node):

    def __init__(self):
        super().__init__('panda_joint_reader')
        self.th = None
        self.d = None
        self.q = None
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_callback,
            100
        )
    def joint_callback(self, msg):
       self.q = list(msg.position)
       self.d = self.q[:2]
       self.th = self.q[2:]
    

def main():
    rclpy.init()

    node = JointReader()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()