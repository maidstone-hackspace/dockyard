import commands

BROWSERS = (
    'firefox',
    'chrome'
)


def get_firefox():
    return commands.getstatusoutput('which firefox')[-1]

def get_chrome():
    return commands.getstatusoutput('which google-chrome')[-1]

def return_browsers():
    for browser in BROWSERS:
        code, path = commands.getstatusoutput('which %s' % browser)
        if code is 0:
            yield browser, path
