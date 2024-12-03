#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from carla_msgs.msg import CarlaActorList, CarlaEgoVehicleControl
import carla
import numpy as np
import time

class SimpleController(Node):
    """
    A ROS2 node that controls a CARLA vehicle using waypoints and stops when an obstacle is detected.
    """
    def __init__(self):
        super().__init__('simple_controller')

        # CARLA Client Setup
        self.client = carla.Client('localhost', 2000)
        self.client.set_timeout(2.0)
        self.world = self.client.get_world()
        self.map = self.world.get_map()
        self.vehicle = None
        self.control = carla.VehicleControl()
        self.control.steer = 0.0
        self.control.throttle = 0.5 # Default throttle value

        # PID controller gains for steering
        self.kp = 0.8
        self.ki = 0.0
        self.kd = 0.1
        self.integral = 0.0
        self.previous_error = 0.0
        self.previous_time = time.time()

        # Subscribers
        self.create_subscription(
            CarlaActorList,
            '/carla/actor_list',
            self.actor_list_callback,
            10
        )
        self.create_subscription(
            Odometry,
            '/carla/ego_vehicle/odometry',
            self.odometry_callback,
            10
        )
        self.create_subscription(
            CarlaEgoVehicleControl,
            '/carla/ego_vehicle/vehicle_status',
            self.vehicle_status_callback,
            10
        )

        # If you have an obstacle detection topic, subscribe to it
        # from std_msgs.msg import Bool
        # self.create_subscription(
        # Bool,
        # '/carla/ego_vehicle/obstacle_detected',
        # self.obstacle_callback,
        # 10
        # )

        # Timer to send control commands at regular intervals
        self.timer = self.create_timer(0.05, self.publish_control_command)
        
        self.get_logger().info('Simple Controller Node Initialized')

    def actor_list_callback(self, msg):
        """
        Callback to get the ego vehicle from the actor list.
        """
        for actor in msg.actors:
            if actor.rolename == 'ego_vehicle':
                self.vehicle = self.world.get_actor(actor.id)
                self.get_logger().info(f'Ego vehicle found: {actor.id}')

    def odometry_callback(self, msg):
        """
        Callback to receive the vehicle's odometry and compute control commands.
        """
        if self.vehicle is None:
            return
    
        # Get current vehicle orientation
        current_yaw = self.vehicle.get_transform().rotation.yaw
    
        # Get desired waypoint (next waypoint ahead)
        vehicle_location = self.vehicle.get_location()
        waypoint = self.map.get_waypoint(vehicle_location, project_to_road=True, lane_type=carla.LaneType.Driving)
        next_waypoints = waypoint.next(2.0) # Get waypoints 2 meters ahead
        
        if not next_waypoints:
            self.get_logger().info('No waypoints ahead.')
            return
        
        next_waypoint = next_waypoints[0]
        desired_yaw = next_waypoint.transform.rotation.yaw
        
        # Calculate yaw error
        yaw_error = desired_yaw - current_yaw
        # Normalize the error to [-180, 180]
        yaw_error = (yaw_error + 180) % 360 - 180

        # Time delta
        current_time = time.time()
        dt = current_time - self.previous_time
        self.previous_time = current_time

        # PID calculations
        self.integral += yaw_error * dt
        derivative = (yaw_error - self.previous_error) / dt if dt > 0 else 0.0
        self.previous_error = yaw_error

        # Compute steering output
        output = self.kp * yaw_error + self.ki * self.integral + self.kd * derivative
        output = np.clip(output, -1.0, 1.0) # Ensure steering is within valid range

        # Update control
        self.control.steer = output

        # Optionally, adjust throttle based on desired speed
        self.control.throttle = 0.5 # Set a constant throttle value or adjust as needed

    def vehicle_status_callback(self, msg):
        """
        Callback to receive the vehicle's status.
        """
        # Implement if needed
        pass

    # Uncomment if using obstacle detection
    # def obstacle_callback(self, msg):
    # """
    # Callback to handle obstacle detection.

    # """
    # obstacle_detected = msg.data
    # if obstacle_detected:
        # self.control.throttle = 0.0
        # self.control.brake = 1.0 # Apply full brake
        # self.get_logger().info('Obstacle detected! Stopping the vehicle.')
    # else:
        # self.control.brake = 0.0
        # self.control.throttle = 0.5 # Resume throttle

    def publish_control_command(self):
        """
        Publish the control command to the vehicle.
        """
        if self.vehicle is None:
            return
    
        self.vehicle.apply_control(self.control)
        self.get_logger().info(f'Applied Control: Steer={self.control.steer}, Throttle={self.control.throttle}')

def main(args=None):
    """
    Main function to run the node.
    """
    rclpy.init(args=args)
    node = SimpleController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    node.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()