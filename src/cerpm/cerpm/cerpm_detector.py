import rclpy
from rclpy.node import Node
from rclpy.subscription import Subscription
from std_msgs.msg import String, UInt16
import json
from pprint import pp
import numpy as np
import random
from typing import Optional
import argparse


class CerpmDetector(Node):
    def __init__(self, x, y, distance_threshold) -> None:
        super().__init__('cerpm_detector')
        print('cerpm_detector init')
        self.x: float = x
        self.y: float = y
        self.DISTANCE_THRESHOLD = distance_threshold
        self.create_timer(1,
                          self.update_location)
        self.create_subscription(String, 'cerpms/broadcast', self.update_cerpms, 10)
        self.in_range_publisher = self.create_publisher(UInt16, 'cerpm_detector/in_range', 10)
        self.out_range_publisher = self.create_publisher(UInt16, 'cerpm_detector/out_range', 10)

    # This will require data from the Carla ROS Bridge
    # May reimplement just for simplicity of early development
    def update_location(self):
        self.x = random.randint(0, 10)
        self.y = random.randint(0, 10)

    # simulate driving around by slowly updating x and y values
    def drive_around(self, direction: String, starting_point: Optional[tuple[float, float]]=None):
        if starting_point:
            self.x = starting_point[0]
            self.y = starting_point[1]

    def update_cerpms(self, msg):
        try:
            print('Got Cerpm Details')
            cerpm_dict = json.loads(msg.data)
            pp(cerpm_dict)
            for cerpm in cerpm_dict['cerpms']:
                msg = UInt16()
                msg.data = cerpm['id']
                print(cerpm)
                current_loc = (self.x, self.y)
                cerpm_loc = (float(cerpm['x']), float(cerpm['y']))
                distance = self.determine_distance(current_loc, cerpm_loc)
                if distance <= self.DISTANCE_THRESHOLD:
                    self.in_range_publisher.publish(msg)
                else:
                    self.out_range_publisher.publish(msg)
            pp(cerpm_dict)
        except Exception as e:
            print(f'{str(e)}')
    
    def determine_distance(self, p1: tuple[float, float], p2: tuple[float, float]):
        point1= np.array(p1)
        point2 = np.array(p2)
        distance = np.linalg.norm(point2 - point1)
        print(f'Distance between {point1} and {point2}: {distance}')
        return distance


def main(args=None):
    parser = argparse.ArgumentParser(description="Process optional arguments x, y, and debug.")
    
    # Add optional arguments
    parser.add_argument('-x', type=float, default=0.0, help="The starting x-coordinate (float). Default is 0.0.")
    parser.add_argument('-y', type=float, default=0.0, help="The starting y-coordinate (float). Default is 0.0.")
    parser.add_argument('--distance', type=float, default=10.0, help='Default distance a cerpm can be detected from')
    parser.add_argument('--debug', action='store_true', help="Enable debug mode (boolean). Default is False.")
    parsed_args = parser.parse_args()
    
    try:
        with rclpy.init(args=args):
            cerpm_detector = CerpmDetector(parsed_args.x, parsed_args.y, parsed_args.distance)
            rclpy.spin(cerpm_detector)
    except:
        pass

if __name__ == '__main__':
    main()

    