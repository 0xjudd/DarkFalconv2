import argparse
import os
import yaml
import sys

from bin.module_switcher import ModuleSwitcher

config = os.path.normpath('etc/config.yml')
header_file = os.path.normpath('rsrc/header.txt')


def parse_args(modules):
	parser = argparse.ArgumentParser()
	parser.add_argument('-m', '--module', help='Module to run')
	parser.add_argument('-a', '--assessment', help='Assessment ID to process')
	parser.add_argument('-f', '--file', help='File to process')
	parser.add_argument('module_args', help='Other arguments that may be required by a specific module', nargs='?')
	args = parser.parse_args()

	if args.module in modules:
		p_module = args.module
	else:
		print('Unknown module. Module List:\n\t{}'.format('\n\t'.join(modules)))
		sys.exit()

	if args.assessment and args.module in ['Detection', 'Update', 'Status']:
		p_assessment_id = args.assessment
	else:
		p_assessment_id = None

	if args.file:
		p_input_file = args.file
	else:
		p_input_file = None

	if args.module_args:
		p_module_args = args.module_args
	else:
		p_module_args = None

	return p_module, p_assessment_id, p_input_file, p_module_args


with open(header_file, 'r') as header_stream:
	print(header_stream.read())

with open(config, 'r') as config_stream:
	config_variables = yaml.load(config_stream, Loader=yaml.BaseLoader)

module, assessment_id, input_file, module_args = parse_args(config_variables['Modules'])

possible_log_levels = ['DEBUG', 'INFO', 'ERROR', 'CRITICAL', 'WARNING']
if config_variables['Log_Level'] not in possible_log_levels:
	print('Unknown log level in config. Please enter one of the following:\n\t{}'.format('\n\t'.join(possible_log_levels)))
	sys.exit()

ModuleSwitcher().module_switcher(module, module_args, assessment_id, input_file)
