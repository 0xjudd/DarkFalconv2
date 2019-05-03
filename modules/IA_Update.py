# Imports
from email.message import EmailMessage
import requests
import os
import sys
import smtplib
import yaml

# Load the config
config = os.path.normpath('etc/config.yml')
with open(config, 'r') as config_stream:
	config_variables = yaml.load(config_stream, Loader=yaml.BaseLoader)

# Global Variables
firedrill_url = config_variables['FireDrill_URLs']['Scenarios_URL']
token = config_variables['FireDrill_Token']
head = {'Authorization': 'token {}'.format(token)}
current_file = os.path.normpath('data/update/currentscenarios.txt')
new_file = os.path.normpath('data/update/newscenarios.csv')
results_num = os.path.normpath('data/update/results.txt')
email_array = []


class UpdateScenarioList:

	def check_num_scenarios(self, r_contents):
		request = requests.get(firedrill_url, headers=head)
		response = request.json()
		count = response["count"]

		print('\nChecking for new scenarios...\n')

		# Check if there are any new scenarios in FireDrill
		if int(count) == int(r_contents):
			print('No new scenarios found. Exiting...\n\tScenario Count: {}\n\tOld Count: {}'.format(count, r_contents))
			sys.exit()
		else:
			print('\tScenario Count: {}\n\tOld Count: {}\n\nNew scenarios found. Querying API for new MITRE scenarios. This may take a while...'.format(count,r_contents))
			overwrite_file = open(results_num, 'w')
			overwrite_file.write(str(count))
			overwrite_file.close()
			return False

	def send_email(self, email_array):
		msg = EmailMessage()
		smtp_server = smtplib.SMTP(config_variables['Email']['SMTP_Server'], config_variables['Email']['SMTP_Port'])
		array_to_string = '\n'.join(email_array)
		message = """
New FireDrill scenarios have been created related to the MITRE framework. The new scenarios have been added to the update spreadsheet and are listed below:
	
{}
	
	""".format(array_to_string)

		msg['Subject'] = 'New FireDrill MITRE Scenarios'
		msg['From'] = config_variables['Email']['Sender']
		msg['To'] = config_variables['Email']['Recipient']
		msg.set_content(message)

		smtp_server.send_message(msg)
		smtp_server.quit()

	def main(self):
		# Delete new file from previous run
		if os.path.isfile(new_file):
			os.remove(new_file)

		# Get old (last run) number of scenarios
		r_file = open(results_num, 'r')
		r_contents = r_file.read()
		r_file.close()

		return_value = self.check_num_scenarios(r_contents)

		if not return_value:

			c_file = open(current_file, 'r')
			c_contents = [line.rstrip() for line in c_file.readlines()]
			c_file.close()

			append_file = open(current_file, 'a')

			n_file = open(new_file, 'a+')
			n_file.write('Name,ID,Sophistication,JSON\n')

			request = requests.get(firedrill_url, headers=head)
			response = request.json()
			count = len(response["results"])
			i = 0

			while i < count:
				scenario_name = response["results"][i]["name"]
				scenario_ID = response["results"][i]["id"]

				tag_count = len(response["results"][i]["scenario_tags"])
				j = 0

				while j < tag_count:
					if response["results"][i]["scenario_tags"][j]["tag"]["tag_set_name"] == "MITRE ID":
						scenario_name = scenario_name.replace(',', '')
						if scenario_name not in c_contents:
							append_file.write('\n{}'.format(scenario_name))
							email_array.append(scenario_name)
							n_file.write(scenario_name + ',' + scenario_ID + ',' + 'Novice' + ',\n')
							n_file.write(scenario_name + ',' + scenario_ID + ',' + 'Practitioner' + ',\n')
							n_file.write(scenario_name + ',' + scenario_ID + ',' + 'Expert' + ',\n')
					j += 1
				i += 1

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

					while l < tag_count:
						if response["results"][k]["scenario_tags"][l]["tag"]["tag_set_name"] == "MITRE ID":
							scenario_name = scenario_name.replace(',', '')
							if scenario_name not in c_contents:
								append_file.write('\n{}'.format(scenario_name))
								email_array.append(scenario_name)
								n_file.write(scenario_name + ',' + scenario_ID + ',' + 'Novice' + ',\n')
								n_file.write(scenario_name + ',' + scenario_ID + ',' + 'Practitioner' + ',\n')
								n_file.write(scenario_name + ',' + scenario_ID + ',' + 'Expert' + ',\n')
						l += 1
					k += 1

			if email_array:
				self.send_email(email_array)
