import requests
import os.path
import os
import subprocess
import json
import psutil
from pick import pick

import pymongo
from bson import ObjectId
from pymongo import MongoClient

def main():

    services_list = list_services()
    services_list.append("EXIT")
    title = "Elige un servicio a solicitar:"
    service_id, index = pick(services_list, title, indicator="=>")
    request = {}
    if service_id != "EXIT":
        service_id = service_id.split(':')[0]
        service = find_service(service_id)
        print(service)
        request["service_id"] = service_id
        request["params"] = {}
        if service.get("params"):
            os.system("clear")
            print("Introduce los parametros del servicio: ")
            params = service["params"]
            request["params"] = params
            for param in params:
                value = input("\t{}: ".format(param))
                request["params"][param] = value
            print(request["params"])
            input("\nPulsa ENTER para solicitar el servicio {}".format(service_id))
        request["agent_ip"] = "localhost"
        result = request_service(request)
        show_result(result, service_id)
        #os.system("clear")


def find_service(_id):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient['test']
    mycol = mydb['tfg']
    myquery = {"_id": "{0}".format(_id)}
    mydoc = mycol.find_one(myquery)
    return mydoc


def list_services():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient['test']
    mycol = mydb['tfg']
    mydoc = mycol.find()
    my_list = []
    for i in mydoc:
        my_list.append(i["_id"])
    return my_list


def request_service(service):
    print("aaaaaa")
    print(service)
    result = requests.post(
        "http://{}:8000/request_service".format("localhost"), json=service).text
    return result


def show_result(result, service_id):
    os.system("clear")
    # result=json.loads(result_output)
    print("RESULTADO DEL SERVICIO {}:\n".format(service_id))
    print(result)


def start_agent():
    try:
        subprocess.call(
            "python3 /home/saparra/tfg/hug/serveis/agent2/start_agent.py &", shell=True)
    except:
        print ("Exit")


if __name__ == '__main__':
    main()
