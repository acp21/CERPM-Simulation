import rclpy
from rclpy.node import Node
from rclpy.subscription import Subscription
from std_msgs.msg import String, Float32MultiArray

class CerpmDetector(Node):
    def __init__(self) -> None:
        super().__init__('cerpm_detector')
        self.x: int
        self.y: int

        self.create_timer(0.1,
                          self.update_location)
        self.create_subscription()

    # This will require data from the Carla ROS Bridge
    # May reimplement just for simplicity of early development
    def update_location(self):
        pass

    def update_cerpms(self):
        pass

    