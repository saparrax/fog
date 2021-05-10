import os
import json
import subprocess
import time
import requests
from threading import Thread


class RunTime:

    def __init__(self, agent):
        self.agent = agent
        self.port = 5000
        self.infinite_services = {}
#getip abans i despres es passa al metode get code i passar
    def execute_service(self, service):
        code = service["code"]
        params = self.prepare_params(service)
        print ("Entra 1")
        #self.get_code(code, service)
        print ("Entra 2")
        #self.get_dependencies_codes(service.get("dependencies_codes"), service)
        print ("Entra 3")
        result = {
            "type": "service_result",
            "status": "unattended",
        }
        if service["ip"]=='':
            print ("ENTRA 4")
            output = self.execute_code(
                service["python_version"], code, params, service)
            if self.check_error(output):
                result = self.get_result(output, "error")
            else:
                result = self.get_result(output, "success")
        #elif service["service_id"] not in self.infinite_services:
        else:
            print ("Entra 5")
            port = self.port
            #self.infinite_services[service["service_id"]] = {
            #    "ip": "localhost",
            #    "port": port
            #}
            print ("NOU THREAD")
            params = self.add_socket_params(params)
            t1 = Thread(target=self.execute_code, args=(
                service["python_version"], code, params, service))
            t1.start()
            socket_ip = service["service_id"]+"_ip"
            socket_port = service["service_id"]+"_port"
            # posar nova ip
            output = json.dumps({
                socket_ip: service["ip"],
                socket_port: port
            })
            result = self.get_result(output, "success")
        ##print("HAGO RESULT DE", result)
        return result

    def add_socket_params(self, params):
                                # afegir ip i port correcte--> execució inicial
        params += "ip=" + "localhost" + " port=" + str(self.port)
        self.port += 2
        return params

    def get_result(self, output, status):
        return {
            "type": "service_result",
            "status": status,
            "output": output
        }

    def check_error(self, output):
        try:
            error = output.split(":")[0]
            return error == "ERROR"
        except:
            return False

    def get_code(self, code, ip):
        if self.has_service_code(code,ip)=="False":
            self.send_remote_file(code, ip)

    def get_dependencies_codes(self, codes, service):
        if codes:
            for code in codes.split(" "):
                self.get_code(code, service)

    def prepare_params(self, service):
        params = service.get("params")
        print("PREPARE PARAMS EXECUTION:", params)
        result = ""
        if params:
            for key, value in params.items():
                if value:
                    if(type(value) is dict):
                        result += key + "='" + json.dumps(value) + "' "
                    elif(type(value) is list):
                        result += key + "=" + str(value) + " "
                        # for item in value:
                        # result+=item+"@"
                        #result += " "
                    elif value != "":
                        result += key + "=" + str(value) + " "
        return result

    def execute_code(self, python_version, code, params, servei):
                                # executar codi gestion, necessito output? executar ssh o api? || crear crida pi
        print("Voy a ejecutar: {} {} {}".format(python_version, code, params))
        if params:
            print("HAY PARAMS")
            if(servei["ip"]=="vehicle"):
            #if (servei["service_id"] == "RECOLLIDA" or servei["service_id"] == "RECOLLIDA_MULTIPLE" or servei["service_id"] == "RESERVA"):
                # crida api get ip
                service = {}
                data = {}
                data["servei"] = servei["service_id"]
                data["id"] = servei["params"]["id"]
                ip = requests.get(
                    "http://147.83.159.200:3001/getIpVehicle", json=data)
                service["python_version"] = python_version
                service["code"] = code
                service["params"] = params
                ipCar = (json.loads(ip.content.decode("utf-8")[1:-1]))['ip']
                self.get_code(code, ipCar)
                print("EXECUCCIO API")
                output = "output-------------------------------------------------------------"

                requests.post(
                    "http://{}:8000/execute".format(ipCar), json=service)

                """HOST = "pi@10.0.1.1877777"
                COMMAND = "{} /home/pi/sapi/codes/{} {}".format(python_version, code, params)
                output = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],shell=False, stdout = subprocess.PIPE,stderr = subprocess.PIPE)"""
            else:
                output = subprocess.getoutput(
                    python_version + " /etc/agent/codes/" + code + " " + params)
                print("OUTPUT")
                print(output)

        else:
            print("NO HAY PARAMS")
            output = subprocess.getoutput(
                python_version + " /etc/agent/codes/" + code)
            # output="test"
        return output

    def get_remote_file(self, code, ip):
                                # obtenir codis remotament
        file = open("/etc/agent/codes/" + code, 'wb')
        content = requests.get("http://{}:{}/download/{}".format(
            service["download_host"], service["download_port"], code)).content
        file.write(content)
        file.close()

    def send_remote_file(self, code, ip):
        # obtenir codis remotament
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print(code)
        p = subprocess.Popen(["scp", "/etc/agent/codes/"+code, "pi@{}:/etc/agent/codes".format(ip)])
        sts = os.waitpid(p.pid, 0)

    def has_service_code(self, code, ip):
        # Comprovar si te els codis via API/ssh
        #return os.path.isfile("/etc/agent/codes/" + code)
        service={}
        service["code"]=code
        b=requests.get("http://{}:8000/has_code".format(ip), json=service)
        print(b.content.decode("utf-8").capitalize())
        return (b.content.decode("utf-8").capitalize())
