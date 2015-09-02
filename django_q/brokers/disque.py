import random
import redis
from django_q.brokers import Broker
from django_q.conf import Conf


class Disque(Broker):

    def enqueue(self, task):
        return self.connection.execute_command(
            'ADDJOB {} {} 500 RETRY {}'.format(self.list_key, task, Conf.RETRY)).decode()

    def dequeue(self):
        task = self.connection.execute_command('GETJOB TIMEOUT 1000 FROM {}'.format(self.list_key))
        if task:
            return task[0][1].decode(), task[0][2].decode()

    def queue_size(self):
        return self.connection.execute_command('QLEN {}'.format(self.list_key))

    def acknowledge(self, task_id):
        return self.connection.execute_command('ACKJOB {}'.format(task_id))

    def ping(self):
        return self.connection.ping()

    def delete(self, task_id):
        return self.connection.execute_command('DELJOB {}'.format(task_id))

    def delete_queue(self):
        jobs = self.connection.execute_command('JSCAN QUEUE {}'.format(self.list_key))[1]
        if jobs:
            self.connection.execute_command('DELJOB {}'.format(' '.join(map(str, jobs))))

    @staticmethod
    def get_connection(list_key=Conf.PREFIX):
        # randomize nodes
        random.shuffle(Conf.DISQUE)
        # find one that works
        for node in Conf.DISQUE:
            host, port = node.split(':')
            redis_client = redis.Redis(host, int(port))
            try:
                if Conf.DISQUE_AUTH:
                    redis_client.execute_command('AUTH {}'.format(Conf.DISQUE_AUTH))
                redis_client.decode_responses = True
                redis_client.execute_command('HELLO')
                return redis_client
            except redis.exceptions.ConnectionError:
                continue
        raise ConnectionError('Could not connect to any Disque nodes')
