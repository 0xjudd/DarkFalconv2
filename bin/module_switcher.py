from modules.IA_Main import AssessmentCreationOrUpdate
from modules.IA_StatusChecker import StatusChecker
from modules.IA_Update import UpdateScenarioList
from modules.IA_Scenarios import Scenarios
from modules.IA_Detection import DetectionResults

import sys


class ModuleSwitcher:

	def module_switcher(self, module_name, module_args, assessment_id, input_file):
		print('\n\tModule: {}\n\tAssessment ID: {}\n\tInput File: {}\n\tAdditional Arguments: {}\n\t'.format(module_name, assessment_id, input_file, module_args))
		if module_name == 'Main':
			if module_args == 'create':
				if not input_file:
					print('Please enter a file path with the \'-f\' switch.')
					sys.exit()
				else:
					arg_return = AssessmentCreationOrUpdate().new_assessment(input_file)
			elif module_args == 'update':
				if not input_file:
					print('Please enter a file path with the \'-f\' switch.')
					sys.exit()
				else:
					arg_return = AssessmentCreationOrUpdate().update_assessment(input_file)
			else:
				print('Unknown module argument. Please use \'create\' or \'update\'.')
		elif module_name == 'Status':
			arg_return = StatusChecker().main(assessment_id, module_args)
		elif module_name == 'Update':
			arg_return = UpdateScenarioList().main()
		elif module_name == 'Scenarios':
			arg_return = Scenarios().main()
		elif module_name == 'Detection':
			arg_return = DetectionResults().main(assessment_id)
