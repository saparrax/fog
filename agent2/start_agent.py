import json
import os.path
from agent import Agent


if os.path.exists("/home/mfrontignan/agent2/device.config"):
	config = open("/home/mfrontignan/agent2/device.config", "r")
	node_info = json.load(config)
	agent = Agent(node_info)

	while True:
		pass
