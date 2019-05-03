from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import getpass
import os

class CryptoSetup:
	def generate_keys(self):
		print('\n[*] Generating encryption public/private key pair...')
		key = RSA.generate(4096)
		encrypted_key = key.export_key(pkcs=8, protection='scryptAndAES128-CBC')
		priv_key_loc = os.path.normpath('../etc/priv_key.pem')
		pub_key_loc = os.path.normpath('../etc/pub_key.pem')
		with open(priv_key_loc, 'wb') as priv_key_out:
			priv_key_out.write(encrypted_key)
		with open(pub_key_loc, 'wb') as pub_key_out:
			pub_key_out.write(key.publickey().export_key())
		print('\n[*] Public and private key pair generated. NOTE: PLEASE MOVE THE PRIVATE KEY TO A SECURE LOCATION AFTER SETUP!')

	def encrypt_password(self):
		password = getpass.getpass('\nPlease enter the password to encrypt: ')
		password_encoded = str.encode(password)
		external_key = os.path.normpath('../etc/pub_key.pem')
		key = RSA.importKey(open(external_key).read())
		encryptor = PKCS1_OAEP.new(key)
		encrypted_data = encryptor.encrypt(password_encoded)
		encoded = base64.b64encode(encrypted_data)

		file = open(os.path.normpath('../etc/encrypted.txt'), 'wb')
		file.write(encoded)
		file.close()
		print('\n[*] Password has been encrypted and stored in file {}.'.format(os.path.normpath('../etc/encrypted.txt')))

	def main(self):
		self.generate_keys()
		encrypt_pwd = input('\nDo you want to encrypt a Splunk password? [y/n]: ')
		if encrypt_pwd[0] == 'y':
			self.encrypt_password()
		elif encrypt_pwd[0] == 'n':
			print('\n[*] If you want to encrypt a Splunk password at a later time (for use with the Detection module), please run bin/crypto_setup.py manually.')

if __name__ == '__main__':
	CryptoSetup().encrypt_password()