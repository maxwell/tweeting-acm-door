import threading
import os
from BeautifulSoup import BeautifulStoneSoup

new_xml_exists = False
#Arbitrary initial value for since_id                                                        
since_id = "8711950820"
screen_name = ""
lock = threading.Lock()

def getNewMention(id):
    lock.acquire()
    id = str(id)
    message = "curl -u acmroom:bluepin7 http://twitter.com/statuses/mentions.xml?since_id=%s" % id
    response = os.popen(message)
    #print soup.prettify()
    soup = BeautifulStoneSoup(response)
    new_xml_exists = True
    try:
        screen_name = soup.find('screen_name').string
    except AttributeError as e:
        new_xml_exists = False
        print ("\n'screen_name' tag was not found in XML:")
        print ("%s" % soup)
        return None
    print "I am at findid"
    since_id = soup.find('id').string
    lock.release()

def initTwitterPolling():
#Initially we request 1 most recent mention (count = 1)
    message = "curl -u acmroom:bluepin7 http://twitter.com/statuses/mentions.xml?count=1"
    response = os.popen(message)
    soup = BeautifulStoneSoup(response)
    #We try to get that tweet's id.
    try:
        since_id = soup.find('id').string 
    # We may go over 150 polls per hour (twitter will deny any more requests)
    # and will not return an 'id' in its xml.
    except AttributeError as e:
        print(" 'id' tag was not found in XML.")
        error = soup.find('error').string
        print(" XML may not have been returned by Twitter.")
        print " Twitter: %s" % error
        print " Exiting....."
        exit(1);
    t = threading.Timer(10.0, getNewMention, args = [int(since_id)])
    t.start()
    condition = threading.Condition([lock])
    while :
        t = threading.Timer(10.0, getNewMention, args = [int(since_id)])
        t.start()

try:
    initTwitterPolling()
    if(new_xml_exists and door_open):
        message = "curl -u acmroom:bluepin7 -d status=\"Hey @%s , the door is open,  come visi\t. \" http://twitter.com/statuses/update.json" % screen_name
        os.system(message)

except RuntimeError as e:
    print("Runtime Exception: %s" % e.details)
    print("Exiting....")
    exit(1)
