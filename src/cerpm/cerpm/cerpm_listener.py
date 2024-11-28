import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.subscription import Subscription
from math import acos
from copy import deepcopy
import json
from collections import deque
from typing import Any, Optional, Tuple, List
import numpy as np

from std_msgs.msg import String, UInt16


class CerpmListener(Node):
    def __init__(self):
        super().__init__('cerpm_listener')
        self.listening_cerpms: List[Subscription] = []
        self.message_queue: deque[Any] = deque(maxlen=10)
        self.location: Tuple[int, int] = (0, 0) # May be removed, currently for testing
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
        if len(self.message_queue) < 3:
            return None

        # Parse and sort messages by timestamp
        parsed_messages = [json.loads(msg) for msg in self.message_queue]
        sorted_messages = sorted(parsed_messages, key=lambda msg: msg['time'])

        # Use a sliding window to find groups of 3
        for i in range(len(sorted_messages) - 2):
            if sorted_messages[i + 2]['time'] - sorted_messages[i]['time'] <= self.TIME_DELTA_THRESHOLD:
                # Group of 3 within the threshold
                matching_msgs = sorted_messages[i:i + 3]

                # Remove these messages from the original deque
                for match in matching_msgs:
                    for original_msg in self.message_queue:
                        if json.loads(original_msg) == match:
                            self.message_queue.remove(original_msg)
                            break

                # print("Processing messages:", [msg['x'] for msg in matching_msgs])
                return matching_msgs  # Return the matching group

        return None

    def listener_callback(self, msg):
        # self.get_logger().info('I heard %s' % msg.data)
        # x, y, id, time
        # Load message data into queue
        # Remove oldest if full
        self.message_queue.append(msg.data)
        window: Optional[List[Any]] = self.process_messages()
        if window:
            print(window)
            w1, w2, w3 = window
            print('Window')
            print(w1['x'], w1['y'])

            d1 = self.determine_distance((0,0), (w1['x'], w1['y']))
            d2 = self.determine_distance((0,0), (w2['x'], w2['y']))
            d3 = self.determine_distance((0,0), (w3['x'], w3['y']))
            print(d1, d2, d3)

            print()
            
            x, y =trilaterate(w1['x'],
                        w1['y'],
                        d1,
                        w2['x'],
                        w2['y'],
                        d2,
                        w3['x'],
                        w3['y'],
                        d3)
            print(f"DETERMINED WE ARE AT POINT {x}, {y}")

    def determine_distance(self, p1: Tuple[float, float], p2: Tuple[float, float]):
        point1= np.array(p1)
        point2 = np.array(p2)
        distance = np.linalg.norm(point2 - point1)
        # print(f'Distance between {point1} and {point2}: {distance}')
        return distance

    # get list of all currently subscribed topics
    def get_listening_topics(self) -> List[str]:
        topics: List[str] = []
        for topic in self.listening_cerpms:
            topics.append(topic.topic)
        return topics

    def in_range_callback(self, msg):
        id = msg.data
        topic = f'cerpms/cerpm_{id}/talk'
        if topic not in self.get_listening_topics():
            print(f'Subscribing to new cerpm {id}')
            # Create subscription to listen to a given cerpm
            new_subscription = self.create_subscription(String,
                                                     topic,
                                                     self.listener_callback,
                                                     10)
            self.listening_cerpms.append(new_subscription)

    def out_range_callback(self, msg):
        id = msg.data
        topic = f'/cerpms/cerpm_{id}/talk'

def trilaterate(x1, y1, r1, x2, y2, r2, x3, y3, r3):
    """
    Solves for the (x, y) coordinates of a point given distances to three known points.
    
    Parameters:
    - x1, y1: Coordinates of the first known point.
    - r1: Distance from the unknown point to the first known point.
    - x2, y2: Coordinates of the second known point.
    - r2: Distance from the unknown point to the second known point.
    - x3, y3: Coordinates of the third known point.
    - r3: Distance from the unknown point to the third known point.
    
    Returns:
    - (x, y): Coordinates of the unknown point.
    """
    # Setup the equations based on the circle equations
    A = np.array([
        [2*(x2 - x1), 2*(y2 - y1)],
        [2*(x3 - x1), 2*(y3 - y1)]
    ])
    b = np.array([
        r1**2 - r2**2 - x1**2 + x2**2 - y1**2 + y2**2,
        r1**2 - r3**2 - x1**2 + x3**2 - y1**2 + y3**2
    ])
    
    # Solve the linear equations
    try:
        x, y = np.linalg.solve(A, b)
        return x, y
    except np.linalg.LinAlgError:
        raise ValueError("The three points do not form a valid configuration for trilateration.")

def main(args=None):
    try:
        rclpy.init(args=args)
        cerpm_listener = CerpmListener()

        rclpy.spin(cerpm_listener)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == '__main__':
    main()