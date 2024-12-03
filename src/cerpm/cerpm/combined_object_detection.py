import rclpy
from rclpy.node import Node
from statemachine import State, StateMachine
from statemachine.transition import Transition
from sensor_msgs.msg import PointCloud2, Image
from sensor_msgs import point_cloud2
from std_msgs.msg import String
from cv_bridge import CvBridge
import math
import numpy as np
import cv2
import os


# ObjectDetectionNode that processes sensor data
class ObjectDetectionNode(Node):
    def __init__(self):
        super().__init__('object_detection_node')
        
        self.lidar_brake_distance = 5.0
        self.lidar_caution_distance = 15.0
        self.lidar_max_distance = 50.0
        self.radar_caution_distance = 10.0
        self.radar_max_distance = 100.0

        # Subscriptions to sensors
        self.lidar_sub = self.create_subscription(
            PointCloud2,
            '/carla/ego_vehicle/lidar',
            self.lidar_callback,
            10)

        self.radar_sub = self.create_subscription(
            PointCloud2,
            '/carla/ego_vehicle/radar',
            self.radar_callback,
            10)

        self.camera_sub = self.create_subscription(
            Image,
            '/carla/ego_vehicle/camera',
            self.camera_callback,
            10)

        # Publisher for detection events
        self.detection_pub = self.create_publisher(
            String,
            'detection_events',
            10)

        # YOLOv2 setup
        self.bridge = CvBridge()
        # Paths to the YOLOv2 configuration and weights files
        yolo_path = '/path/to/yolov2/'  # Update this path
        self.net = cv2.dnn.readNetFromDarknet(
            os.path.join(yolo_path, "yolov2.cfg"),
            os.path.join(yolo_path, "yolov2.weights"))
        self.layer_names = self.net.getUnconnectedOutLayersNames()
        # Load the COCO class labels
        with open(os.path.join(yolo_path, "coco.names"), 'r') as f:
            self.class_names = [line.strip() for line in f.readlines()]

    def lidar_callback(self, msg):
        obstacle_distance = self.process_lidar(msg)
        if obstacle_distance is not None:
            if obstacle_distance < 5.0:
                # Obstacle very close, need to brake
                detection_msg = String()
                detection_msg.data = 'lidar_brake'
                self.detection_pub.publish(detection_msg)
            elif obstacle_distance < 15.0:
                # Obstacle detected, proceed with caution
                detection_msg = String()
                detection_msg.data = 'radar_caution'
                self.detection_pub.publish(detection_msg)
            else:
                # Obstacle is far, clear to proceed
                detection_msg = String()
                detection_msg.data = 'radar_clear'
                self.detection_pub.publish(detection_msg)
        else:
            # No obstacles detected
            detection_msg = String()
            detection_msg.data = 'radar_clear'
            self.detection_pub.publish(detection_msg)

    def radar_callback(self, msg):
        obstacle_distance = self.process_radar(msg)
        if obstacle_distance is not None:
            if obstacle_distance < 10.0:
                # Obstacle detected by radar, proceed with caution
                detection_msg = String()
                detection_msg.data = 'radar_caution'
                self.detection_pub.publish(detection_msg)
            else:
                # Obstacle is far, clear to proceed
                detection_msg = String()
                detection_msg.data = 'radar_clear'
                self.detection_pub.publish(detection_msg)
        else:
            # No obstacles detected
            detection_msg = String()
            detection_msg.data = 'radar_clear'
            self.detection_pub.publish(detection_msg)

    def camera_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        emergency_stop = self.process_camera(cv_image)
        if emergency_stop:
            detection_msg = String()
            detection_msg.data = 'emergency_stop'
            self.detection_pub.publish(detection_msg)
        # Optionally, display the image with bounding boxes
        # cv2.imshow('Camera View', cv_image)
        # cv2.waitKey(1)

    def process_lidar(self, msg):
        # Process the point cloud data to detect obstacles
        points = point_cloud2.read_points(
            msg, field_names=("x", "y", "z"), skip_nans=True)
        min_distance = None
        point_count = 0
        for point in points:
            x, y, z = point
            distance = math.sqrt(x**2 + y**2 + z**2)
            if distance < self.lidar_max_distance:
                point_count += 1
                if min_distance is None or distance < min_distance:
                    min_distance = distance
        if point_count > 0:
            self.get_logger().info(f"LiDAR detected {point_count} points, closest at {min_distance:.2f} meters")
            return min_distance
        else:
            return None

    def process_radar(self, msg):
        # Process the radar data to detect objects
        points = point_cloud2.read_points(
            msg, field_names=("x", "y", "z"), skip_nans=True)
        min_distance = None
        point_count = 0
        for point in points:
            x, y, z = point
            distance = math.sqrt(x**2 + y**2 + z**2)
            if distance < 100.0:  # Consider points within 100 meters
                point_count += 1
                if min_distance is None or distance < min_distance:
                    min_distance = distance
        if point_count > 0:
            print(f"Radar detected {point_count} points, closest at {min_distance:.2f} meters")
            return min_distance
        else:
            return None

    def process_camera(self, cv_image):
        # Process the camera image using YOLOv2
        height, width = cv_image.shape[:2]
        # Create a blob from the image
        blob = cv2.dnn.blobFromImage(
            cv_image, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        # Run forward pass
        outputs = self.net.forward(self.layer_names)
        boxes = []
        confidences = []
        class_ids = []
        # Loop over each of the outputs
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                # Filter out weak predictions
                if confidence > 0.5:
                    # Scale the bounding box coordinates
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    # Calculate top-left corner
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        # Apply Non-Max Suppression
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        emergency_stop = False
        if len(idxs) > 0:
            for i in idxs.flatten():
                x, y, w, h = boxes[i]
                label = str(self.class_names[class_ids[i]])
                # Draw bounding box and label on the image
                color = (0, 255, 0)
                cv2.rectangle(cv_image, (x, y), (x + w, y + h), color, 2)
                cv2.putText(cv_image, label, (x, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                # Check for specific objects to trigger events
                if label == 'stop sign':
                    emergency_stop = True
        # Optionally, display the image with bounding boxes
        # cv2.imshow('Camera View', cv_image)
        # cv2.waitKey(1)
        return emergency_stop

def main(args=None):
    rclpy.init(args=args)
    # Start both the StateManager and ObjectDetectionNode
    object_detection_node = ObjectDetectionNode()
    try:
        rclpy.spin(object_detection_node)
    except KeyboardInterrupt:
        object_detection_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
