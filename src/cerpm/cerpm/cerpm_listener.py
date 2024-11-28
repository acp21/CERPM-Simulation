import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.subscription import Subscription
from math import acos
import json
from queue import Queue
from typing import Any

from std_msgs.msg import String, UInt16


class CerpmListener(Node):
    def __init__(self):
        super().__init__('cerpm_listener')
        self.listening_cerpms: list[Subscription] = []
        self.message_queue: Queue[Any] = Queue(10)
        self.location: tuple[int, int] = (0, 0) # May be removed, currently for testing
        self.TIME_DELTA_THRESHOLD = 0.1

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

    def process_messages(self):
        if len(self.message_queue)  < 3:
            return
        sorted_messages = sorted(self.message_queue, 
                                 key=lambda msg: json.loads(msg)['timestamp'])

        # Use a sliding window to find groups of 3
        for i in range(len(sorted_messages) - 2):
            if (
                sorted_messages[i + 2].timestamp - sorted_messages[i].timestamp
                <= self.TIME_DELTA_THRESHOLD
            ):
                # Process the matching group
                matching_msgs = sorted_messages[i:i + 3]
                print("Processing messages:", [msg.data for msg in matching_msgs])
    
                # Remove the matched messages from the deque
                for msg in matching_msgs:
                    self.message_queue.remove(msg)
                return

    def listener_callback(self, msg):
        self.get_logger().info('I heard %s' % msg.data)
        # x, y, id, time
        # Load message data into queue
        # Remove oldest if full
        if self.message_queue.full():
            self.message_queue.get()
        self.message_queue.put(msg.data)
        self.process_messages()
        
    # get list of all currently subscribed topics
    def get_listening_topics(self) -> list[str]:
        topics: list[str] = []
        for topic in self.listening_cerpms:
            topics.append(topic.topic)
        return topics

    def in_range_callback(self, msg):
        id = msg.data
        topic = f'cerpms/cerpm_{id}/talk'
        if topic not in self.get_listening_topics():
            # Create subscription to listen to a given cerpm
            new_subscription = self.create_subscription(String,
                                                     topic,
                                                     self.listener_callback,
                                                     10)
            self.listening_cerpms.append(new_subscription)

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