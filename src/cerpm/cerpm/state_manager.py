import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.subscription import Subscription
from statemachine import State, StateMachine
from statemachine.transition import Transition

class VehicleStateMachine(StateMachine):
    begin = State('begin', initial=True)
    standard = State('standard')
    slow = State('slow')
    emergency = State('emergency', final=True)
    caution = State('caution')
    brake = State('break')
    
    
    exceed_speed_limit = standard.to(slow)
    match_speed_limit = slow.to(standard)
    radar_detection = standard.to(caution)
    obstacle = caution.to(brake)
    avoid_obstacle = brake.to(standard)
    clear_radar = caution.to(standard)
    start_run = begin.to(standard)
    trigger_emergency_stop = StateMachine.from_(StateMachine.ANY_STATE).to(emergency)
    
    def on_enter_standard(self):
        print('Resuming standard operation')
        self.state_pub.publish(String(data='standard'))  # Publish current state

    def on_enter_caution(self):
        print('Entering caution state')
        self.state_pub.publish(String(data='caution'))  # Publish current state

    def on_enter_brake(self):
        print('Obstacle very close, braking...')
        self.state_pub.publish(String(data='brake'))  # Publish current state

    def on_enter_emergency(self):
        print("EMERGENCY TRIGGERED, VEHICLE STOPPING")
        self.state_pub.publish(String(data='emergency'))

class StateManager(Node):
    def __init__(self):
        super().__init__('state_manager')
        self.state_pub = self.create_publisher(String, '/vehicle_state', 10)
        self.machine = VehicleStateMachine()
        self.machine.activate_initial_state()
        
        self.detection_sub = self.create_subscription(
            String,
            '/detection_events',
            self.detection_callback,
            10)
        
    def detection_callback(self, msg):
        event = msg.data
        if event == 'radar_caution':
            if self.machine.is_standard:
                self.machine.radar_detection()
        elif event == 'radar_clear':
            if self.machine.is_caution:
                self.machine.clear_radar()
        elif event == 'lidar_brake':
            if self.machine.is_caution or self.machine.is_standard:
                self.machine.obstacle_near()
        elif event == 'lidar_caution':
            if self.machine.is_brake:
                self.machine.obstacle_far()
        elif event == 'emergency_stop':
            self.machine.trigger_emergency_stop()

        
def main(args=None):
    try:
        rclpy.init(args=args)
        state_manager = StateManager()
        rclpy.spin(state_manager)
    except Exception as e:
        print(f'Error: {str(e)}')
        
if __name__ == '__main__':
    main()