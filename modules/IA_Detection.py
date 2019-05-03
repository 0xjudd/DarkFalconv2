# Imports
import requests
import sys
import logging
import splunklib.client as client
import splunklib.results as results
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import base64
import yaml
import os

# Load the config
config = os.path.normpath('etc/config.yml')
with open(config, 'r') as config_stream:
	config_variables = yaml.load(config_stream, Loader=yaml.BaseLoader)

# Global Variables
log_level = config_variables['Log_Level']
projects_url = config_variables['FireDrill_URLs']['Projects_URL']
vendor_results = config_variables['FireDrill_URLs']['Vendor_Products_URL']
token = config_variables['FireDrill_Token']
assessment_name = config_variables['FireDrill_Assessment']
head = {'Authorization': 'token {}'.format(token)}
priv_key = config_variables['Splunk']['Password_Decryption_Key']
password_encrypt = config_variables['Splunk']['Encrypted_Password']
current_assessments_full = []
current_assessments_name = []
scenario_and_ID = []
detection_results_full = []
splunk_host = config_variables['Splunk']['Splunk_Server']
splunk_port = config_variables['Splunk']['Splunk_Port']
username = config_variables['Splunk']['Username']
lookup_file = config_variables['Splunk']['Detection_Lookup_File']
search_kwargs = {'earliest_time': '-24h', 'latest_time': 'now'}


class DetectionResults:

	def get_assessment(self):
		request = requests.get(projects_url, headers=head)
		response = request.json()

		i = 0
		count = len(response["results"])
		assessment_id = None

		while i < count:
			scenario_name = response["results"][i]["name"]
			if scenario_name == assessment_name:
				assessment_id = response["results"][i]["id"]
				break
			else:
				i += 1
		if not assessment_id:
			print('Assessment with name {} not found.'.format(assessment_name))
			sys.exit()
		return assessment_id

	def get_password(self):
		try:
			key_file = RSA.importKey(open(priv_key, 'r').read())
			decryptor = PKCS1_OAEP.new(key_file)
		except Exception as e:
			logging.error('Unable to open file ' + priv_key + '. Verify file exists and contains the appropriate key.')
			logging.error('Error message: ' + str(e))
			sys.exit()

		try:
			file = open(os.path.normpath('etc/{}').format(password_encrypt), 'r')
			decoded = base64.b64decode(file.read())
			password = decryptor.decrypt(decoded)
		except Exception as e:
			logging.error('Unable to open file ' + password_encrypt + '. Verify file exists and contains the appropriate Base64-encoded encryption string.')
			logging.error('Error message: ' + str(e))
			sys.exit()
		file.close()
		return password

	def send_results(self, s_service, s_name, t_name, c_product, c_vendor, s_type, o_id, o_name):
		search_query = """
| makeresults
| eval scenario_name="{}"
| eval test_name="{}"
| eval control_product="{}"
| eval control_vendor="{}"
| eval sourcetype="{}"
| eval outcome_id="{}"
| eval outname_name="{}"
| eval date_added=now()
| outputlookup append=true {}
""".format(s_name, t_name, c_product, c_vendor, s_type, o_id, o_name, lookup_file)

		try:
			search_results = s_service.jobs.oneshot(search_query, **search_kwargs)
		except Exception as e:
			logging.error('Unable to connect to Splunk. Please verify Splunk is up and running.')
			logging.debug('Error message: ' + str(e))
			return

		reader = results.ResultsReader(search_results)
		for item in reader:
			logging.error('Splunk Results: ' + str(item))

	def main(self, assessment_id):
		# Start the logger
		log_file = os.path.normpath('data/InfernoAuger.log')
		log_format = '%(asctime)s - %(module)s - %(funcName)s - %(levelname)-8s %(message)s'
		logging.basicConfig(filename=log_file, format=log_format, datefmt='%a, %d %b %Y %H:%M:%S', level=log_level)

		password = self.get_password()
		try:
			service = client.connect(host=splunk_host, port=splunk_port, username=username, password=password, app='SA-darkfalcon')
		except Exception as e:
			logging.error('Unable to connect to Splunk. Please verify Splunk is up and running and the username/password are correct.')
			logging.debug('Error message: ' + str(e))
			sys.exit()

		if not assessment_id:
			assessment_id = self.get_assessment()

		print('\nPulling detection results and pushing them to Splunk. This may take a while. To monitor progress, run "|inputlookup {}" in your Splunk instance.'.format(lookup_file))

		i = 0
		request = requests.get(vendor_results + '?project_id=' + assessment_id + "&show_last_result=true", headers=head)
		response = request.json()
		response_count = len(response["results"])

		while i < response_count:
			product_split = response["results"][i]["vendor_product_name"]
			scenario_name = response["results"][i]["scenario_name"]
			test_name = response["results"][i]["master_job_name"]
			control_product = product_split.split('-', 1)[0]
			control_vendor = response["results"][i]["vendor_name"]
			source_type = product_split.split('-', 1)[1]
			outcome_id = response["results"][i]["outcome"]
			outcome_name = response["results"][i]["outcome_name"]

			self.send_results(service, scenario_name, test_name, control_product, control_vendor, source_type, outcome_id, outcome_name)
			i += 1

		while response["next"]:
			request = requests.get(response["next"], headers=head)
			response = request.json()
			k = 0
			resp_count = len(response["results"])

			while k < resp_count:
				product_split = response["results"][k]["vendor_product_name"]
				scenario_name = response["results"][k]["scenario_name"]
				test_name = response["results"][k]["master_job_name"]
				control_product = product_split.split('-', 1)[0]
				control_vendor = response["results"][k]["vendor_name"]
				source_type = product_split.split('-', 1)[1]
				outcome_id = response["results"][k]["outcome"]
				outcome_name = response["results"][k]["outcome_name"]

				self.send_results(service, scenario_name, test_name, control_product, control_vendor, source_type, outcome_id, outcome_name)
				k += 1
