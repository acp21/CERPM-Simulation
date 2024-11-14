import carla
import matplotlib.pyplot as plt

def main():
    # Connect to the CARLA server
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    # Get the world and the map
    world = client.get_world()
    carla_map = world.get_map()

    # Get waypoints at a given distance interval
    waypoints = carla_map.generate_waypoints(distance=15)

    # Separate waypoints by lane for visualization
    left_lane_x, left_lane_y = [], []
    right_lane_x, right_lane_y = [], []

    for waypoint in waypoints:
        if waypoint.lane_type == carla.LaneType.Driving:
            # Get the left and right lane boundaries
            left_boundary = waypoint.get_left_lane()
            right_boundary = waypoint.get_right_lane()

            # Store coordinates for the left boundary
            if left_boundary and left_boundary.lane_type == carla.LaneType.Driving:
                left_lane_x.append(left_boundary.transform.location.x)
                left_lane_y.append(left_boundary.transform.location.y)

            # Store coordinates for the right boundary
            if right_boundary and right_boundary.lane_type == carla.LaneType.Driving:
                right_lane_x.append(right_boundary.transform.location.x)
                right_lane_y.append(right_boundary.transform.location.y)

    # Plot lane boundaries as discrete points
    plt.figure(figsize=(10, 10))
    plt.scatter(left_lane_x, left_lane_y, color='blue', label="Left Lane Boundary", s=10, marker='o')
    plt.scatter(right_lane_x, right_lane_y, color='red', label="Right Lane Boundary", s=10, marker='o')
    plt.xlabel("X Position")
    plt.ylabel("Y Position")
    plt.title("CARLA Lane Boundaries as Points")
    plt.legend()
    plt.axis("equal")
    plt.show()

if __name__ == '__main__':
    main()
