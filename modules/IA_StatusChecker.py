import requests
import re
from pick import pick
import time
import logging
from prettytable import PrettyTable
from platform import system
import yaml
import sys
import os

# Load the config
config = os.path.normpath('etc/config.yml')
with open(config, 'r') as config_stream:
	config_variables = yaml.load(config_stream, Loader=yaml.BaseLoader)

log_level = config_variables['Log_Level']
projects_url = config_variables['FireDrill_URLs']['Projects_URL']
token = config_variables['FireDrill_Token']
head = {'Authorization': 'token {}'.format(token)}
current_assessments_full = []
current_assessments_name = []
num_status = 3


class StatusChecker:

	def get_assessment(self):
		request = requests.get(projects_url, headers=head)
		response = request.json()

		for assessment in response["results"]:
			current_assessments_full.append('{}:{}'.format(assessment["name"], assessment["id"]))
			current_assessments_name.append(assessment["name"])
		update_title = 'Please select the assessment to view: '
		current_assessments_full.sort()
		current_assessments_name.sort()
		option, index = pick(current_assessments_name, update_title)
		r = re.compile('.*' + option + ':')
		assessment_picked = list(filter(r.match, current_assessments_full))
		assessment_picked_str = assessment_picked[0]
		assessID = assessment_picked_str.split(':')
		return assessID[1]

	def get_run_info(self, assessment_ID, endpoint_url):
		full_url = endpoint_url + '?project_id=' + assessment_ID
		request = requests.get(full_url, headers=head)
		response = request.json()
		return response

	def pull_results(self, assessment_ID, endpoint_url):
		self.clear_screen()
		loop_status = 0
		run_info = self.get_run_info(assessment_ID, endpoint_url)

		latest_run = run_info["results"][0]

		pending_count = latest_run["pending_count"]
		run_status = latest_run["running"]

		print("Assessment: {}\n".format(assessment_ID))
		print('Pending Scenarios: {}'.format(pending_count))
		print('Running?: {}\n'.format(run_status))

		table = PrettyTable(['Status Name', 'Count', 'Total %'])

		while loop_status < num_status:
			statName = latest_run["assessment_status"][loop_status]["name"]
			statCount = latest_run["assessment_status"][loop_status]["count"]
			statPct = latest_run["assessment_status"][loop_status]["pct"]
			table.add_row([statName, statCount, statPct])
			loop_status += 1
		print(table)
		return run_status

	def clear_screen(self):
		# Check for operating system type
		if system().lower() == 'windows':
			os.system('cls')
		else:
			os.system('clear')

	def main(self, i_assessment_id, module_args):
		# Start the logger
		log_file = os.path.normpath('data/InfernoAuger.log')
		log_format = '%(asctime)s - %(module)s - %(funcName)s - %(levelname)-8s %(message)s'
		logging.basicConfig(filename=log_file, format=log_format, datefmt='%a, %d %b %Y %H:%M:%S', level=log_level)

		status_run = 0
		if i_assessment_id:
			assessment_id = i_assessment_id
		else:
			assessment_id = self.get_assessment()

		if module_args == 'scheduled':
			endpoint_url = config_variables['FireDrill_URLs']['Scheduled_Run_URL']
		elif module_args == 'ondemand':
			endpoint_url = config_variables['FireDrill_URLs']['On_Demand_Run_URL']
		else:
			print('Please specify "scheduled" or "ondemand" to determine type of assessment run to query.')
			sys.exit()

		while status_run == 0:
			run_status = self.pull_results(assessment_id, endpoint_url)
			if not run_status:
				status_run += 1
				sys.exit()
			time.sleep(120)
