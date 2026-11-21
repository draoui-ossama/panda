import rclpy
from rclpy.node import Node

from tf2_ros import Buffer, TransformListener
from tf_transformations import euler_from_quaternion

# Example quaternion (replace with your actual values)




class EndEffectorPosition(Node):

    def __init__(self):
        super().__init__('end_effector_position')

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(
            self.tf_buffer, self
        )

        self.timer = self.create_timer(0.1, self.get_position)

    def get_position(self):

        try:
            transform = self.tf_buffer.lookup_transform(
                'panda_link0',
                'panda_link8',
                rclpy.time.Time()
            )

            p = transform.transform.translation
            q = transform.transform.rotation
            roll, pitch, yaw = euler_from_quaternion([q.x,q.y,q.z,q.w])

            return [p.x,p.y,p.z,roll,pitch,yaw]

        except Exception as e:
            self.get_logger().warning(str(e))


def main():
    rclpy.init()
    node = EndEffectorPosition()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()