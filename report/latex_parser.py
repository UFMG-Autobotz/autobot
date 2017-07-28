#!/usr/bin/env python
#coding: utf-8

import datetime, os, yaml, io, time
from general_utils import get_yaml_dict, set_new_var

def get_comment(com):
	return com.replace('\n', '\\par ')

def get_planos(plan):
	planos_string = '\\item #PLANO'
	r_plan = ""
	if len(plan) >=1:
		for p in plan:
			r_plan+=planos_string.replace('#PLANO', p.replace('\n','\\newline ') )+'\n'
	return r_plan[:-1]

def get_tarefas(ativ):
	tarefas_string = '\\hline #TAREFA & #HORA \\\\'
	horas_totais = 0
	tar = ""
	if len(ativ) >=1:
		for a in ativ:
			tar+=tarefas_string.replace('#TAREFA', a[1].replace('\n','\\newline ') ).replace('#HORA', str(a[0]))+'\n'
			horas_totais+=a[0]
		tar = tar[:-1]
	tar+='}{'+str(horas_totais)
	return tar

def get_nome(nome):
	return nome

def get_membro(info):
	membro_string = u'''\\begin{membro}
\\nome{#NOME}
\\tarefas{#TAREFAS}
\\planos{#PLANOS}
\\comentarios{#COMMENT}
\\end{membro}\n\n'''
	membro_string = membro_string.replace('#NOME', get_nome(info.nome) )
	membro_string = membro_string.replace('#TAREFAS', get_tarefas(info.atividades) )
	membro_string = membro_string.replace('#PLANOS', get_planos(info.planos) )
	membro_string = membro_string.replace('#COMMENT', get_comment(info.comments) )
	return membro_string

def get_date():
	meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
	data = datetime.datetime.now()
	semana_atual = data.isocalendar()[1]
	semana_init = data-datetime.timedelta(days=data.isocalendar()[2]-1)
	semana_end = data+datetime.timedelta(days=7-data.isocalendar()[2])

	data = [data.day, data.month, data.year]
	semana_init = [semana_init.day, semana_init.month, semana_init.year]
	semana_end = [semana_end.day, semana_end.month, semana_end.year]

	date_string = '\\def \\semana {'+str(semana_atual)+'}\n'

	if semana_init[2] != semana_end[2]:
		date_string +='\\def \\dataInicio {'+str(semana_init[0])+' de '+meses[semana_init[1]]+' de '+str(semana_init[2])+'}'
	elif semana_init[1] != semana_end[1]:
		date_string +='\\def \\dataInicio {'+str(semana_init[0])+' de '+meses[semana_init[1]]+'}'
	else:
		date_string +='\\def \\dataInicio {'+str(semana_init[0])+'}'
	date_string +='\n\\def \\dataFim {'+str(semana_end[0])+' de '+meses[semana_end[1]]+' de '+str(semana_end[2])+'}'

	# print data
	# print semana_atual
	# print semana_init
	# print semana_end

	return date_string, semana_atual

def generate_report():
	PATH = './timesheet/'
	# WEEKS = 1

	date_string, semana_atual = get_date()

	TIMESHEET_PREFIX = 'timesheet_'

	TIMESHEET_FILE = PATH + TIMESHEET_PREFIX + str(semana_atual) + '.yaml'
	# print 'retrieving info from: ' + TIMESHEET_FILE
	timesheet_dict = get_yaml_dict(TIMESHEET_FILE)

	# print date_string
	# print '\n'*3

	with open("report/dados/datas.tex", "w") as file:
		file.write(date_string)

	with io.open("report/dados/membros.tex", "w", encoding='utf8') as file:
		for key in sorted(timesheet_dict.keys()):
			membro_string = get_membro( set_new_var( timesheet_dict[key] ) )
			# print membro_string
			# print ''
			file.write(membro_string)

	os.system("cp report/timesheet.tex report/timesheet_"+str(semana_atual)+".tex")
	os.system("pdflatex -interaction=nonstopmode report/timesheet_"+str(semana_atual)+".tex")
	time.sleep(1)
	os.system("rm report/timesheet_"+str(semana_atual)+".tex")
	os.system("rm timesheet_"+str(semana_atual)+".aux")
	os.system("rm timesheet_"+str(semana_atual)+".log")
	os.system("mv timesheet_"+str(semana_atual)+".pdf "+PATH)

	return PATH+"timesheet_"+str(semana_atual)+".pdf"

def main():
	print generate_report()

if __name__  == "__main__":
	main()