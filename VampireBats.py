"""
Vampire bats, (Desmodus rotundus), are extremely sociable animals which tend to live in colonies in dark places, 
such as caves, old wells, hollow trees, and buildings.

The program loops thru all groups and in which picks up members from to add as friends.
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


############################################
# Main Code
############################################
bot = Bot(None,2,None,None,None,None)
##CONFIGURATION
groups=bot.groups(True,False)
logger.info(str(len(groups)) + " groups found. Looping thru them...")
for group in groups:
	logger.info("Processing group " + group.name + " ... ")
	friends=group.search()
	for friend in friends:
		bot.add_friend(friend,"马尼拉中国小吃外卖")
		logger.info("Sleeping for 30 mins before adding next friend ...")
		##time.sleep(60*30)
		time.sleep(5)

