import rclpy
from rclpy.node import Node
from rclpy.subscription import Subscription
from std_msgs.msg import String

class CerpmDetector(Node):
    def __init__(self) -> None:
        super().__init__('cerpm_detector')
        self.x: int
        self.y: int

        self.create_timer(0.1,
                          self.update_location)

    def update_location(self):
        pass

    def update_cerpms(self):
        pass

    