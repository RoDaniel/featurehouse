__author__ = "Cyril Jaquier"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2010-07-25 12:47:01 $"
__copyright__ = "Copyright (c) 2004 Cyril Jaquier"
__license__ = "GPL"
from server.jails import UnknownJailException
from server.jails import DuplicateJailException
import logging
logSys = logging.getLogger("fail2ban.client.config")
class Beautifier:
	
	def __init__(self, cmd = None):
		self.__inputCmd = cmd
	def setInputCmd(self, cmd):
		self.__inputCmd = cmd
		
	def getInputCmd(self):
		return self.__inputCmd
		
	def beautify(self, response):
		logSys.debug("Beautify " + `response` + " with " + `self.__inputCmd`)
		inC = self.__inputCmd
		msg = response
		try:
			if inC[0] == "ping":
				msg = "Server replied: " + response
			elif inC[0] == "start":
				msg = "Jail started"
			elif inC[0] == "stop":
				if len(inC) == 1:
					if response == None:
						msg = "Shutdown successful"
				else:
					if response == None:
						msg = "Jail stopped"
			elif inC[0] == "add":
				msg = "Added jail " + response
			elif inC[0:1] == ['status']:
				if len(inC) > 1:
					
					ipList = ""
					for ip in response[1][1][2][1]:
						ipList += ip + " "
					
					fileList = ""
					for f in response[0][1][2][1]:
						fileList += f + " "
					
					msg = "Status for the jail: " + inC[1] + "\n"
					msg = msg + "|- " + response[0][0] + "\n"
					msg = msg + "|  |- " + response[0][1][2][0] + ":\t" + fileList + "\n"
					msg = msg + "|  |- " + response[0][1][0][0] + ":\t" + `response[0][1][0][1]` + "\n"
					msg = msg + "|  `- " + response[0][1][1][0] + ":\t" + `response[0][1][1][1]` + "\n"
					msg = msg + "`- " + response[1][0] + "\n"
					msg = msg + "   |- " + response[1][1][0][0] + ":\t" + `response[1][1][0][1]` + "\n"
					msg = msg + "   |  `- " + response[1][1][2][0] + ":\t" + ipList + "\n"
					msg = msg + "   `- " + response[1][1][1][0] + ":\t" + `response[1][1][1][1]`
				else:
					msg = "Status\n"
					msg = msg + "|- " + response[0][0] + ":\t" + `response[0][1]` + "\n"
					msg = msg + "`- " + response[1][0] + ":\t\t" + response[1][1]
			elif inC[1] == "logtarget":
				msg = "Current logging target is:\n"
				msg = msg + "`- " + response
			elif inC[1:2] == ['loglevel']:
				msg = "Current logging level is "
				if response == 1:
					msg = msg + "ERROR"
				elif response == 2:
					msg = msg + "WARN"
				elif response == 3:
					msg = msg + "INFO"
				elif response == 4:
					msg = msg + "DEBUG"
				else:
					msg = msg + `response`
			elif inC[2] in ("logpath", "addlogpath", "dellogpath"):
				if len(response) == 0:
					msg = "No file is currently monitored"
				else:
					msg = "Current monitored log file(s):\n"
					for path in response[:-1]:
						msg = msg + "|- " + path + "\n"
					msg = msg + "`- " + response[len(response)-1]
			elif inC[2] in ("ignoreip", "addignoreip", "delignoreip"):
				if len(response) == 0:
					msg = "No IP address/network is ignored"
				else:
					msg = "These IP addresses/networks are ignored:\n"
					for ip in response[:-1]:
						msg = msg + "|- " + ip + "\n"
					msg = msg + "`- " + response[len(response)-1]
			elif inC[2] in ("failregex", "addfailregex", "delfailregex",
							"ignoreregex", "addignoreregex", "delignoreregex"):
				if len(response) == 0:
					msg = "No regular expression is defined"
				else:
					msg = "The following regular expression are defined:\n"
					c = 0
					for ip in response[:-1]:
						msg = msg + "|- [" + str(c) + "]: " + ip + "\n"
						c += 1
					msg = msg + "`- [" + str(c) + "]: " + response[len(response)-1]
		except Exception:
			logSys.warn("Beautifier error. Please report the error")
			logSys.error("Beautify " + `response` + " with " + `self.__inputCmd` +
						 " failed")
			msg = msg + `response`
		return msg
	def beautifyError(self, response):
		logSys.debug("Beautify (error) " + `response` + " with " + `self.__inputCmd`)
		msg = response
		if isinstance(response, UnknownJailException):
			msg = "Sorry but the jail '" + response[0] + "' does not exist"
		elif isinstance(response, IndexError):
			msg = "Sorry but the command is invalid"
		elif isinstance(response, DuplicateJailException):
			msg = "The jail '" + response[0] + "' already exists"
		return msg
