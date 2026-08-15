#!/usr/bin/env python3
import sys
import threading
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped, Quaternion
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, PositionConstraint, OrientationConstraint, BoundingVolume
from shape_msgs.msg import SolidPrimitive

import tkinter as tk
from tkinter import ttk, messagebox

# Target Box Coordinates (X, Y, Z - matching table surface Z=0.38)
# We position the end-effector 0.2m above the top of each box (Z = 0.58m)
BOX_TARGETS = {
    "Box 1 (Red)":   {"x": 0.55, "y": -0.20, "z": 0.58},
    "Box 2 (Green)": {"x": 0.65, "y":  0.00, "z": 0.58},
    "Box 3 (Blue)":  {"x": 0.55, "y":  0.20, "z": 0.58},
}

class MoveItCommanderNode(Node):
    def __init__(self):
        super().__init__('block_selector_commander')
        self._action_client = ActionClient(self, MoveGroup, 'move_action')

    def send_pose_goal(self, target_x, target_y, target_z, status_callback):
        if not self._action_client.wait_for_server(timeout_sec=3.0):
            status_callback("Error: /move_action server not available!")
            return

        goal_msg = MoveGroup.Goal()
        goal_msg.request.group_name = "ur_manipulator"
        goal_msg.request.num_planning_attempts = 10
        goal_msg.request.allowed_planning_time = 5.0
        goal_msg.request.max_velocity_scaling_factor = 0.5
        goal_msg.request.max_acceleration_scaling_factor = 0.5

        # Position Constraint
        pos_constraint = PositionConstraint()
        pos_constraint.header.frame_id = "world"
        pos_constraint.link_name = "tool0"
        
        box_primitive = SolidPrimitive()
        box_primitive.type = SolidPrimitive.BOX
        box_primitive.dimensions = [0.01, 0.01, 0.01]  # 1cm tolerance box

        target_pose = PoseStamped()
        target_pose.header.frame_id = "world"
        target_pose.pose.position.x = target_x
        target_pose.pose.position.y = target_y
        target_pose.pose.position.z = target_z

        bounding_volume = BoundingVolume()
        bounding_volume.primitives.append(box_primitive)
        bounding_volume.primitive_poses.append(target_pose.pose)

        pos_constraint.constraint_region = bounding_volume
        pos_constraint.weight = 1.0

        # Orientation Constraint (End-effector pointing straight down towards table)
        ori_constraint = OrientationConstraint()
        ori_constraint.header.frame_id = "world"
        ori_constraint.link_name = "tool0"
        # Quaternion pointing downward along Z-axis: [x=0, y=1, z=0, w=0]
        ori_constraint.orientation = Quaternion(x=0.0, y=1.0, z=0.0, w=0.0)
        ori_constraint.absolute_x_axis_tolerance = 0.1
        ori_constraint.absolute_y_axis_tolerance = 0.1
        ori_constraint.absolute_z_axis_tolerance = 0.1
        ori_constraint.weight = 1.0

        constraints = Constraints()
        constraints.position_constraints.append(pos_constraint)
        constraints.orientation_constraints.append(ori_constraint)

        goal_msg.request.goal_constraints.append(constraints)

        status_callback(f"Planning motion to X:{target_x:.2f}, Y:{target_y:.2f}, Z:{target_z:.2f}...")

        send_goal_future = self._action_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(
            lambda future: self.goal_response_callback(future, status_callback)
        )

    def goal_response_callback(self, future, status_callback):
        goal_handle = future.result()
        if not goal_handle.accepted:
            status_callback("Planning rejected by MoveIt.")
            return

        status_callback("Executing movement in Gazebo/RViz...")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(
            lambda f: status_callback("Arm successfully arrived above target!")
        )


class BlockSelectorUI:
    def __init__(self, root, ros_node):
        self.root = root
        self.ros_node = ros_node

        self.root.title("UR5e Target Selector")
        self.root.geometry("400x320")
        self.root.resizable(False, False)

        # Style
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 11), padding=6)
        style.configure("TLabel", font=("Arial", 10))

        # Title Label
        title_label = ttk.Label(
            root, text="Select Target Block", font=("Arial", 14, "bold")
        )
        title_label.pack(pady=15)

        # Block Selection Dropdown
        self.selected_block = tk.StringVar(value="Box 2 (Green)")
        dropdown_frame = ttk.Frame(root)
        dropdown_frame.pack(pady=5)

        dropdown_label = ttk.Label(dropdown_frame, text="Target Block: ")
        dropdown_label.pack(side=tk.LEFT, padx=5)

        block_menu = ttk.OptionMenu(
            dropdown_frame,
            self.selected_block,
            self.selected_block.get(),
            *BOX_TARGETS.keys(),
        )
        block_menu.pack(side=tk.LEFT, padx=5)

        # Move Button
        self.move_btn = ttk.Button(
            root, text="Move Arm Above Block", command=self.on_move_click
        )
        self.move_btn.pack(pady=20)

        # Status Footer Label
        self.status_label = ttk.Label(
            root, text="Status: Ready", font=("Arial", 10, "italic"), foreground="gray"
        )
        self.status_label.pack(side=tk.BOTTOM, pady=15)

    def update_status(self, message):
        def _update():
            self.status_label.config(text=f"Status: {message}")
            if "Error" in message or "rejected" in message:
                self.status_label.config(foreground="red")
            elif "successfully" in message:
                self.status_label.config(foreground="green")
            else:
                self.status_label.config(foreground="blue")
        self.root.after(0, _update)

    def on_move_click(self):
        block_name = self.selected_block.get()
        coords = BOX_TARGETS[block_name]
        
        # Dispatch ROS 2 action in background to keep UI responsive
        threading.Thread(
            target=self.ros_node.send_pose_goal,
            args=(coords["x"], coords["y"], coords["z"], self.update_status),
            daemon=True
        ).start()


def main():
    rclpy.init()
    ros_node = MoveItCommanderNode()

    # Spin ROS 2 node in background thread
    ros_thread = threading.Thread(target=rclpy.spin, args=(ros_node,), daemon=True)
    ros_thread.start()

    # Main Tkinter Loop
    root = tk.Tk()
    app = BlockSelectorUI(root, ros_node)
    
    try:
        root.mainloop()
    finally:
        ros_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()