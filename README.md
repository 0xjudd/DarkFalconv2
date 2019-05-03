# InfernoAuger

InfernoAuger is a tool to help automate many components related to AttackIQ's adversary simulation tool, FireDrill. There are five main modules within InfernoAuger:

 * Main - This is the core module. This module allows for the creation and update of assessments within the FireDrill tool with pre-configured scenario parameters. The scenarios are configured by sophistication levels required to perform such an attack.
 * Detection - This module pushes results from FireDrill's attack detection component into a Splunk lookup file. This information can then be used within Splunk for further correlation or analytics.
 * Status - This module checks the progress of an assessment's run. It will automatically refresh it's information until the assessment run completes, providing some basic status information.
 * Scenarios - This module creates a CSV file containing all of FireDrill's scenarios tagged as part of the MITRE ATT&CK framework. The CSV will contain information such as: MITRE Technique ID, supported platforms, scenario parameters, etc.
 * Update - This module checks for any new MITRE ATT&CK tagged scenarios within FireDrill since its' previous run, and sends an e-mail to a specified account with a list of new scenarios. It also creates a CSV in the format that the "Main" module requires for updating.
 
 Setup
 -----
 To prepare InfernoAuger for usage, please run the setup file in the "bin" directory like the following: `python bin\setup.py`
 
 This script will walk you through the installation. Since the Detection module requires a username/password to connect to a Splunk instance,
 a portion of the setup will generate a public/private key pair and prompt for your Splunk account's password to encrypt. If you are not using 
 the Detection module, this option can be ignored.
 
 After installation, copy the `etc\config_TEMPLATE.yml` file to `etc\config.yml` and fill in all the appropriate information (NOTE: Only the items encased in <> are required to be populated)
 
 Usage
 -----
 Full usage information can be found at this blog post here: https://security-storm.squarespace.com/playbook/2019/5/3/automating-firedrill-adsim-configuration-with-infernoauger
 
 Below is a quick run down on how to use each module:
 
 #### Main
 `python InfernoAuger.py -m Main -f <MASTER_CONFIG_LOC> <create/update>`

##### Examples
 Create a new assessment using the sample config CSV in the samples directory:
 
 `python InfernoAuger.py -m Main -f samples\master_config_sample.csv create`
 
 Update an existing assessment with the sample update config CSV in the samples directory:
 
 `python InfernoAuger.py -m Main -f samples\update_config_sample.csv update`
 
 Update an existing assessment, specifying the assessment to update in the command line:
 
 `python InfernoAuger.py -m Main -f samples\update_config_sample.csv -a 11111111-1111-1111-111111111111 update`
 
 #### Detection
 `python InfernoAuger.py -m Detection`
 
 ##### Examples
 
 Pull detection results from FireDrill, specifying an assessment post-command:
 
 `python InfernoAuger.py -m Detection`
 
 Pull detection results from FireDrill, specifying the assessment in the command line:
 
 `python InfernoAuger.py -m Detection -a 11111111-1111-1111-111111111111`
 
 #### Status
 `python InfernoAuger.py -m Status <scheduled/ondemand>`
 
 ##### Examples
 
 Get the status of a scheduled assessment run:
 
 `python InfernoAuger.py -m Status scheduled`
 
 Get the status of an on-demand assessment run, specifying the assessment in the command line:
 
 `python InfernoAuger.py -m Status -a 11111111-1111-1111-111111111111 ondemand`
 
 #### Scenarios
 
 `python InfernoAuger.py -m Scenarios`
 
 ##### Examples
 
 Pull all MITRE ATT&CK scenarios from FireDrill:
 
 `python InfernoAuger.py -m Scenarios`
 
 #### Update
 
 `python InfernoAuger.py -m Update`
 
 ##### Examples
 
 Get the new MITRE ATT&CK scenarios since the last run:
 
 `python InfernoAuger.py -m Update`
 
 Licensing
 ---------
 This program is licensed under GNU GPL v3. For more information, please reference the LICENSE file that came with this program or visit https://www.gnu.org/licenses/.
 
 Issues or Concerns
 ------------------
 If you run into any issues using this tool or have any questions, please feel free to open an Issue within the GitHub repository.