# Module Imports
import csv
import requests
import json
from tqdm import tqdm
import re
import logging
import sys
from pick import pick
import os
import yaml

# Load the config
config = os.path.normpath('etc/config.yml')
with open(config, 'r') as config_stream:
	config_variables = yaml.load(config_stream, Loader=yaml.BaseLoader)

# Global Variables
log_level = config_variables['Log_Level']
token = config_variables['FireDrill_Token']
head = {'Content-Type': 'application/json', 'Authorization': 'Token {}'.format(token)}
assessment_url = config_variables['FireDrill_URLs']['Assessment_URL']
tests_url = config_variables['FireDrill_URLs']['Tests_URL']
test_scenario_url = config_variables['FireDrill_URLs']['Test_Scenarios_URL']
projects_url = config_variables['FireDrill_URLs']['Projects_URL']
asset_group_url = config_variables['FireDrill_URLs']['Asset_Group_URL']
sophistication_lvls = ['Novice', 'Practitioner', 'Expert']
novice_ID = ''
pract_ID = ''
expert_ID = ''
current_assessments_full = []
current_assessments_name = []


class AssessmentCreationOrUpdate:

	def count_csv_lines(self, csv_file):
		with open(csv_file) as f:
			csv_reader = csv.reader(f)
			row_count = list(csv_reader)
			return len(row_count)

	def asset_group(self, asset_group_name, head):
		try:
			request = requests.get(asset_group_url + '?name=' + asset_group_name, headers=head)
			response = request.json()

			asset_group_ID = response["results"][0]["id"]
			return asset_group_ID
		except Exception as e:
			logging.error('Error finding FireDrill group named ' + asset_group_name + '. Please verify group exists within FireDrill.')
			logging.debug('Error message: ' + str(e))
			return "Error"

	def create_assessment(self, assessment_url, head):
		assessment_name = input('\nEnter Assessment Name (Using the MITRE ATT&CK template): ')
		logging.info('Creating assessment named ' + assessment_name)
		data = {'project_name': assessment_name, 'template': "73599a2c-ee91-44a8-b017-febccd64b364"}

		request = requests.post(assessment_url, data=json.dumps(data), headers=head)
		response = request.json()

		project_ID = response["project_id"]
		logging.info('Assessment creation complete. Project ID number: ' + project_ID)
		logging.debug('JSON: ' + request.text)
		return project_ID

	def create_tests(self, tests_url, head, project_ID, sophistication_lvls):
		logging.info('Creating test object for level ' + sophistication_lvls)
		data = {
			"name": sophistication_lvls,
			"project": project_ID
		}
		request = requests.post(tests_url, data=json.dumps(data), headers=head)
		response = request.json()

		logging.info('Test object creation complete. Test ID: ' + response["id"])
		logging.debug('JSON: ' + request.text)
		return response["id"]

	def assign_tests(self, scenario_ID, soph_level, tests_url, head):
		if soph_level == 'Novice':
			test_ID = novice_ID
		elif soph_level == 'Practitioner':
			test_ID = pract_ID
		elif soph_level == 'Expert':
			test_ID = expert_ID
		else:
			test_ID = soph_level

		test_modify_url = tests_url + '/' + test_ID + '/bulk_add_scenarios'

		logging.info('Assigning scenario with ID ' + scenario_ID + ' to ' + soph_level + ' test.')
		data = {
			"tag": [],
			"tag_set": [],
			"search": "",
			"supported_platforms": "",
			"id": test_ID,
			"include": [scenario_ID]
		}

		try:
			request = requests.post(test_modify_url, data=json.dumps(data), headers=head)
			response = request.json()
			test_scenario_ID = response["scenario_master_job_scenarios"][0]
			logging.info('Assignment of scenario ' + scenario_ID + ' to ' + soph_level + ' complete.')
			logging.debug('JSON: ' + request.text)
			return test_scenario_ID
		except Exception as e:
			logging.error('Error assigning scenario ' + scenario_ID + ' to ' + soph_level + '.')
			logging.debug('Error message: ' + str(e))
			return "Error"

	def assign_scenario_params(self, test_scenario_ID, scenario_JSON, scenario_ID, test_scenario_url, head):
		try:
			set_params_url = test_scenario_url + '/' + str(test_scenario_ID)
			test_scenario_string = str(test_scenario_ID)
			decoded_JSON = json.loads(scenario_JSON)

			logging.info('Setting required parameters for scenario ' + scenario_ID + '.')
			data = {
				"id": test_scenario_string,
				"model_json": decoded_JSON
			}
			request = requests.patch(set_params_url, data=json.dumps(data), headers=head)
		except ValueError as e:
			logging.error('Error encountered when working on {}. Error JSON: {}\n'.format(str(test_scenario_ID), str(scenario_JSON)))
			logging.error('Error Message: {}'.format(str(e)))

	def assign_assets(self, project_ID, head, asset_group_ID):
			data = {
				"asset_groups": asset_group_ID,
				"replace_existing": True
			}
			request = requests.post(projects_url + '/' + project_ID + '/update_defaults', data=json.dumps(data), headers=head)

	def set_schedule(self, project_ID, head):
		cron_sched = '0;16;*;*;*'
		data = {
			"default_schedule": cron_sched
		}
		request = requests.patch(projects_url + '/' + project_ID, data=json.dumps(data), headers=head)

	def activate_assessment(self, project_ID, head):
		activate_url = projects_url + '/' + project_ID + '/activate'
		request = requests.post(activate_url, headers=head)

	def check_tests(self, scenario_ID, soph_level, assessment_ID, scenario_JSON):
		request = requests.get(tests_url + '?project=' + str(assessment_ID), headers=head)
		response = request.json()
		mark_complete = False

		i = 0
		count = response["count"]

		while i < count:
			test_name = response["results"][i]["name"]
			if soph_level == test_name:
				scenario_count = len(response["results"][i]["scenarios"])
				j = 0

				while j < scenario_count:
					scenario_GUID = response["results"][i]["scenarios"][j]["id"]

					if scenario_ID == scenario_GUID:
						test_master_ID = response["results"][i]["id"]

						request2 = requests.get(test_scenario_url + '?scenario_master_job=' + test_master_ID, headers=head)
						response2 = request2.json()

						test_scenario_ID = response2["results"][0]["id"]
						decoded_JSON = json.loads(scenario_JSON)
						data = {
							"id": test_master_ID,
							"model_json": decoded_JSON
						}
						logging.info('Updating scenario {} on test {} in assessment'.format(test_scenario_ID,soph_level))
						requests.patch(test_scenario_url + '/' + test_scenario_ID, data=json.dumps(data), headers=head)
						mark_complete = True
					j += 1
				if not mark_complete:
					test_ID = response["results"][i]["id"]
					add_new = self.assign_tests(scenario_ID, test_ID, tests_url, head)
					self.assign_scenario_params(add_new, scenario_JSON, scenario_ID, test_scenario_url, head)
			i += 1

	def new_assessment(self, csv_master):
		# Start the logger
		log_file = os.path.normpath('data/InfernoAuger.log')
		log_format = '%(asctime)s - %(module)s - %(funcName)s - %(levelname)-8s %(message)s'
		logging.basicConfig(filename=log_file, format=log_format, datefmt='%a, %d %b %Y %H:%M:%S', level=log_level)

		asset_group_name = input('\nEnter name of asset group to assign: ')

		if asset_group_name:
			asset_group_ID = self.asset_group(asset_group_name, head)
			if asset_group_ID == "Error":
				print('\nError getting asset group. Please verify that group exists within FireDrill. View the log for more information.')
				sys.exit()

		project_ID = self.create_assessment(assessment_url, head)
		self.assign_assets(project_ID, head, asset_group_ID)

		global novice_ID
		global pract_ID
		global expert_ID

		for level in sophistication_lvls:
			return_ID = self.create_tests(tests_url, head, project_ID, level)
			if level == 'Novice':
				novice_ID = return_ID
			elif level == 'Practitioner':
				pract_ID = return_ID
			elif level == 'Expert':
				expert_ID = return_ID

		row_count = self.count_csv_lines(csv_master)
		bar = tqdm(total=row_count, ascii=True, desc='Progress: ', bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} | Estimated Time: {remaining}')

		try:
			with open(csv_master) as f:
				reader = csv.reader(f)
				next(reader, None)

				for row in reader:
					bar.update()
					scenario_ID = row[1]
					soph_level = row[2]
					scenario_JSON = row[3]
					if scenario_JSON == 'NOT USED':
						logging.info('Scenario ID {} for sophistication level {} not used. Skipping...'.format(scenario_ID,soph_level))
						continue
					test_scenario_ID = self.assign_tests(scenario_ID, soph_level, tests_url, head)
					if test_scenario_ID == "Error":
						logging.info('Error encountered, skipping scenario parameter assignment for scenario ' + scenario_ID + ' on test ' + soph_level + '.')
					else:
						self.assign_scenario_params(test_scenario_ID, scenario_JSON, scenario_ID, test_scenario_url, head)

		except OSError as e:
			logging.error('Error encountered reading CSV file. Please make sure file exists and is in CSV format.')
			logging.debug('Error Message: ' + str(e))
			print('\nError reading file. Please make sure the file exists and is in CSV format. View the log for more information.')
			logging.info('Cleaning up orphaned assessment ID ' + project_ID + '.')
			self.delete_assessment(project_ID, head)
			logging.info('Orphaned assessment ' + project_ID + ' deleted. Exiting InfernoAuger.')
			sys.exit()
		except Exception as g:
			print(str(g))

		self.set_schedule(project_ID, head)
		self.activate_assessment(project_ID, head)

	def update_assessment(self, csv_update):
		# Start the logger
		log_file = os.path.normpath('data/InfernoAuger.log')
		log_format = '%(asctime)s - %(module)s - %(funcName)s - %(levelname)-8s %(message)s'
		logging.basicConfig(filename=log_file, format=log_format, datefmt='%a, %d %b %Y %H:%M:%S', level=log_level)

		request = requests.get(projects_url, headers=head)
		response = request.json()

		for assessment in response["results"]:
			current_assessments_full.append('{}:{}'.format(assessment["name"],assessment["id"]))
			current_assessments_name.append(assessment["name"])
		update_title = 'Please select the assessment to modify: '
		current_assessments_full.sort()
		current_assessments_name.sort()
		option, index = pick(current_assessments_name, update_title)
		r = re.compile('.*' + option + ':')

		assessment_picked = list(filter(r.match, current_assessments_full))
		assessment_picked_str = assessment_picked[0]
		assessment_ID = assessment_picked_str.split(':')

		with open(csv_update) as f:
			reader = csv.reader(f)
			next(reader, None)

			for row in reader:
				scenario_ID = row[1]
				soph_level = row[2]
				scenario_JSON = row[3]

				self.check_tests(scenario_ID, soph_level, assessment_ID[1], scenario_JSON)

	def delete_assessment(self, project_ID, head):
		requests.delete(projects_url + '/' + project_ID, headers=head)
