__author__ = 'DarkWeb'

'''
Starting point of the Darkweb Forums Mining
'''

from datetime import *
from Forums.BestCardingWorld.crawler_selenium import crawler as crawlerBestCardingWorld
from Forums.RespostasOcultas.crawler_selenium import crawler as crawlerRespostasOcultas
from Forums.Pitch.crawler_selenium import crawler as crawlerPitch


import configparser
import os
import subprocess


config = configparser.ConfigParser()
config.read('../../setup.ini')
CURRENT_DATE = str("%02d" % date.today().month) + str("%02d" % date.today().day) + str("%04d" % date.today().year)


# reads list of marketplaces manually inputted
def getForums():
    forums = []
    with open('forumsList.txt') as f:
        forums = f.readlines()
    return forums


# Creates needed directories for marketplace if doesn't exist
def createDirectory(forum):

    # Package should already be there, holding crawler and parser
    if forum == 'Reddits':
        pagesMainDir = '../' + forum
    else:
        # pagesMainDir = '../' + forum + "/HTML_Pages"
        pagesMainDir = os.path.join(config.get('Project', 'shared_folder'), "Forums/" + forum + "/HTML_Pages")

    if not os.path.isdir(pagesMainDir):
        os.makedirs(pagesMainDir)

    if forum == 'Reddits':
        createRedditsSubdirectories(pagesMainDir)
    else:
        createSubdirectories(pagesMainDir)


def createRedditsSubdirectories(pagesMainDir):

    with open('../Reddits/redditsList.txt', 'r') as f:
        reddits = f.readlines()

    for reddit in reddits:
        reddit = reddit.strip('\n')
        redditMainDir = pagesMainDir + '/' + reddit + '/HTML_Pages'
        if not os.path.isdir(redditMainDir):
            os.mkdir(redditMainDir)
        # Create inner time folders
        createSubdirectories(redditMainDir)


def createSubdirectories(pagesDir):

    currentDateDir = pagesDir + '/' + CURRENT_DATE
    if not os.path.isdir(currentDateDir):
        os.mkdir(currentDateDir)

    listingDir = currentDateDir + '/Listing'
    if not os.path.isdir(listingDir):
        os.mkdir(listingDir)

    listReadDir = listingDir + '/Read'
    if not os.path.isdir(listReadDir):
        os.mkdir(listReadDir)

    descriptionDir = currentDateDir + '/Description'
    if not os.path.isdir(descriptionDir):
        os.mkdir(descriptionDir)

    descReadDir = descriptionDir + '/Read'
    if not os.path.isdir(descReadDir):
        os.mkdir(descReadDir)


# Opens Tor Browser
def opentor():
    global pid
    print("Connecting Tor...")
    pro = subprocess.Popen(config.get('TOR', 'firefox_binary_path'))
    pid = pro.pid
    # time.sleep(7.5)
    input('Press ENTER when Tor is connected to continue')
    return


# main method
if __name__ == '__main__':

    opentor()

    # assignment from forumsList.txt
    forumsList = getForums()

    # get forum from forumsList
    for forum in forumsList:
        forum = forum.replace('\n','')

        print("\nCreating listing and description directories ... for " + forum)
        createDirectory(forum)
        # time.sleep(5)  # wait for directories to be created
        print("Directories created.")

        if forum == "BestCardingWorld":
            crawlerBestCardingWorld()
        elif forum == "RespostasOcultas":
            crawlerRespostasOcultas()
        elif forum == "Pitch":
            crawlerPitch()

    print("\nScraping process completed!")
