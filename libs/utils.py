import commands

def get_firefox():
	return commands.getstatusoutput('which firefox')[-1]

def get_chrome():
    return commands.getstatusoutput('which google-chrome')[-1]