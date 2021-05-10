import socket
import pickle
import uuid
import json
from pathlib import Path
from threading import Thread
from service_execution import ServiceExecution
from runtime import RunTime
from api import API


class Agent:

    def __init__(self, node_info):
        self.generated_services_id = []
        self.service_execution = ServiceExecution(self)
        self.runtime = RunTime(self)
        self.API = API(self, host="0.0.0.0")
        self.API.start()


############################## UTILS ##############################

    def generate_service_id(self):
        random_id = uuid.uuid4()
        if random_id in self.generated_services_id:
            return self.generate_service_id()
        return random_id

