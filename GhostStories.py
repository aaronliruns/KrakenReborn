"""
Ghost Stories. Keep on telling ...

Depending on how tasks are configured, the program
 continously performing tasks like sending messages
 to wechat groups or individual friends.
"""

from wxpy import *
from datetime import datetime as dt
import threading
import time

####################
# LOGGING SETUP
####################
### Setting up logger
logger = logging.getLogger('GhostStories')
logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)


####################
# CONFIGURATIONS
####################
#SESSION_GAP stands for the maxium time duration before next message blasting session
#The message cache will be wiped off and repopulated when a new session starts
SESSION_GAP = 60 * 2
msgQLastUpdate = dt.strptime('1Jan1970', '%d%b%Y')


####################
# GLOBAL VARIABLES
####################
messageQ = {}
messageQ[TEXT]    = []
messageQ[PICTURE] = 0
bot = None
lastExorcist = None



############################################
# Main Code
############################################
class Scheduler:
    def __init__(self, startHour, stopHour, interval, tasks):
        self.startHour = startHour
        self.stopHour = stopHour
        self.interval = interval
        self.tasks = tasks
        logger.info("Scheduler being brought up ... #startHour=%d#stopHour=%d#interval=%d" % (self.startHour,self.stopHour,self.interval))
        time.sleep(1)

    def isGoodForGroup(self):
        if dt.now().hour in range(self.startHour, self.stopHour):
            return True
        else:
            return False

    def kickOffTasks(self):
        while True:
            if self.isGoodForGroup():  # start, stop are integers (eg: 6, 9)
                ## Executing passed in tasks
                logger.info("Waiting for " + str(self.interval) + " seconds before next task...")
                time.sleep(self.interval)  # Minimum interval between task executions
                self.tasks()
            else:
                time.sleep(10)  # The else clause is not necessary but would prevent the program to keep the CPU bu


def shouldStartNewSession(lastUpdate):
    global msgQLastUpdate
    diff = lastUpdate - msgQLastUpdate
    msgQLastUpdate = lastUpdate
    if diff.total_seconds() - SESSION_GAP >= 0:
        return True
    else:
        return False


def startBot():
    global bot
    bot = Bot(None,False,None,None,None,None)
    ##CONFIGURATION
    global lastExorcist
    lastExorcist= bot.friends().search('Last Exorcist')[0]

    @bot.register(lastExorcist, [TEXT, PICTURE])
    def auto_respond_admin(msg):
        global messageQ
        returnMsg = ""
        if shouldStartNewSession(dt.now()):
            messageQ[TEXT]    = []  # reset text queue
            messageQ[PICTURE] = 0
            returnMsg = "NEW_SESSION:"

        if msg.type == TEXT:
            logger.info("Message type = {} Message text= {}".format(msg.type, msg.text))
            ##Append the received message to the text queue
            messageQ[TEXT].append(msg.text)
            returnMsg = returnMsg + " | " + str(len(messageQ[TEXT])) + " message(s) in the queue."
            return returnMsg
        elif msg.type == PICTURE:
            picIndex = messageQ[PICTURE]
            picName  = str(picIndex) +'.jpg'
            msg.get_file(picName)
            messageQ[PICTURE] = messageQ[PICTURE] + 1
            returnMsg = returnMsg + " | " + str(messageQ[PICTURE]) + " picture(s) in the queue."
            return returnMsg
        else:
            return 'Message is not recognized.'

        bot.join()

# Spawning a thread to launch the wechat bot
#startBot()
thread = threading.Thread(target=startBot(), args=())
thread.daemon = True # Daemonize thread
thread.start()       # Start the execution


##########################
# TASK SETUP
##########################
def groupTask():
    logger.info("")
    excludedGroups = []
    feihua = bot.groups().search('菲华网')
    if len(feihua) > 0:
        excludedGroups.append(feihua[0])
    allGroups = bot.groups().search()
    for group in allGroups:
        if group not in excludedGroups:
            logger.info("Processing group " + group.name)
            for msg in messageQ[TEXT]:
                try:
                    group.send(msg)
                    time.sleep(2)
                except:
                    logger.exception("Failed to send a message")
                    raise

            for i in range(0,messageQ[PICTURE]):
                try:
                    group.send_image(str(i)+'.jpg')
                    time.sleep(2)
                except:
                    logger.exception("Failed to send a picture.")
                    raise
            time.sleep(20)


scheduler = Scheduler(0,23,60*50,groupTask)
scheduler.kickOffTasks()
