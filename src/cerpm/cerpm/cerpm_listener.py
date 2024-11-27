import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.subscription import Subscription
from math import acos
import json
from queue import Queue

from std_msgs.msg import String, UInt16


class CerpmListener(Node):
    def __init__(self):
        super().__init__('cerpm_listener')
        self.listening_cerpms: list[Subscription] = []
        self.message_queue = Queue(10)
        self.location: tuple[int, int] = (0, 0) # May be removed, currently for testing

        # Listen for incoming cerpms from cerpm_detector
        self.subscription = self.create_subscription(
            UInt16,
            'cerpm_detector/in_range',
            self.in_range_callback,
            10
        )
        # Listen for outgoing cerpms from cerpm_detector
        self.create_subscription(UInt16, 'cerpm_detector/out_range', self.mute_cerpm, 10)
        

    def mute_cerpm(self, msg):
        pass


    def listener_callback(self, msg):
        self.get_logger().info('I heard %s' % msg.data)
        # x, y, id
        data = json.loads(msg.data)
        x = data['x']
        y = data['y']
        id = data['id']
        

    # def triangle(self, a, b, c):

    # get list of all currently subscribed topics
    def get_listening_topics(self) -> list[str]:
        topics: list[str] = []
        for topic in self.listening_cerpms:
            topics.append(topic.topic)
        return topics

    # TODO: Ensure that multiple subscriptions for same topic are not created
    def in_range_callback(self, msg):
        id = msg.data
        topic = f'cerpms/cerpm_{id}/talk'
        # Create subscription to listen to a given cerpm
        new_subscription = self.create_subscription(String,
                                                    topic,
                                                    self.listener_callback,
                                                    10)
    def out_range_callback(self, msg):
        id = msg.data
        topic = f'/cerpms/cerpm_{id}/talk'

def main(args=None):
    try:
        with rclpy.init(args=args):
            cerpm_listener = CerpmListener()

            rclpy.spin(cerpm_listener)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == '__main__':
    main()