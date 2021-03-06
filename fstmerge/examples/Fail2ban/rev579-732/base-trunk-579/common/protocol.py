__author__ = "Cyril Jaquier"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2010-07-25 12:46:55 $"
__copyright__ = "Copyright (c) 2004 Cyril Jaquier"
__license__ = "GPL"
import textwrap
protocol = [
['', "BASIC", ""],
["start", "starts the server and the jails"], 
["reload", "reloads the configuration"], 
["stop", "stops all jails and terminate the server"], 
["status", "gets the current status of the server"], 
["ping", "tests if the server is alive"], 
['', "LOGGING", ""],
["set loglevel <LEVEL>", "sets logging level to <LEVEL>. 0 is minimal, 4 is debug"], 
["get loglevel", "gets the logging level"], 
["set logtarget <TARGET>", "sets logging target to <TARGET>. Can be STDOUT, STDERR, SYSLOG or a file"], 
["get logtarget", "gets logging target"], 
['', "JAIL CONTROL", ""],
["add <JAIL> <BACKEND>", "creates <JAIL> using <BACKEND>"], 
["start <JAIL>", "starts the jail <JAIL>"], 
["stop <JAIL>", "stops the jail <JAIL>. The jail is removed"], 
["status <JAIL>", "gets the current status of <JAIL>"],
['', "JAIL CONFIGURATION", ""],
["set <JAIL> idle on|off", "sets the idle state of <JAIL>"], 
["set <JAIL> addignoreip <IP>", "adds <IP> to the ignore list of <JAIL>"], 
["set <JAIL> delignoreip <IP>", "removes <IP> from the ignore list of <JAIL>"], 
["set <JAIL> addlogpath <FILE>", "adds <FILE> to the monitoring list of <JAIL>"], 
["set <JAIL> dellogpath <FILE>", "removes <FILE> to the monitoring list of <JAIL>"], 
["set <JAIL> timeregex <REGEX>", "sets the regular expression <REGEX> to match the date format for <JAIL>. This will disable the autodetection feature."], 
["set <JAIL> timepattern <PATTERN>", "sets the pattern <PATTERN> to match the date format for <JAIL>. This will disable the autodetection feature."], 
["set <JAIL> addfailregex <REGEX>", "adds the regular expression <REGEX> which must match failures for <JAIL>"], 
["set <JAIL> delfailregex <INDEX>", "removes the regular expression at <INDEX> for failregex"], 
["set <JAIL> addignoreregex <REGEX>", "adds the regular expression <REGEX> which should match pattern to exclude for <JAIL>"],
["set <JAIL> delignoreregex <INDEX>", "removes the regular expression at <INDEX> for ignoreregex"], 
["set <JAIL> findtime <TIME>", "sets the number of seconds <TIME> for which the filter will look back for <JAIL>"], 
["set <JAIL> bantime <TIME>", "sets the number of seconds <TIME> a host will be banned for <JAIL>"], 
["set <JAIL> maxretry <RETRY>", "sets the number of failures <RETRY> before banning the host for <JAIL>"], 
["set <JAIL> addaction <ACT>", "adds a new action named <NAME> for <JAIL>"], 
["set <JAIL> delaction <ACT>", "removes the action <NAME> from <JAIL>"], 
["set <JAIL> setcinfo <ACT> <KEY> <VALUE>", "sets <VALUE> for <KEY> of the action <NAME> for <JAIL>"], 
["set <JAIL> delcinfo <ACT> <KEY>", "removes <KEY> for the action <NAME> for <JAIL>"], 
["set <JAIL> actionstart <ACT> <CMD>", "sets the start command <CMD> of the action <ACT> for <JAIL>"], 
["set <JAIL> actionstop <ACT> <CMD>", "sets the stop command <CMD> of the action <ACT> for <JAIL>"], 
["set <JAIL> actioncheck <ACT> <CMD>", "sets the check command <CMD> of the action <ACT> for <JAIL>"], 
["set <JAIL> actionban <ACT> <CMD>", "sets the ban command <CMD> of the action <ACT> for <JAIL>"],
["set <JAIL> actionunban <ACT> <CMD>", "sets the unban command <CMD> of the action <ACT> for <JAIL>"], 
['', "JAIL INFORMATION", ""],
["get <JAIL> logpath", "gets the list of the monitored files for <JAIL>"],
["get <JAIL> ignoreip", "gets the list of ignored IP addresses for <JAIL>"],
["get <JAIL> timeregex", "gets the regular expression used for the time detection for <JAIL>"],
["get <JAIL> timepattern", "gets the pattern used for the time detection for <JAIL>"],
["get <JAIL> failregex", "gets the list of regular expressions which matches the failures for <JAIL>"],
["get <JAIL> ignoreregex", "gets the list of regular expressions which matches patterns to ignore for <JAIL>"],
["get <JAIL> findtime", "gets the time for which the filter will look back for failures for <JAIL>"],
["get <JAIL> bantime", "gets the time a host is banned for <JAIL>"],
["get <JAIL> maxretry", "gets the number of failures allowed for <JAIL>"],
["get <JAIL> addaction", "gets the last action which has been added for <JAIL>"],
["get <JAIL> actionstart <ACT>", "gets the start command for the action <ACT> for <JAIL>"],
["get <JAIL> actionstop <ACT>", "gets the stop command for the action <ACT> for <JAIL>"],
["get <JAIL> actioncheck <ACT>", "gets the check command for the action <ACT> for <JAIL>"],
["get <JAIL> actionban <ACT>", "gets the ban command for the action <ACT> for <JAIL>"],
["get <JAIL> actionunban <ACT>", "gets the unban command for the action <ACT> for <JAIL>"],
]
def printFormatted():
	INDENT=4
	MARGIN=41
	WIDTH=34
	firstHeading = False
	for m in protocol:
		if m[0] == '' and firstHeading:
			print
		firstHeading = True
		first = True
		for n in textwrap.wrap(m[1], WIDTH):
			if first:
				line = ' ' * INDENT + m[0] + ' ' * (MARGIN - len(m[0])) + n
				first = False
			else:
				line = ' ' * (INDENT + MARGIN) + n
			print line
def printWiki():
	firstHeading = False
	for m in protocol:
		if m[0] == '':
			if firstHeading:
				print "|}"
			__printWikiHeader(m[1], m[2])
			firstHeading = True
		else:
			print "|-"
			print "| <span style=\"white-space:nowrap;\"><tt>" + m[0] + "</tt></span> || || " + m[1]
	print "|}"
def __printWikiHeader(section, desc):
	print
	print "=== " + section + " ==="
	print
	print desc
	print
	print "{|"
	print "| '''Command''' || || '''Description'''"
