
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class PandaController(Node):

    def __init__(self):
        super().__init__('panda_controller')
        # Action client for the 7 arm joints
        self.arm_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/panda_arm_controller/follow_joint_trajectory'
        )

        # Action client for the gripper
        self.hand_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/panda_hand_controller/follow_joint_trajectory'
        )

        self.get_logger().info('Panda controller initialized')

    def move_arm(self, positions, duration_sec=0,duration_ms=2):

        joint_names = [
            'panda_joint1',
            'panda_joint2',
            'panda_joint3',
            'panda_joint4',
            'panda_joint5',
            'panda_joint6',
            'panda_joint7'
        ]

        if len(positions) != 7:
            raise ValueError('The Panda arm requires 7 joint positions')

        if not self.arm_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Arm controller not available')
            return

        # Create trajectory goal
        goal = FollowJointTrajectory.Goal()

        goal.trajectory.joint_names = joint_names

        # Define target position
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=duration_sec,nanosec=duration_ms*1000)

        goal.trajectory.points.append(point)

        # Send goal
        # self.get_logger().info(f'Moving arm to: {positions}')

        future = self.arm_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)

        goal_handle = future.result()

        if goal_handle is None or not goal_handle.accepted:
            self.get_logger().error('Trajectory rejected')
            return

        # Wait for execution result
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        result = result_future.result()

        if not (result is not None and result.result.error_code == 0):
            self.get_logger().error('Arm movement failed')


    def move_hand(self, opening, duration=2):

        joint_names = [
            'panda_finger_joint1',
            'panda_finger_joint2'
        ]

        if not 0.0 <= opening <= 0.04:
            raise ValueError('Opening must be between 0 and 0.04 meters')

        if not self.hand_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Hand controller not available')
            return

        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = joint_names

        point = JointTrajectoryPoint()
        point.positions = [opening, opening]
        point.time_from_start = Duration(sec=duration)

        goal.trajectory.points.append(point)

        self.get_logger().info(f'Gripper opening: {opening} m')

        future = self.hand_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)

        goal_handle = future.result()

        if goal_handle is None or not goal_handle.accepted:
            self.get_logger().error('Gripper command rejected')
            return

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        result = result_future.result()

        if result is not None and result.result.error_code == 0:
            self.get_logger().info('Gripper movement completed')
        else:
            self.get_logger().error('Gripper movement failed')

def main(args=None):


    panda = PandaController()
    

    try:
        # Move arm to a target configuration
        panda.move_arm(
            [0.3, -0.5, 0.2, -1.8, 0.2, 1.5, 0.5],
            duration=5
        )

        # Open gripper
        panda.move_hand(0.00)

        # Close gripper
        panda.move_hand(0.04)

    except KeyboardInterrupt:
        pass

    finally:
        panda.destroy()


if __name__ == '__main__':
    main()
