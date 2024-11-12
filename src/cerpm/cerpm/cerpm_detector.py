import rclpy
from rclpy.node import Node
from rclpy.subscription import Subscription
from std_msgs.msg import String
import json
from pprint import pp

class CerpmDetector(Node):
    def __init__(self) -> None:
        super().__init__('cerpm_detector')
        print('cerpm_detector init')
        self.x: int
        self.y: int

        self.create_timer(0.1,
                          self.update_location)
        self.create_subscription(String, 'cerpms/broadcast', self.update_cerpms, 10)

    # This will require data from the Carla ROS Bridge
    # May reimplement just for simplicity of early development
    def update_location(self):
        pass

    def update_cerpms(self, msg):
        print('Got Cerpm Details')
        cerpm_dict = json.loads(msg.data)
        pp(cerpm_dict)

def main(args=None):
    try:
        with rclpy.init(args=args):
            cerpm_detector = CerpmDetector()
            rclpy.spin(cerpm_detector)

    except:
        pass

if __name__ == '__main__':
    main()

    