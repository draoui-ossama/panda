import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math


class JointReader(Node):

    def __init__(self):
        super().__init__('panda_joint_reader')
        self.q = None
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_callback,
            10
        )

    def joint_callback(self, msg):
       self.q = list(msg.position)
    

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