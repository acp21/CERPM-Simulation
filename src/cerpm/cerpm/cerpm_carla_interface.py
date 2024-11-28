import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import String
import json

class CerpmCarlaInterface(Node):
    def __init__(self):
        super().__init__('ego_vehicle_location_node')
        
        # Publisher for ego vehicle's location
        self.location_publisher = self.create_publisher(String, 'cerpms/ego_vehicle_location', 10)
        
        # Subscriber to the Carla ROS Bridge ego vehicle's odometry
        self.create_subscription(Odometry, '/carla/ego_vehicle/odometry', self.odometry_callback, 10)

        self.get_logger().info('Ego Vehicle Location Node has been started.')

    def odometry_callback(self, msg: Odometry):
        """ Callback function to process the vehicle's odometry and publish location """
        
        # Log the ego vehicle's location

        self.get_logger().info(f'Received Ego Vehicle Location: x={msg.pose.pose.position.x}, y={msg.pose.pose.position.y}, z={msg.pose.pose.position.z}')
        x = msg.pose.pose.position.x 
        y = msg.pose.pose.position.y
        point = {'x': x,
                 'y': y}
        msg = String()
        json_str = json.dumps(point)
        msg.data = json_str
        self.location_publisher.publish(msg)
        
        # Publish the received location to another topic (for example 'ego_vehicle_location')
        # self.location_publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)

    node = CerpmCarlaInterface()
    
    # Spin the node to keep it alive and processing callbacks
    rclpy.spin(node)

    # Shutdown ROS 2 client
    rclpy.shutdown()

if __name__ == '__main__':
    main()
