# Imports
import requests
import logging
import yaml
import os

# Load the config
config = os.path.normpath('etc/config.yml')
with open(config, 'r') as config_stream:
	config_variables = yaml.load(config_stream, Loader=yaml.BaseLoader)

# Global Variables
log_level = config_variables['Log_Level']
scenario_url = config_variables['FireDrill_URLs']['Scenarios_URL']
token = config_variables['FireDrill_Token']
head = {'Authorization': 'token {}'.format(token)}
csv_file_name = os.path.normpath('data/scenarios/FireDrillScenarios.csv')


class Scenarios:

	def main(self):
		# Start the logger
		log_file = os.path.normpath('data/InfernoAuger.log')
		log_format = '%(asctime)s - %(module)s - %(funcName)s - %(levelname)-8s %(message)s'
		logging.basicConfig(filename=log_file, format=log_format, datefmt='%a, %d %b %Y %H:%M:%S', level=log_level)

		# Variables for initial API call
		request = requests.get(scenario_url, headers=head)
		response = request.json()
		count = len(response["results"])
		i = 0

		# Delete CSV file if it already exists
		if os.path.isfile(csv_file_name):
			os.remove(csv_file_name)

		# Create the CSV file and add the headers
		with open(csv_file_name, "a") as csv_file:
			csv_file.write("Name,ID,MITRE,Platforms,Parameters")
			csv_file.write('\n')

			print('Querying the API for scenarios. This may take a while...')

			# Parse through API, pulling out required fields (specifically for first page)
			while i < count:
				scenario_name = response["results"][i]["name"]
				scenario_ID = response["results"][i]["id"]

				tag_count = len(response["results"][i]["scenario_tags"])
				j = 0
				try:
					while j < tag_count:
						if response["results"][i]["scenario_tags"][j]["tag"]["tag_set_name"] == "MITRE ID":
							scenario_platforms = response["results"][i]["supported_platforms"]
							scenario_mitre = response["results"][i]["scenario_tags"][j]["tag"]["display_name"]
							scenario_name = scenario_name.replace(',', '')
							scenario_params_list = response["results"][i]["scenario_template"]["descriptor_json"]["resources"][0]["schema"]["properties"]
							scenario_params = '|'.join(scenario_params_list)
							if scenario_params == 'scripts':
								scenario_params_scripts_list = response["results"][i]["scenario_template"]["descriptor_json"]["resources"][0]["schema"]["properties"]["scripts"]["items"]["properties"].keys()
								scenario_params = '|'.join(scenario_params_scripts_list)
							elif scenario_params == 'browsers':
								scenario_params_browsers_list = response["results"][i]["scenario_template"]["descriptor_json"]["resources"][0]["schema"]["properties"]["browsers"]["default"]
								scenario_params = "|".join(scenario_params_browsers_list)
							elif scenario_params == 'registry':
								scenario_params_registry_list = response["results"][i]["scenario_template"]["descriptor_json"]["resources"][0]["schema"]["properties"]["registry"]["items"]["properties"].keys()
								scenario_params = "|".join(scenario_params_registry_list)
							elif scenario_params == 'services':
								scenario_params_services_list = response["results"][i]["scenario_template"]["descriptor_json"]["resources"][0]["schema"]["properties"]["services"]["items"]["properties"].keys()
								scenario_params = "|".join(scenario_params_services_list)
							elif scenario_params == 'tool':
								scenario_params_tool_list = response["results"][i]["scenario_template"]["descriptor_json"]["resources"][0]["schema"]["properties"]["tool"]["default"]
								scenario_params = "|".join(scenario_params_tool_list)
							csv_line = scenario_name + "," + scenario_ID + "," + scenario_mitre + "," + '|'.join(scenario_platforms) + "," + scenario_params
							csv_file.write(csv_line)
							csv_file.write('\n')
						j += 1
				except Exception as e:
					logging.error('Error writing scenario. Message:\n\t{}'.format((response["results"][j]["name"]) + " : " + str(e)))
					csv_line = scenario_name + "," + scenario_ID + "," + scenario_mitre + "," + '|'.join(scenario_platforms) + ","
					csv_file.write(csv_line)
					csv_file.write('\n')
				i += 1

			# Parse through all of API pages until there is no more, writing the required fields to the CSV
			while response["next"]:
				request = requests.get(response["next"], headers=head)
				response = request.json()
				count = len(response["results"])
				k = 0
				while k < count:
					scenario_name = response["results"][k]["name"]
					scenario_ID = response["results"][k]["id"]

					tag_count = len(response["results"][k]["scenario_tags"])
					l = 0
					try:
						while l < tag_count:
							if response["results"][k]["scenario_tags"][l]["tag"]["tag_set_name"] == "MITRE ID":
								scenario_platforms = response["results"][k]["supported_platforms"]
								scenario_mitre = response["results"][k]["scenario_tags"][l]["tag"]["display_name"]
								scenario_name = scenario_name.replace(',', '')
								scenario_params_list = response["results"][k]["scenario_template"]["descriptor_json"]["resources"][0]["schema"]["properties"]
								scenario_params = '|'.join(scenario_params_list)
								if scenario_params == 'scripts':
									scenario_params_scripts_list = response["results"][k]["scenario_template"]["descriptor_json"]["resources"][0]["schema"]["properties"]["scripts"]["items"]["properties"].keys()
									scenario_params = '|'.join(scenario_params_scripts_list)
								elif scenario_params == 'browsers':
									scenario_params_browsers_list = response["results"][k]["scenario_template"]["descriptor_json"]["resources"][0]["schema"]["properties"]["browsers"]["default"]
									scenario_params = "|".join(scenario_params_browsers_list)
								elif scenario_params == 'registry':
									scenario_params_registry_list = response["results"][k]["scenario_template"]["descriptor_json"]["resources"][0]["schema"]["properties"]["registry"]["items"]["properties"].keys()
									scenario_params = "|".join(scenario_params_registry_list)
								elif scenario_params == 'services':
									scenario_params_services_list = response["results"][k]["scenario_template"]["descriptor_json"]["resources"][0]["schema"]["properties"]["services"]["items"]["properties"].keys()
									scenario_params = "|".join(scenario_params_services_list)
								elif scenario_params == 'tool':
									scenario_params_tool_list = response["results"][k]["scenario_template"]["descriptor_json"]["resources"][0]["schema"]["properties"]["tool"]["default"]
									scenario_params = "|".join(scenario_params_tool_list)
								csv_line = scenario_name + "," + scenario_ID + "," + scenario_mitre + "," + '|'.join(scenario_platforms) + "," + scenario_params
								csv_file.write(csv_line)
								csv_file.write('\n')
							l += 1
					except Exception as e:
						logging.error('Error writing scenario. Message:\n\t{}'.format((response["results"][k]["name"]) + " : " + str(e)))
						csv_line = scenario_name + "," + scenario_ID + "," + scenario_mitre + "," + '|'.join(scenario_platforms) + ","
						csv_file.write(csv_line)
						csv_file.write('\n')
					k += 1

