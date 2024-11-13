import carla
import random
def main():
    # Connect to the Carla Simulator
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()
    # Get available blueprints for spawning vehicles and pedestrians
    blueprint_library = world.get_blueprint_library()
    vehicle_blueprints = blueprint_library.filter('vehicle.*')
    pedestrian_blueprints = blueprint_library.filter('walker.pedestrian.*')
    # Define the number of vehicles and pedestrians to spawn
    num_vehicles = 100
    num_pedestrians = 100
    # Get available spawn points
    spawn_points = world.get_map().get_spawn_points()
    random.shuffle(spawn_points)
    # Spawn vehicles
    for i in range(num_vehicles):
        blueprint = random.choice(vehicle_blueprints)
        spawn_point = random.choice(spawn_points)
        vehicle = world.try_spawn_actor(blueprint, spawn_point)
        if vehicle is not None:
            vehicle.set_autopilot(True)
    print(f'Spawned {vehicle.type_id} at {spawn_point.location}')
    # Spawn pedestrians
    for i in range(num_pedestrians):
        blueprint = random.choice(pedestrian_blueprints)
        spawn_point = carla.Transform()
        spawn_point.location = world.get_random_location_from_navigation()
        pedestrian = world.try_spawn_actor(blueprint, spawn_point)
        if pedestrian is not None:
            print(f'Spawned {pedestrian.type_id} at {spawn_point.location}')

if __name__ == '__main__':
    main()