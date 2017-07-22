import os
from slackclient import SlackClient


slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

if __name__ == "__main__":
	api_call = slack_client.api_call("users.list")
	if api_call.get('ok'):
		# retrieve all users so we can find our bot
		users = api_call.get('members')
		for user in users:
			if 'name' in user:
				print user.get('name'), user.get('id')
	print '\n'*3
	api_call = slack_client.api_call("channels.list")
	if api_call.get('ok'):
		# retrieve all users so we can find our bot
		channels = api_call.get('channels')
		for channel in channels:
			if 'name' in channel:
				print channel.get('name'), channel.get('id')