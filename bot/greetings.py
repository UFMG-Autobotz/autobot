#!/usr/bin/env python
#coding: utf-8

import os, time
from slackclient import SlackClient

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

def main():
	# instantiate Slack & Twilio clients
	slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

	GREETINGS_MSG = '''Olá!

Sou o Autobot (sim, trocadilho ruim, culpe o criador, ninguém escolhe o próprio nome) e, de agora em diante, passarei a culidar do timesheet da equipe.

Para falar comigo, mande uma mensagem me marcando (ex: _@autobot comando_). Lembre-se de me marcar, ou vai ficar falando sozinho kkkkkk.

Sempre que eu não entender um comando (o que pode acontecer com frequência), vou enviar uma mensagem explicando o que posso fazer, então basta escrever _@autobot oi_ para começarmos.

Não creio que seja necessário, mas dê preferência em conversar no privado. Ninguém precisa ficar recebendo nossas mensagens. Nossas conversas privadas ficam no canto esquerdo inferior, em *APPS*. Caso eu não esteja aparecendo, clique no sinal de *+* e me adicione.

Ainda estou em fase de testes, então podem haver problemas (tipo eu parar de funcionar ou tentar dominar o mundo). Caso haja problemas, fale com o criador (o cara legal de barba) e ele vai te ajudar assim que possível.

Espero que eu possa ser muito útil para o dia a dia da equipe!'''
	greetings_channel = 'C5AFCH0KD'

	if slack_client.rtm_connect():
		print "StarterBot connected!"
		slack_client.api_call("chat.postMessage", channel=greetings_channel, text=GREETINGS_MSG, as_user=True)
		time.sleep(1)

	else:
		print "Connection failed. Invalid Slack token or bot ID?"

if __name__ == "__main__":
	main()
