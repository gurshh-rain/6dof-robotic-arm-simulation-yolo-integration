#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from moveit_msgs.msg import PlanningScene, CollisionObject
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose

class PlanningScenePublisher(Node):
    def __init__(self):
        super().__init__('planning_scene_publisher')
        self.publisher = self.create_publisher(PlanningScene, '/planning_scene', 10)
        self.timer = self.create_timer(1.0, self.publish_scene)
        self.published = False

    def make_box(self, box_id, dimensions, position):
        obj = CollisionObject()
        obj.header.frame_id = 'world'
        obj.id = box_id

        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = dimensions

        pose = Pose()
        pose.position.x = position[0]
        pose.position.y = position[1]
        pose.position.z = position[2]
        pose.orientation.w = 1.0

        obj.primitives.append(primitive)
        obj.primitive_poses.append(pose)
        obj.operation = CollisionObject.ADD
        return obj

    def publish_scene(self):
        scene = PlanningScene()
        scene.is_diff = True

        # Table in front of robot
        table = self.make_box('table', [0.8, 1.0, 0.5], [0.5, 0.0, 0.25])
        
        # 3 Boxes on top of table matching Gazebo positions
        box1 = self.make_box('box1', [0.06, 0.06, 0.06], [0.4, -0.2, 0.55])
        box2 = self.make_box('box2', [0.06, 0.06, 0.06], [0.5, 0.0, 0.55])
        box3 = self.make_box('box3', [0.06, 0.06, 0.06], [0.4, 0.2, 0.55])

        scene.world.collision_objects.extend([table, box1, box2, box3])
        self.publisher.publish(scene)
        self.get_logger().info('Published table and 3 boxes to MoveIt Planning Scene.')

def main():
    rclpy.init()
    node = PlanningScenePublisher()
    # Publish twice to ensure RViz receives it
    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.5)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from moveit_msgs.msg import PlanningScene, CollisionObject
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose

class PlanningScenePublisher(Node):
    def __init__(self):
        super().__init__('planning_scene_publisher')
        self.publisher = self.create_publisher(PlanningScene, '/planning_scene', 10)

    def make_box(self, box_id, dimensions, position):
        obj = CollisionObject()
        obj.header.frame_id = 'world'
        obj.id = box_id

        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = dimensions

        pose = Pose()
        pose.position.x = position[0]
        pose.position.y = position[1]
        pose.position.z = position[2]
        pose.orientation.w = 1.0

        obj.primitives.append(primitive)
        obj.primitive_poses.append(pose)
        obj.operation = CollisionObject.ADD
        return obj

    def publish_scene(self):
        scene = PlanningScene()
        scene.is_diff = True

        # Shorter table further away (x = 0.65m, height = 0.35m)
        table = self.make_box('table', [0.8, 1.0, 0.35], [0.65, 0.0, 0.175])
        
        # 3 Boxes resting on top of table
        box1 = self.make_box('box1', [0.06, 0.06, 0.06], [0.55, -0.2, 0.38])
        box2 = self.make_box('box2', [0.06, 0.06, 0.06], [0.65, 0.0, 0.38])
        box3 = self.make_box('box3', [0.06, 0.06, 0.06], [0.55, 0.2, 0.38])

        scene.world.collision_objects.extend([table, box1, box2, box3])
        self.publisher.publish(scene)
        self.get_logger().info('Published updated table and boxes to MoveIt!')

def main():
    rclpy.init()
    node = PlanningScenePublisher()
    for _ in range(5):
        node.publish_scene()
        rclpy.spin_once(node, timeout_sec=0.2)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from moveit_msgs.msg import PlanningScene, CollisionObject
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose

class PlanningScenePublisher(Node):
    def __init__(self):
        super().__init__('planning_scene_publisher')
        self.publisher = self.create_publisher(PlanningScene, '/planning_scene', 10)

    def make_box(self, box_id, dimensions, position):
        obj = CollisionObject()
        obj.header.frame_id = 'world'
        obj.id = box_id

        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = dimensions  # [X, Y, Z]

        pose = Pose()
        pose.position.x = float(position[0])
        pose.position.y = float(position[1])
        pose.position.z = float(position[2])
        pose.orientation.w = 1.0

        obj.primitives.append(primitive)
        obj.primitive_poses.append(pose)
        obj.operation = CollisionObject.ADD
        return obj

    def publish_scene(self):
        scene = PlanningScene()
        scene.is_diff = True

        # Table: Size [0.8, 1.0, 0.35], Pose [0.65, 0.0, 0.175] (Center Z = Height / 2)
        table = self.make_box('table', [0.8, 1.0, 0.35], [0.65, 0.0, 0.175])
        
        # 3 Boxes: Size [0.06, 0.06, 0.06], Pose Z = 0.35 + 0.03 = 0.38
        box1 = self.make_box('box1', [0.06, 0.06, 0.06], [0.55, -0.2, 0.38])
        box2 = self.make_box('box2', [0.06, 0.06, 0.06], [0.65, 0.0, 0.38])
        box3 = self.make_box('box3', [0.06, 0.06, 0.06], [0.55, 0.2, 0.38])

        scene.world.collision_objects.extend([table, box1, box2, box3])
        self.publisher.publish(scene)
        self.get_logger().info('Synchronized exact table and box dimensions with RViz2!')

def main():
    rclpy.init()
    node = PlanningScenePublisher()
    for _ in range(5):
        node.publish_scene()
        rclpy.spin_once(node, timeout_sec=0.2)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from moveit_msgs.msg import PlanningScene, CollisionObject
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose

class PlanningScenePublisher(Node):
    def __init__(self):
        super().__init__('planning_scene_publisher')
        self.publisher = self.create_publisher(PlanningScene, '/planning_scene', 10)

    def make_box(self, box_id, dimensions, position):
        obj = CollisionObject()
        obj.header.frame_id = 'world'
        obj.id = box_id

        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = dimensions  # [X, Y, Z]

        pose = Pose()
        pose.position.x = float(position[0])
        pose.position.y = float(position[1])
        pose.position.z = float(position[2])
        pose.orientation.w = 1.0

        obj.primitives.append(primitive)
        obj.primitive_poses.append(pose)
        obj.operation = CollisionObject.ADD
        return obj

    def publish_scene(self):
        scene = PlanningScene()
        scene.is_diff = True

        # Table: Size [0.8, 1.0, 0.35], Pose [0.65, 0.0, 0.175] (Center Z = Height / 2)
        table = self.make_box('table', [0.8, 1.0, 0.35], [0.65, 0.0, 0.175])
        
        # 3 Boxes: Size [0.06, 0.06, 0.06], Pose Z = 0.35 + 0.03 = 0.38
        box1 = self.make_box('box1', [0.06, 0.06, 0.06], [0.55, -0.2, 0.38])
        box2 = self.make_box('box2', [0.06, 0.06, 0.06], [0.65, 0.0, 0.38])
        box3 = self.make_box('box3', [0.06, 0.06, 0.06], [0.55, 0.2, 0.38])

        scene.world.collision_objects.extend([table, box1, box2, box3])
        self.publisher.publish(scene)
        self.get_logger().info('Synchronized exact table and box dimensions with RViz2!')

def main():
    rclpy.init()
    node = PlanningScenePublisher()
    for _ in range(5):
        node.publish_scene()
        rclpy.spin_once(node, timeout_sec=0.2)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
