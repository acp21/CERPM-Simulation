import carla
import csv
import matplotlib.pyplot as plt

def main():
    # Connect to the CARLA server
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    # Get the world and the map
    world = client.get_world()
    carla_map = world.get_map()

    # Get waypoints at a given distance interval
    waypoints = carla_map.generate_waypoints(distance=.5)
    cerpm_points = carla_map.generate_waypoints(distance=10)
    std_tup = build_waypoints(waypoints)
    cpm_tup = build_waypoints(cerpm_points)
    write_to_csv(cpm_tup, "cerpm_points.csv")
    plot_points(std_tup, cpm_tup)

    # Separate waypoints by lane for visualization
    

def build_waypoints(waypoints):
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
    return left_lane_x, left_lane_y

def write_to_csv(data, filename):
    """Write points to a CSV file."""
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["x", "y"])  # Header
        for x, y in zip(data[0], data[1]):
            writer.writerow([x, y])

def plot_points(waypoints, cpms):
    # Plot lane boundaries as discrete points
    plt.figure(figsize=(10, 10))
    plt.scatter(waypoints[0], waypoints[1], color='blue', label="Left Lane Boundary", s=10, marker='o')
    plt.scatter(cpms[0], cpms[1], color='red', label="CERPMS", s=10, marker='o')
    plt.xlabel("X Position")
    plt.ylabel("Y Position")
    plt.title("CARLA Lane Boundaries as Points")
    plt.legend()
    plt.axis("equal")
    plt.show()

if __name__ == '__main__':
    main()
