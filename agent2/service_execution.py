import time
import uuid
import json
from threading import Thread


class ServiceExecution:

    def __init__(self, agent):
        self.agent = agent
        self.running_dependencies = {}
        self.dependency_of = {}
        self.pending_services = {}

    def request_service(self, service):
        print("REQUEST SERVICE")
        reg_service = self.agent.API.get_service(service)
        self.fill_service(service, reg_service)
        if "dependencies" in service.keys():
            for dependency in service.get("dependencies"):
                service_to_request = {"service_id": dependency}
                service_to_request["params"] = service["params"] if "params" in service.keys() else None
                result_dependency = self.agent.API.request_service_to_me(service_to_request)
                self.get_params_from_result(service, result_dependency)
        return self.agent.API.delegate_service(service)

    def get_params_from_result(self, service, result):
        print("PARAMETRES DEL SERVEI ")
        print(result)
        if "status" in result.keys() and result["status"] == "success" and "output" in result.keys():
            print("Resultado: ", result)
            print(type(result["output"]))
            try:
                result["output"] = json.loads(result["output"])
                print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                print(result["output"])
                output=result["output"]
                if "params" not in service.keys():
                    service["params"] = result["output"]
                else:
                    for key, value in result["output"].items():
                        service["params"][key] = value
            except:
                print("Me ha petado con el output", result)

    def merge_params(self, service, params):
        if "params" not in service.keys():
            service["params"] = {}
        for param in params.keys():
            service["params"][param] = params[param]

    def fill_service(self, service, reg_service={}):
        random_id = str(self.agent.generate_service_id())
        for key in reg_service.keys():
            if key not in service.keys() and key != "params":
                service[key] = reg_service[key]
