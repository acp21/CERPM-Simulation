import csv
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
from sensor_msgs_py import point_cloud2
from tf2_ros import TransformListener, Buffer
import tf_transformations


class PointCloudPublisher(Node):
    def __init__(self):
        super().__init__('pointcloud_publisher')
        
        # Initialize TF buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Publisher for the transformed PointCloud2 message
        self.publisher_ = self.create_publisher(PointCloud2, '/transformed_pointcloud', 10)

        # Load points from the CSV file in the map frame
        self.points = self.load_points_from_csv("cerpm_points.csv")

        # Timer to publish periodically
        self.timer = self.create_timer(1.0, self.publish_pointcloud)

    def load_points_from_csv(self, filename):
        points = []
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                x = float(row['x'])
                y = float(row['y'])
                z = 0.0  # Set z coordinate if needed
                intensity = 1.0  # Set intensity if needed
                points.append((x, y, z, intensity))
        return points

    def transform_points(self, points, transform):
        transformed_points = []
        for (x, y, z, intensity) in points:
            point = tf_transformations.translation_matrix((x, y, z))
            transformed_point = tf_transformations.concatenate_matrices(transform, point)
            x_t, y_t, z_t = tf_transformations.translation_from_matrix(transformed_point)
            transformed_points.append((x_t, y_t, z_t, intensity))
        return transformed_points

    def publish_pointcloud(self):
        try:
            # Lookup the transform from map to ego_vehicle
            transform_stamped = self.tf_buffer.lookup_transform('ego_vehicle', 'map', rclpy.time.Time())

            # Build translation matrix
            translation = tf_transformations.translation_matrix((
                transform_stamped.transform.translation.x,
                transform_stamped.transform.translation.y,
                transform_stamped.transform.translation.z
            ))

            # Convert quaternion to rotation matrix
            rotation = tf_transformations.quaternion_matrix((
                transform_stamped.transform.rotation.x,
                transform_stamped.transform.rotation.y,
                transform_stamped.transform.rotation.z,
                transform_stamped.transform.rotation.w
            ))

            # Combine translation and rotation into a single transformation matrix
            transform = tf_transformations.concatenate_matrices(translation, rotation)

            # Transform the points
            transformed_points = self.transform_points(self.points, transform)

            # Create a PointCloud2 message in the ego_vehicle frame
            header = Header()
            header.stamp = self.get_clock().now().to_msg()
            header.frame_id = "ego_vehicle"
            pointcloud_msg = point_cloud2.create_cloud(
                header,
                [
                    PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
                    PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
                    PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
                    PointField(name="intensity", offset=12, datatype=PointField.FLOAT32, count=1)
                ],
                transformed_points
            )

            # Publish the transformed point cloud
            self.publisher_.publish(pointcloud_msg)

        except Exception as e:
            self.get_logger().warn(f"Could not transform points: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = PointCloudPublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
