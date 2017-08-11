#!/usr/bin/env python
#coding: utf-8

import os, time, yaml, datetime, requests, sys
from general_utils import get_yaml_dict
sys.path.append('./report')
from latex_parser import generate_report
from slackclient import SlackClient
from git import Repo
from socket import error as SocketError

user_dict = {
	'U5ALA8Y4V': 'admin',
	'U6B1LBESW': 'autobot',
	'U5C35ENUU': 'barbara-almeida',
	'U5C2MA4V7': 'bhryan',
	'U5C6TJRCM': 'biancamartins',
	'U5CKKKS8N': 'bruno-cerqueira',
	'U5AHMQ734': 'daniel-leite',
	'U5C2TF8H2': 'daniel.gsousa',
	'U5CE810DQ': 'elisa-bacelar',
	'U5H8PREPM': 'guiraffo',
	'U69E97XBN': 'howdy',
	'U5BU98WSX': 'italo-lelis',
	'U5BJ1HAGH': 'jonatan',
	'U5ACF9X5W': 'josuehfa',
	'U5BUL6TV0': 'mariacristinafonteboa',
	'U5CQJQNAZ': 'marimeireles',
	'U5F0U5JG7': 'nataliapaixao',
	'U5BUYMQMR': 'pedro',
	'U5DQHR6JF': 'polly',
	'U5CFCV03U': 'rafaelsa97',
	'U5C8D57CK': 'renan.cvr',
	'U5D94M6FQ': 'rodrigo-cezar',
	'U5CKFJMF0': 'thiago-lages',
	'U5CKUEBRD': 'victor-castro',
	'U5BNQ6F32': 'virginia-satyro',
	'USLACKBOT': 'slackbot',

	'C59TD6V3J': 'eletrônica',
	'C5N4TBULS': 'fotos',
	'C5AFCH0KD': 'general',
	'C5AHM785Q': 'gestão',
	'C5AFGG4R1': 'mecânica',
	'C5AK25KU4': 'navegação',
	'C5AHHA5MY': 'random'
}

COMMAND = var = lambda: None

COMMAND.TIMESHEET = "timesheet"
COMMAND.ADD = "add"
COMMAND.ADD_PLAN = "add_plan"
COMMAND.COMMENT = "comment"
COMMAND.DELETE = "delete"
COMMAND.EDIT = "edit"
COMMAND.GET = "get"
COMMAND.HELP = "help"
COMMAND.VIEW = "view"

HELP = {
	COMMAND.ADD: '*'+ COMMAND.ADD +'*: adiciona uma atividade ao timesheet. EX -> *timesheet add* _Tempo em horas_ : _Descrição_\n',
	COMMAND.ADD_PLAN: '*'+ COMMAND.ADD_PLAN +'*: adiciona uma atividade planejada para a semana seguinte. EX ->  *timesheet add_plan* _Descrição_\n',
	COMMAND.COMMENT: '*'+ COMMAND.COMMENT +'*: Inclui um comentário para o relatório. Atualmente, apenas um comentário por relatório semanal é arquivado, de modo que a adição de um novo comentário exclui o antigo. EX ->  *timesheet comment* _Comentário_\n',
	COMMAND.DELETE: '*'+ COMMAND.DELETE +'*: remove uma atividade ao timesheet, de acordo com a numeração do comando view. EX-> *timesheet delete* _ID_\n',
	COMMAND.EDIT: '*'+ COMMAND.EDIT +'*: edita a quantidade de horas de uma atividade no timesheet, de acordo com a numeração do comando view. EX-> *timesheet edit* _ID_ : _Tempo em horas_\n',
	COMMAND.GET: '*'+ COMMAND.GET +'*: compila e posta uma versão parcial do relatório da semana. Pode levar alguns segundos, uma vez que é necessário recompilar o .tex para gerar o relatório. EX ->  *timesheet get*\n',
	COMMAND.VIEW: '*'+ COMMAND.VIEW +'*: lista as atividades e comentário já registrados na semana. EX ->  *timesheet view*\n'
}

PATH = './timesheet/'
TIMESHEET_PREFIX = PATH+'timesheet_'
TIMESHEET_FILE = PATH+'timesheet.yaml'

ATIVIDADES = 'atividades'
COMMENTS = 'comments'
PLANOS = 'planos'

HELP_RESPONSE = 'Atualmente, eu sou apenas capaz de organizar o timesheet. Os seguintes comandos estão atualmente disponíveis:\n'
for key in sorted(HELP.keys()):
	HELP_RESPONSE += HELP[key]+'\n'

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def check_time():
	data = datetime.datetime.now()
	semana_atual = data.isocalendar()[1]
	return data, semana_atual

def check_timesheet():
	data = datetime.datetime.now()
	semana_atual = data.isocalendar()[1]
	global TIMESHEET_FILE
	new_TIMESHEET_FILE = TIMESHEET_PREFIX + str(semana_atual) + '.yaml'
	if not os.path.isfile(new_TIMESHEET_FILE):
		os.system("cp "+TIMESHEET_FILE+" "+new_TIMESHEET_FILE)
		time.sleep(1)
	TIMESHEET_FILE = new_TIMESHEET_FILE

def upload_file(filepath, channels, filename=None, content=None, title=None, initial_comment=None):
	"""Upload file to channel

	Note:
		URLs can be constructed from:
		https://api.slack.com/methods/files.upload/test
	"""

	if filename is None:
		filename = os.path.basename(filepath)

	data = {}
	data['token'] = os.environ.get('SLACK_BOT_TOKEN')
	data['file'] = filepath
	data['filename'] = filename
	data['channels'] = channels

	if content is not None:
		data['content'] = content

	if title is not None:
		data['title'] = title

	if initial_comment is not None:
		data['initial_comment'] = initial_comment

	# filepath = data['file']
	files = { 'file': (filepath, open(filepath, 'rb'), '', { 'Expires': '0' }) }
	data['media'] = files
	response = requests.post(url='https://slack.com/api/files.upload', data=data, headers={'Accept': 'application/json'}, files=files)

	return response.text

def post_report(filepath, channels, title='Relatório semanal', com=None):
	# print upload_file(filepath=filepath, channels=channels, title=title, initial_comment=com)
	upload_file(filepath=filepath, channels=channels, title=title, initial_comment=com)

def handle_command(command, channel, user):
	"""
	    Receives commands directed at the bot and determines if they
	    are valid commands. If so, then acts on the commands. If not,
	    returns back what it needs for clarification.
	"""
	timesheet_dict = get_yaml_dict(TIMESHEET_FILE)
	user_list = timesheet_dict.keys()
	response = "Não entendi o que quis dizer.\n" + HELP_RESPONSE
	response_sent = False
	# print channel, command, user

	erro = False

	if user.upper() in user_dict.keys():
		user_name = user_dict[user.upper()]

	if command.lower().startswith(COMMAND.HELP):
		response = HELP_RESPONSE

	elif command.lower().startswith(COMMAND.TIMESHEET):
		command = command[len(COMMAND.TIMESHEET):].strip()

		try:

			if command.lower().startswith(COMMAND.ADD_PLAN):
				command = command[len(COMMAND.ADD_PLAN):].strip()

				plan = command
				if user_name in user_list:
					timesheet_dict[user_name][PLANOS].append(plan)
					response = 'Sua atividade foi registrada, parabéns por se planejar com antecedência!'
				else:
					response = 'O nome de usuário fornecido não foi reconhecido.'

			elif command.lower().startswith(COMMAND.ADD):
				command = command[len(COMMAND.ADD):].strip()
				
				try:
					hrs = float(command.split(':')[0].strip().replace(',','.'))
				except:
					erro = True
					response = 'Número inválido de horas.'

				command = command.split(':')[1].strip()

				description =  command
				# description =  command.split('-')[0].strip()
				# comment = None
				# if len(command.split('-')) > 1:
				# 	comment = command.split('-')[1].strip()

				if not erro:
					if user_name in user_list:
						timesheet_dict[user_name][ATIVIDADES].append([hrs, description])
						# timesheet_dict[user_name].append([hrs, description, comment])
						response = 'Sua atividade foi registrada, continue o bom trabalho!'
					else:
						response = 'O nome de usuário fornecido não foi reconhecido.'

			elif command.lower().startswith(COMMAND.DELETE):
				command = command[len(COMMAND.DELETE):].strip()

				try:
					ID = int(command)
				except:
					erro = True
					response = 'ID inválido!'

				if not erro:
					if user_name in user_list:
						try:
							if ID <= len(timesheet_dict[user_name][ATIVIDADES]):
								del timesheet_dict[user_name][ATIVIDADES][ID-1]
								response = 'A atividade '+ str(ID) +' foi deletada!'
							elif ID <= len(timesheet_dict[user_name][ATIVIDADES]) + len(timesheet_dict[user_name][PLANOS]):
								del timesheet_dict[user_name][PLANOS][ID-1-len(timesheet_dict[user_name][ATIVIDADES])]
								response = 'A atividade '+ str(ID) +' foi deletada!'
							elif ID == len(timesheet_dict[user_name][ATIVIDADES]) + len(timesheet_dict[user_name][PLANOS]) + 1:
								if timesheet_dict[user_name][COMMENTS]:
									timesheet_dict[user_name][COMMENTS] = ''
									response = 'A atividade '+ str(ID) +' foi deletada!'
								else:
									response = 'ID não encontrado.'
							else:
								response = 'ID não encontrado.'
						except:
							erro = True
							response = 'ID não encontrado.'
					else:
						response = 'O nome de usuário fornecido não foi reconhecido.'
				

			elif command.lower().startswith(COMMAND.VIEW):

				if user_name in user_list:
					ativ_list = timesheet_dict[user_name][ATIVIDADES]
					plan_list = timesheet_dict[user_name][PLANOS]
					com = timesheet_dict[user_name][COMMENTS]
					response = '*Atividades da semana*\n\n'

					for k, ativ in enumerate(ativ_list):
						response+=str(k+1)+') '+str(ativ[0])+' hrs: '+ativ[1]+'\n\n'

					response+='\n*Atividades planejadas*\n\n'
					for k, plan in enumerate(plan_list):
						response+=str(k+len(ativ_list)+1)+') '+plan+'\n\n'

					response+='\n*Comentario*\n\n'
					if timesheet_dict[user_name][COMMENTS]:
						response+=str(len(ativ_list)+len(plan_list)+1)+') '+com+'\n\n'

				else:
					response = 'O nome de usuário fornecido não foi reconhecido.'

			elif command.lower().startswith(COMMAND.COMMENT):
				command = command[len(COMMAND.COMMENT):].strip()

				com = command
				if user_name in user_list:
					timesheet_dict[user_name][COMMENTS] = com
					response = 'Seu comentário foi registrado!'
				else:
					response = 'O nome de usuário fornecido não foi reconhecido.'

			elif command.lower().startswith(COMMAND.GET):
				pdf_file = generate_report()
				data, semana_atual = check_time()
				post_report(pdf_file, channel, title='Relatório semana '+str(semana_atual), com=None)
				response_sent = True

			elif command.lower().startswith(COMMAND.EDIT):
				command = command[len(COMMAND.EDIT):].strip()
				
				try:
					ID = int(command.split(':')[0].strip())
				except:
					erro = True
					response = 'ID inválido!'

				command = command.split(':')[1].strip()

				try:
					hrs = float(command.replace(',','.'))
				except:
					erro = True
					response = 'Número inválido de horas.'

				if not erro:
					if user_name in user_list:
						try:
							timesheet_dict[user_name][ATIVIDADES][ID-1][0] = hrs
							response = 'A atividade '+ str(ID) +' foi editada!'
						except:
							erro = True
							response = 'ID não encontrado.'
					else:
						response = 'O nome de usuário fornecido não foi reconhecido.'

		except:
			pass
	with open(TIMESHEET_FILE, 'w') as f:
		yaml.dump(timesheet_dict, f)
		f.close()
	if not response_sent:
		slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
	"""
	    The Slack Real Time Messaging API is an events firehose.
	    this parsing function returns None unless a message is
	    directed at the Bot, based on its ID.
	"""

	# bot's ID as an environment variable
	BOT_ID = os.environ.get("BOT_ID")
	AT_BOT = "<@" + BOT_ID + ">"

	output_list = slack_rtm_output
	if output_list and len(output_list) > 0:
		for output in output_list:
			if output and 'text' in output and AT_BOT in output['text']:
				# return text after the @ mention, whitespace removed
				return output['text'].split(AT_BOT)[1].strip(), output['channel'], output['user']
	return None, None, None

def main():
	# # print os.getcwd()
	# # exit()
	init_time = check_time()
	time_1 = check_time()

	WATCHED_SRC_FILES = ['bot/autobot.py', 'bot/general_utils.py', 'report/latex_parser.py']
	WATCHED_SRC_FILES_MTIMES = [(f, os.path.getmtime(f)) for f in WATCHED_SRC_FILES]

	WATCHED_DATA_FILES = ['report/dados/datas.tex', 'report/dados/membros.tex', TIMESHEET_FILE, TIMESHEET_FILE.replace()]
	WATCHED_DATA_FILES_MTIMES = [(f, os.path.getmtime(f)) for f in WATCHED_DATA_FILES]

	rep = Repo('.')
	weekly_post = False
	POST_CHANNEL = 'C6J00MNH2' #relatórios
	PULL_time = 60

	READ_WEBSOCKET_DELAY = 1.5 # 1 second delay between reading from firehose
	socket_err_cnt = 0
	sucess_cnt = 0
	if slack_client.rtm_connect():
		print "StarterBot connected and running!"
		while True:
			check_timesheet()
			current_time = check_time()

			if weekly_post and current_time[1] != init_time[1]:
				pdf_file = generate_report(init_time[1])
				post_report(pdf_file, POST_CHANNEL, title='Relatório semana '+str(init_time[1]), com=None)
				init_time = check_time()

			time_diff = current_time[0] - time_1[0]
			if time_diff.total_seconds() > PULL_time:
				time_1 = check_time()
				rep.git.fetch()
				commits_behind = rep.iter_commits('master..origin/master')
				count_behind = sum(1 for c in commits_behind)

				uncommited_changes = 0
				for f, mtime in WATCHED_DATA_FILES_MTIMES:
					if os.path.getmtime(f) != mtime:
						rep.git.add(f)
						uncommited_changes +=1

				WATCHED_DATA_FILES_MTIMES = [(f, os.path.getmtime(f)) for f in WATCHED_DATA_FILES]

				if uncommited_changes > 0:
					rep.git.commit(m='bot_update')

				if count_behind > 0 or uncommited_changes > 0:

					rep.git.pull()

					if uncommited_changes > 0:
						rep.git.push()

					# Check whether a watched file has changed.
					for f, mtime in WATCHED_SRC_FILES_MTIMES:
						if os.path.getmtime(f) != mtime:
							# One of the files has changed, so restart the script.
							# When running the script via './script.py', use
							# os.execv(__file__, sys.argv)
							# When running the script via 'python script.py', use
							os.execv(sys.executable, ['python'] + sys.argv)
			try:
				command, channel, user = parse_slack_output(slack_client.rtm_read())
				if command and channel:
					handle_command(command, channel, user)
				sucess_cnt+=1

			except SocketError, err_text:
				socket_err_cnt+=1

				if socket_err_cnt == 1:
					print err_text

				if socket_err_cnt == 30:
					print '30'
					exit()

			time.sleep(READ_WEBSOCKET_DELAY)
	else:
		print "Connection failed. Invalid Slack token or bot ID?"

if __name__ == "__main__":
	main()