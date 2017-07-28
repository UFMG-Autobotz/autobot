# import datetime
# import time

# def check_time():
# 	data = datetime.datetime.now()
# 	semana_atual = data.isocalendar()[1]
# 	return data, semana_atual

# def main():
# 	init = check_time()
# 	a = check_time()
# 	while True:
# 		b = check_time()
# 		c = b[0]-a[0]
# 		if c.total_seconds() > 1:
# 			a = check_time()
# 			k = b[0]-init[0]
# 			print k.total_seconds()
# 			if k.total_seconds() > 15:
# 				break

# if __name__ == "__main__":
# 	main()

import os

def main():
	while True:
		os.system("bash run_autobot.sh")
		os.system("git pull")

if __name__ == "__main__":
	main()