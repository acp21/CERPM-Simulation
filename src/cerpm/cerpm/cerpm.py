import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
import pandas as pd
from rclpy.publisher import Publisher
from rclpy.timer import Timer
from std_msgs.msg import String
import random
import time
import json


class Cerpm():
    def __init__(self, id, x, y, publisher: Publisher[String]) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.publisher: Publisher[String] = publisher
    
    def talk(self):
        msg = String()
        # TODO: remove before shipping to production
        time.sleep(random.randint(0,2))
        msg_str = f'{self.id}:{self.x}:{self.y}'
        msg.data = msg_str
        self.publisher.publish(msg)
        print(f'CERPM {self.id} published talk')

class CerpmCluster(Node):

    def __init__(self):
        super().__init__('cerpm')
        self.cerpms: list[Cerpm] = []
        self.timer: Timer = self.create_timer(0.5, self.timer_callback)
        self.broadcast_timer: Timer = self.create_timer(0.5, self.broadcast)
        self.broadcast_publisher = self.create_publisher(String, 'cerpms/broadcast', 10)
        print('created cerpm_cluster')

    def broadcast(self):
        print('Broadcasting CERPMs')
        msg = String()
        cerpm_info = {'cerpms':[]}
        for cerpm in self.cerpms:
            cerpm_obj = {
                'id': cerpm.id,
                'x': cerpm.x,
                'y': cerpm.y
            }
            cerpm_info['cerpms'].append(cerpm_obj)
        json_str = json.dumps(cerpm_info)
        msg.data = json_str
        self.broadcast_publisher.publish(msg)


    def build_cerpm(self, id, x, y):
        publisher_topic = f'cerpms/cerpm_{id}/talk'
        publisher: Publisher[String] = self.create_publisher(String, publisher_topic, 10)
        cerpm = Cerpm(id, x, y, publisher)
        self.cerpms.append(cerpm)
    
    def timer_callback(self):
        for cerpm in self.cerpms:
            cerpm.talk()

    def load_cerpms_from_file(self, file_path: str, generate_ids:bool=False):
        print(f'loading cerpms from csv {file_path}')
        if(generate_ids):
            print('Generate IDs set to true, ignoring ids in csv file')
        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            print(f'File {file_path} not found!')
        id = 0
        print(df)
        for row in df.itertuples(index=True, name='cerpms'):
            print(row)  # Access the entire row
            if generate_ids:
                self.build_cerpm(id, row.x, row.y)
                id += 1
            else:
                self.build_cerpm(row.id, row.x, row.y)
        print(self.cerpms)

        

def main(args=None):
    try:
        with rclpy.init(args=args):
            cerpm_cluster = CerpmCluster()
            cerpm_cluster.load_cerpms_from_file('cerpm_list.csv', True)
            rclpy.spin(cerpm_cluster)

    except:
        pass

if __name__ == '__main__':
    main()