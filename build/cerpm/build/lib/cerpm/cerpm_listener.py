import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.subscription import Subscription

from std_msgs.msg import String

class CerpmListener(Node):
    def __init__(self):
        super().__init__('cerpm_listener')
        self.listening_cerpms: list[Subscription] = []
        self.subscription = self.create_subscription(
            String,
            'cerpms/cerpm_1/talk',
            self.listener_callback,
            10
        )

        self.subscription = self.create_subscription(
            String,
            'cerpms/cerpm_heard',
            self.heard_callback,
            10
        )

    def listener_callback(self, msg):
        self.get_logger().info('I heard %s' % msg.data)

    def heard_callback(self, msg):
        pass

def main(args=None):
    try:
        with rclpy.init(args=args):
            cerpm_listener = CerpmListener()

            rclpy.spin(cerpm_listener)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == '__main__':
    main()