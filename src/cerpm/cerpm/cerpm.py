import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
import pandas as pd
from rclpy.publisher import Publisher
from std_msgs.msg import String
import random
import time


class Cerpm():
    def __init__(self, id, x, y, publisher: Publisher[String]) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.publisher: Publisher[String] = publisher
    
    def talk(self):
        msg = String()
        time.sleep(random.randint(0,2))
        msg.data = 'Hello from cerpm: %d' % self.id
        self.publisher.publish(msg)
        print(f'Published message from cerpm {self.id}')

class CerpmCluster(Node):

    def __init__(self):
        super().__init__('cerpm')
        self.cerpms: list[Cerpm] = []
        self.timer = self.create_timer(0.5, self.timer_callback)
        print('created cerpm_cluster')
        self.build_cerpm(1, 1, 1)
        self.build_cerpm(2, 2, 2)

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
            print('hi')
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