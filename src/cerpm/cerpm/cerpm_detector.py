import rclpy
from rclpy.node import Node
from rclpy.subscription import Subscription
from std_msgs.msg import String, UInt16
import json
from pprint import pp
import numpy as np
import random

DISTANCE_THRESHOLD = 10

class CerpmDetector(Node):
    def __init__(self) -> None:
        super().__init__('cerpm_detector')
        print('cerpm_detector init')
        self.x: float
        self.y: float
        self.distance_threshold = DISTANCE_THRESHOLD
        self.create_timer(1,
                          self.update_location)
        self.create_subscription(String, 'cerpms/broadcast', self.update_cerpms, 10)
        self.create_publisher(UInt16, 'cerpm_detector/in_range', 10)
        self.create_publisher(UInt16, 'cerpm_detector/out_range', 10)

    # This will require data from the Carla ROS Bridge
    # May reimplement just for simplicity of early development
    def update_location(self):
        self.x = random.randint(0, 10)
        self.y = random.randint(0, 10)

    def update_cerpms(self, msg):
        try:
            print('Got Cerpm Details')
            cerpm_dict = json.loads(msg.data)
            pp(cerpm_dict)
            for cerpm in cerpm_dict['cerpms']:
                print(cerpm)
                current_loc = (self.x, self.y)
                cerpm_loc = (float(cerpm['x']), float(cerpm['y']))
                self.determine_distance(current_loc, cerpm_loc)
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
    try:
        with rclpy.init(args=args):
            cerpm_detector = CerpmDetector()
            rclpy.spin(cerpm_detector)
    except:
        pass

if __name__ == '__main__':
    main()

    