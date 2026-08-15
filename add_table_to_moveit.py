import rclpy
from rclpy.node import Node
from moveit_msgs.msg import PlanningScene, CollisionObject
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose

def main():
    rclpy.init()
    node = Node('add_table_planning_scene')
    
    if not node.has_parameter('use_sim_time'):
        node.declare_parameter('use_sim_time', True)

    publisher = node.create_publisher(PlanningScene, '/planning_scene', 10)
    rclpy.spin_once(node, timeout_sec=1.0)

    scene = PlanningScene()
    scene.is_diff = True

    # Define Collision Object
    table = CollisionObject()
    table.header.frame_id = 'world'
    table.id = 'table'

    # Table Top Surface (Thin box to prevent engulfing the robot base)
    box = SolidPrimitive()
    box.type = SolidPrimitive.BOX
    box.dimensions = [1.2, 0.8, 0.05]  # length=1.2m, width=0.8m, thickness=0.05m

    pose = Pose()
    pose.position.x = 0.6    # Center of table forward from arm base
    pose.position.y = 0.0
    pose.position.z = -0.025 # Placed immediately below world origin (z=0)

    table.primitives.append(box)
    table.primitive_poses.append(pose)
    table.operation = CollisionObject.ADD

    scene.world.collision_objects.append(table)
    
    for _ in range(10):
        publisher.publish(scene)
        rclpy.spin_once(node, timeout_sec=0.1)

    print("Table collision surface updated successfully!")
    rclpy.shutdown()

if __name__ == '__main__':
    main()
