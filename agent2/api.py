import cherrypy
import pymongo
import requests
import json
import datetime

import pymongo
from bson import ObjectId
from pymongo import MongoClient


@cherrypy.expose
class API(object):

    def __init__(self, agent, host='localhost', port=4321):
        self.agent = agent
        self.host = host
        self.port = port

    @cherrypy.tools.json_out()
    def GET(self, obj=None, id=None):
        if obj == "service":
            return self.get_service(id)
        elif obj == "a":
            return self.raspy()

    @cherrypy.tools.json_in()
    def POST(self, action=None):
        info = cherrypy.request.json
        result = ""
        if action == "request_service":
            result = self.request_service(info)
        elif action == "execute_service":
            result = self.execute_service(info)
        elif action == "prova":
            result="OK"
        return self.return_data(result)

    def start(self, silent_access=False):
        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True,
                'tools.response_headers.on': True,
                'tools.response_headers.headers': [
                    ('Access-Control-Allow-Origin', '*'),
                    ('Content-Type', '*')
                ]
            }
        }
        cherrypy.config.update({'log.screen': not silent_access})
        #cherrypy.server.socket_host = self.host
        cherrypy.server.socket_host = '0.0.0.0'
        cherrypy.server.socket_port = self.port
        cherrypy.quickstart(API(self.agent), '/', conf)

    def stop(self):
        cherrypy.engine.exit()

    def get_service(self, input=None):
        print("OBTENIR SERVEI: ")
        print(input)
        service = self.find_service(input['service_id'])
        return service

    def request_service(self, service):
        print("REQUEST_SERVICE:", service)
        return self.agent.service_execution.request_service(service)

    def execute_service(self, service):
        return self.agent.runtime.execute_service(service)

    def delegate_service(self, service):
        try:
            response = requests.post(
                "http://localhost:4321/execute_service", json=service)
            status_code = response.status_code
            return json.loads(response.text)
        except Exception as e:
            # print(e)
            status_code = -1
        if status_code != 200:
            pass
            # print("No se ha podido delegar el servicio {} al agent".format(service["service_id"]))

    def request_service_to_me(self, service):
        try:
            response = requests.post(
                "http://localhost:4321/request_service", json=service)
            status_code = response.status_code
            return json.loads(response.text)
        except Exception as e:
            # print(e)
            status_code = -1
            return
        if status_code != 200:
            pass
            # print("No me he podido pedir el servicio")

    def return_data(self, data):
        result = ""
        if isinstance(data, dict):
            result = json.dumps(data)
        elif isinstance(data, int):
            result = str(data)
        elif isinstance(data, list):
            result = str(data)
        elif data is not None:
            result = data
        return result.encode()

    def find_service(self, _id):
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient['test']
        mycol = mydb['tfg']
        myquery = {"_id": "{0}".format(_id)}
        mydoc = mycol.find_one(myquery)
        return mydoc

    def raspy(self):
        return "Hello World2"
