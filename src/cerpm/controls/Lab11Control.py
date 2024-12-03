#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Bool, String
from ackermann_msgs.msg import AckermannDrive
import csv
import os
from datetime import datetime


class CombinedControlNode(Node):
    def __init__(self):
        super().__init__('combined_control_node')

        # CSV Logging setup
        self.current_state = 'standard'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_file = f"plot.csv"
        self.csv_file = open(self.output_file, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["Time (s)", "Lane Offset", "Speed"])  # CSV header

        # Timer to publish both speed and steering together
        self.timer = self.create_timer(0.1, self.publish_control_command)

        self.get_logger().info(f"Logging lane data to {self.output_file}")

        # Publishers and Subscribers
        self.control_publisher = self.create_publisher(AckermannDrive, '/carla/ego_vehicle/ackermann_cmd', 10)
        
        # Subscribe to control signals
        self.create_subscription(Float32, '/lane_center_offset', self.control_steering, 10)
        self.create_subscription(Bool, '/alex_stop_signal', self.control_speed, 10)
        self.create_subscription(String, '/state_manage', self.state_callback, 10)
        
        
        self.speed_subscriber = self.create_subscription(Float32,
            'carla/ego_vehicle/speedometer', self.speed_callback, 10)
                    
        # Initialize variables for speed and steering
        self.lane_offset = 0.0 # Default lane center offset
        self.stop_flag = False # Default stop signal flag
        
        # Timer to publish both speed and steering together
        self.timer = self.create_timer(0.1, self.publish_control_command)

    def speed_callback(self, msg):
            """Callback to update the current speed of the vehicle."""
            self.current_speed = msg.data
            self.get_logger().info(f"Current speed: {self.current_speed}")

    def state_callback(self, msg):
        self.current_state = msg.data
        self.get_logger().info(f'Controller state set to {self.current_state}')

    def control_steering(self, msg):
        """Callback for updating the lane center offset for lateral control."""
        self.lane_offset = msg.data
        current_time = self.get_clock().now().to_msg().sec  # Log the time in seconds
        speed = self.speed_subscriber

        # Write data to CSV
        self.csv_writer.writerow([current_time, self.lane_offset,self.current_speed])
        self.get_logger().info(f"Logged offset: {self.lane_offset} at time: {current_time}")

    
    def control_speed(self, msg):
        """Callback for updating the stop signal for longitudinal control."""
        self.stop_flag = msg.data
        self.get_logger().info(f'Received stop signal: {self.stop_flag}')

    def publish_control_command(self):
        """Publish Ackermann drive message with both speed and steering angle."""
        drive_msg = AckermannDrive()

        # Handle steering based on lane offset
        steering_angle = -self.lane_offset * 1.5 # Adjust scaling factor if needed
        drive_msg.steering_angle = steering_angle


            # drive_msg.speed = 10.0 # Move forward at default speed (m/s)
        if self.current_state == 'standard':  # Modified: Check current state
            drive_msg.speed = 15.0 - abs(self.lane_offset) * 200.0  # Default speed with lane offset adjustment
        elif self.current_state == 'caution':
            drive_msg.speed = 10.0 - abs(self.lane_offset) * 200.0 # Reduced speed in caution state
        elif self.current_state == 'brake':
            drive_msg.speed = 0.0 - abs(self.lane_offset) * 200.0 # Apply brakes in brake state
        elif self.current_state == 'emergency':
            drive_msg.speed = 0.0  # Stop vehicle in emergency state
        else:
            drive_msg.speed = 15.0  # Default speed if state is unknown
        
        # Log the control command for debugging
        self.get_logger().info(f'Publishing control command: speed={drive_msg.speed}, steering_angle={drive_msg.steering_angle}')

        # Publish the combined control message
        self.control_publisher.publish(drive_msg)

        print ("lane offset=", self.lane_offset) 

    def destroy(self):
        """Ensure the CSV file is properly closed upon shutdown."""
        self.csv_file.close()
        self.get_logger().info(f"CSV file saved: {self.output_file}")
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = CombinedControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()