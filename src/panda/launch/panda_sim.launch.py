#!/usr/bin/env python3

"""Launch the Franka Panda Gazebo simulation and ros2_control controllers."""

import os
import re

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    RegisterEventHandler,
    SetEnvironmentVariable,
    TimerAction,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    panda_share = get_package_share_directory('panda')
    gz_share = get_package_share_directory('ros_gz_sim')

    urdf_path = os.path.join(panda_share, 'urdf', 'panda.urdf')
    controllers_yaml = os.path.join(panda_share, 'config', 'panda_controllers.yaml')

    with open(urdf_path, 'r', encoding='utf-8') as urdf_file:
        robot_description = urdf_file.read()

    # Use the installed package-share path for the Gazebo ros2_control plugin.
    # This avoids a machine-specific absolute path in the URDF.
    robot_description, replacements = re.subn(
        r'<parameters>.*?</parameters>',
        f'<parameters>{controllers_yaml}</parameters>',
        robot_description,
        count=1,
        flags=re.DOTALL,
    )
    if replacements == 0:
        raise RuntimeError(
            'Could not find the <parameters>...</parameters> element in panda.urdf'
        )

    # Gazebo must be able to resolve the Panda's relative mesh paths.
    current_gz_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    resource_paths = [panda_share]
    if current_gz_path:
        resource_paths.append(current_gz_path)

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gz_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r -v 4 empty.sdf'}.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': True},
        ],
    )

    spawn_panda = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_panda',
        output='screen',
        arguments=[
            '-name', 'panda',
            '-topic', '/robot_description',
            '-x', '0', '-y', '0', '-z', '0.5',
        ],
    )

    # Pass the YAML to each controller spawner. The Gazebo plugin loads the
    # controller-manager types, while the spawners pass each controller's
    # own joints/interfaces parameters during controller initialization.
    spawner_common_args = [
        '--controller-manager', '/controller_manager',
        '--param-file', controllers_yaml,
        '--switch-timeout', '30',
    ]

    spawn_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        name='spawn_joint_state_broadcaster',
        output='screen',
        arguments=['joint_state_broadcaster', *spawner_common_args],
    )

    spawn_arm_controller = Node(
        package='controller_manager',
        executable='spawner',
        name='spawn_panda_arm_controller',
        output='screen',
        arguments=['panda_arm_controller', *spawner_common_args],
    )

    spawn_hand_controller = Node(
        package='controller_manager',
        executable='spawner',
        name='spawn_panda_hand_controller',
        output='screen',
        arguments=['panda_hand_controller', *spawner_common_args],
    )

    return LaunchDescription([
        SetEnvironmentVariable(
            name='GZ_SIM_RESOURCE_PATH',
            value=os.pathsep.join(resource_paths),
        ),
        gazebo,
        robot_state_publisher,
        # Give Gazebo and robot_state_publisher time to start before spawning.
        TimerAction(period=5.0, actions=[spawn_panda]),
        # Start controllers in order after the Panda has been spawned.
        RegisterEventHandler(
            OnProcessExit(
                target_action=spawn_panda,
                on_exit=[TimerAction(period=2.0, actions=[spawn_joint_state_broadcaster])],
            )
        ),
        RegisterEventHandler(
            OnProcessExit(
                target_action=spawn_joint_state_broadcaster,
                on_exit=[TimerAction(period=1.0, actions=[spawn_arm_controller])],
            )
        ),
        RegisterEventHandler(
            OnProcessExit(
                target_action=spawn_arm_controller,
                on_exit=[TimerAction(period=1.0, actions=[spawn_hand_controller])],
            )
        ),
    ])
