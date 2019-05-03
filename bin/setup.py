from crypto_setup import CryptoSetup
import subprocess
import sys
import os

print('[*] Starting setup of InfernoAuger...\n')
print('[*] Checking version of Python running this setup...')

if sys.version_info.major >= 3 and sys.version_info.minor >= 7:
	print('[*] Running version of Python greater than 3.7')
else:
	print('[*] Script must be run with a version of Python 3.7+')
	sys.exit()

print('\n[*] Installing pre-requisite packages...')
reqs = os.path.normpath('../requirements.txt')
subprocess.call([sys.executable, "-m", "pip", "--trusted-host", "pypi.org", "--trusted-host", "pypi.python.org", "--trusted-host", "files.pythonhosted.org", "install", "-r", reqs])

print('\n[*] Starting encryption setup...')
CryptoSetup().main()
