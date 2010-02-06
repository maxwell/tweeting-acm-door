from Phidgets.PhidgetException import * 
from Phidgets.Events.Events import * 
from Phidgets.Devices.RFID import *
import os
import time
import datetime
from BeautifulSoup import BeautifulStoneSoup

#GLOBALS
tag = "210050A70B"
door_open = False
#Arbitrary initial value for since_id
since_id = "8711950820"

#Information Display Function
def displayDeviceInfo():
    print("|------------|----------------------------------|--------------|------------|")
    print("|- Attached -|-              Type              -|- Serial No. -|-  Version -|")
    print("|------------|----------------------------------|--------------|------------|")
    print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (rfid.isAttached(), rfid.getDeviceType(), rfid.getSerialNum(), rfid.getDeviceVersion()))
    print("|------------|----------------------------------|--------------|------------|")
    print("Number of outputs: %i -- Antenna Status: %s -- Onboard LED Status: %s" % (rfid.getOutputCount(), rfid.getAntennaOn(), rfid.getLEDOn()))


def sinceIDReply()
#Figure out threading.Timer to call this function every 5 minutes or something.
    message = "curl -u acmroom:bluepin7 http://twitter.com/statuses/mentions.xml?since_id=%s" % since_id
    response = os.popen(message)
    
    print soup.prettify()
    screen_name = soup.find('screen_name').string
    #Get the new id
    since_id = soup.find('id').string

#Event Handler Callback Functions
def rfidAttached(e):
    attached = e.device
    print("RFID %i Attached!" % (attached.getSerialNum()))

    

def rfidDetached(e):
    detached = e.device
    print("RFID %i Detached!" % (detached.getSerialNum()))
	

def rfidError(e):
    source = e.device
    print("RFID %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))

def rfidOutputChanged(e):
    source = e.device
    print("RFID %i: Output %i State: %s" % (source.getSerialNum(), e.index, e.state))

def rfidTagGained(e):
    print
    print
    print
    source = e.device
    rfid.setLEDOn(1)
    print("RFID %i: Tag Read: %s" % (source.getSerialNum(), e.tag))
    if (tag == e.tag):
		message = "curl -u acmroom:bluepin7 -d status=\"the ACM room door is now closed :(  posted at %s \" http://twitter.com/statuses/update.json" % str(time.time())
		door_open = False	
		os.system(message)
		time.sleep(1)

def rfidTagLost(e):
    print
    print
    print
    source = e.device
    rfid.setLEDOn(0)
    print("RFID %i: Tag Lost: %s" % (source.getSerialNum(), e.tag))
    if (tag == e.tag):
   		message = "curl -u acmroom:bluepin7 -d status=\"ACM ROOM IS OPEN! come hang out! posted at %s \" http://twitter.com/statuses/update.json" % str(time.time())
		door_open = True
		os.system(message)
		time.sleep(1)  


# Create an RFID object
try:
    rfid = RFID()
    rfid.setOnAttachHandler(rfidAttached)
    rfid.setOnDetachHandler(rfidDetached)
    rfid.setOnErrorhandler(rfidError)
	
    rfid.setOnTagHandler(rfidTagGained)
    rfid.setOnTagLostHandler(rfidTagLost)
	
    # Open RFID
    rfid.openPhidget()
	
    # Attach and Display RFID Info
    try:
        rfid.waitForAttach(10000)
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        try:
            rfid.closePhidget()
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Exiting....")
            exit(1)
        else:
            displayDeviceInfo()
	
    # Set Antenna On
    print("Turning on the RFID antenna....")
    rfid.setAntennaOn(True)
    #Get the most recent message, whether new or old, so we can find its id.
    message = "curl -u acmroom:bluepin7 http://twitter.com/statuses/mentions.xml?count=1"
    response = os.popen(message)

    soup = BeautifulStoneSoup(response)
    #Get the most recent id, new or old.
    since_id = soup.find('id').string


    if(since_id >  && door_open):
        message = "curl -u acmroom:bluepin7 -d status=\"Hey @%s , the door is open,  come visit. \" http://twitter.com/statuses/update.json" % screen_name
        os.system(message)

	#poll twitter for new @s
	#grab new one , and username
	#curl "@username, hey I am BOOL 

    print("Closing...")
    message = "curl -u acmroom:bluepin7 -d status=\"acmdoor isn't tweeting right now... posted at %s \" http://twitter.com/statuses/update.json" % str(time.time())
    os.system(message)

    print("Done.")
    exit(0)
	
except RuntimeError as e:
    print("Runtime Exception: %s" % e.details)
    print("Exiting....")
    exit(1)
