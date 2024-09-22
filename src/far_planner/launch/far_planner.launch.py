import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from nav2_common.launch import ReplaceString

def generate_launch_description():
    # Map fully qualified names to relative ones so the node's namespace can be prepended.
    # In case of the transforms (tf), currently, there doesn't seem to be a better alternative
    # https://github.com/ros/geometry2/issues/32
    # https://github.com/ros/robot_state_publisher/pull/30
    # TODO(orduno) Substitute with `PushNodeRemapping`
    #              https://github.com/ros2/launch_ros/issues/56
    remappings = [("/tf", "tf"), ("/tf_static", "tf_static")]

    pkg_far_planner_dir = get_package_share_directory("far_planner")

    namespace = LaunchConfiguration("namespace")
    config_path = LaunchConfiguration("config_path")
    rviz_path = LaunchConfiguration("rviz_path")

    declare_namespace = DeclareLaunchArgument(
        "namespace", default_value="", description=""
    )

    declare_config_path = DeclareLaunchArgument(
        "config_path", default_value=os.path.join(pkg_far_planner_dir, "config", "default.yaml"), description=""
    )

    declare_rviz_path = DeclareLaunchArgument(
        "rviz_path", default_value=os.path.join(pkg_far_planner_dir, "rviz", "default.rviz"), description=""
    )

    namespaced_rviz_config_file = ReplaceString(
        source_file=rviz_path,
        replacements={"<robot_namespace>": ("/", namespace)},
    )

    start_far_planner_node = Node(
        package='far_planner',
        executable='far_planner',
        output='screen',
        namespace=namespace,
        parameters=[config_path],
        remappings=remappings,
    )

    start_graph_decoder = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('graph_decoder'), 'launch', 'decoder.launch.py')
        )
    )

    start_rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        namespace=namespace,
        remappings=remappings,
        arguments=['-d', namespaced_rviz_config_file],
        respawn=False,
    )

    ld = LaunchDescription()

    ld.add_action(declare_namespace)
    ld.add_action(declare_config_path)
    ld.add_action(declare_rviz_path)

    ld.add_action(start_far_planner_node)
    ld.add_action(start_graph_decoder)
    ld.add_action(start_rviz_node)

    return ld
