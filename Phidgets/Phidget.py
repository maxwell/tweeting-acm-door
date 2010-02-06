"""Copyright 2008 Phidgets Inc.
This work is licensed under the Creative Commons Attribution 2.5 Canada License. 
To view a copy of this license, visit http://creativecommons.org/licenses/by/2.5/ca/
"""

__author__ = 'Adam Stelmack'
__version__ = '2.1.6'
__date__ = 'Oct 21 2009'

from threading import *
from ctypes import *
from Phidgets.PhidgetLibrary import *
from Phidgets.PhidgetException import *
from Phidgets.Events.Events import *
import sys

class PhidgetLogLevel:
    PHIDGET_LOG_CRITICAL = 1
    PHIDGET_LOG_ERROR = 2
    PHIDGET_LOG_WARNING = 3
    PHIDGET_LOG_DEBUG = 4
    PHIDGET_LOG_INFO = 5
    PHIDGET_LOG_VERBOSE = 6

class Phidget:
    """This is the base class from which all Phidget device classes derive."""
    def __init__(self):
        """Default Class constructor.
        
        This constructor is to be used only by subclasses, as the Phidget calss should never need to be instatiated directly by the user.
        """
        self.handle = c_void_p()
        
        self.__attach = None
        self.__detach = None
        self.__error = None
        self.__serverConnect = None
        self.__serverDisconnect = None
        
        self.__onAttach = None
        self.__onDetach = None
        self.__onError = None
        self.__onServerConnect = None
        self.__onServerDisconnect = None
        
        if sys.platform == 'win32':
            self.__ATTACHHANDLER = WINFUNCTYPE(c_int, c_void_p, c_void_p)
            self.__DETACHHANDLER = WINFUNCTYPE(c_int, c_void_p, c_void_p)
            self.__ERRORHANDLER = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_char_p)
            self.__SERVERATTACHHANDLER = WINFUNCTYPE(c_int, c_void_p, c_void_p)
            self.__SERVERDETACHHANDLER = WINFUNCTYPE(c_int, c_void_p, c_void_p)
        elif sys.platform == 'darwin' or sys.platform == 'linux2':
            self.__ATTACHHANDLER = CFUNCTYPE(c_int, c_void_p, c_void_p)
            self.__DETACHHANDLER = CFUNCTYPE(c_int, c_void_p, c_void_p)
            self.__ERRORHANDLER = CFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_char_p)
            self.__SERVERATTACHHANDLER = CFUNCTYPE(c_int, c_void_p, c_void_p)
            self.__SERVERDETACHHANDLER = CFUNCTYPE(c_int, c_void_p, c_void_p)
        

    def closePhidget(self):
        """Closes this Phidget.
        
        This will shut down all threads dealing with this Phidget and you won't recieve any more events.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened.
        """
        try:
            result = PhidgetLibrary.getDll().CPhidget_close(self.handle)
        except RuntimeError:
            raise

        if result > 0:
            raise PhidgetException(result)
        else:
            result = PhidgetLibrary.getDll().CPhidget_delete(self.handle)
            self.handle = None
            if result > 0:
                raise PhidgetException(result)

    def openPhidget(self, serial=-1):
        """Open a Phidget with or without a serial number.
        
        Open is pervasive. What this means is that you can call open on a device before it is plugged in, and keep the device opened across device dis- and re-connections.
        
        Open is Asynchronous.  What this means is that open will return immediately -- before the device being opened is actually available,
        so you need to use either the attach event or the waitForAttachment method to determine if a device is available before using it.
        
        If no arguement is provided, the first available Phidget will be opened. If there are two Phidgets of the same type attached to the system,
        you should specify a serial number, as there is no guarantee which Phidget will be selected by the call to open().
        
        The serial number is a unique number assigned to each Phidget during production and can be used to uniquely identify specific phidgets.
        
        Parameters:
            serial<int>: The serial number of the device
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException
        """
        try:
            result = PhidgetLibrary.getDll().CPhidget_open(self.handle, c_int(serial))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)

    def openRemote(self, serverID, serial=-1, password=""):
        """Open this Phidget remotely using a Server ID, securely providing a password, and whether or not to connect to a specific serial number.
        
        Providing a password will open the connection securely depending on if a password is set on the host machine's webservice.
        
        If no serial number is provided, the first available Phidget will be opened. If there are two Phidgets of the same type attached to the system,
        you should specify a serial number, as there is no guarantee which Phidget will be selected by the call to open().
        
        Parameters:
            serverID<string>: ServerID of the Phidget Webservice
            serial<int>: The serial number of the device
            password<string>: The secure password for the Phidget Webservice
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: if the Phidget Webservice cannot be contacted
        """
        if not isinstance(serial, int):
            if password == "":
                password = serial
                serial = -1
            else:
                raise TypeError("inappropriate arguement type: serial %s" % (type(serial)))
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_openRemote(self.handle, c_int(serial), c_char_p(serverID), c_char_p(password))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)

    def openRemoteIP(self, IPAddress, port, serial=-1, password=""):
        """Open this Phidget remotely using an IP Address, securely providing a password,and whether or not to connect to a specific serial number.
        
        Providing a password will open the connection securely depending on if a password is set on the host machine's webservice.
        
        If no serial number is provided, the first available Phidget will be opened. If there are two Phidgets of the same type attached to the system,
        you should specify a serial number, as there is no guarantee which Phidget will be selected by the call to open().
        
        Parameters:
            IPAddress<string>: IP Address or hostname of the Phidget Webservice
            port<int>: Port of the Phidget Webservice
            serial<int>: The serial number of the device
            password<string>: The secure password for the Phidget Webservice
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: if the Phidget Webservice cannot be contacted
        """
        if not isinstance(serial, int):
            if password == "":
                password = serial
                serial = -1
            else:
                raise TypeError("inappropriate arguement type: serial %s" % (type(serial)))
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_openRemoteIP(self.handle, c_int(serial), c_char_p(IPAddress), c_int(port), c_char_p(password))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)

    def getDeviceLabel(self):
        """Gets the label associated with this Phidget.
        
        This label is a String - up to ten digits - that is stored in the Flash memory of newer Phidgets.
        This label can be set programatically (see setDeviceLabel), and is non-volatile - so it is remembered even if the Phidget is unplugged.
        
        Returns:
            The label associated with this Phidget <string>.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened and attached, or if this Phidget does not support labels.
        """
        label = c_char_p()
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_getDeviceLabel(self.handle, byref(label))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            return label

    def getDeviceName(self):
        """Return the name of this Phidget.
        
        This is a string that describes the device. For example, a PhidgetInterfaceKit 
        could be described as "Phidget InterfaceKit 8/8/8", or "Phidget InterfaceKit 0/0/4", among others, depending on the specific device.
        
        This lets you determine the specific type of a Phidget, within the broader classes of Phidgets, such as PhidgetInterfaceKit, or PhidgetServo.
        
        Returns:
            The name of the device <string>.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this phidget is not opened or attached.
        """
        ptr = c_char_p()
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_getDeviceName(self.handle, byref(ptr))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            return ptr.value

    def getDeviceType(self):
        """Return the device type of this Phidget.
        
        This is a string that describes the device as a class of devices. For example, all PhidgetInterfaceKit Phidgets
        will returns the String "PhidgetInterfaceKit".
        
        Returns:
            The Device Type <string>.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If there is no Phidget attached.
        """
        ptr = c_char_p()
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_getDeviceType(self.handle, byref(ptr))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            return ptr.value

    def getDeviceVersion(self):
        """Returns the device version of this Phidget.
        
        This number is simply a way of distinguishing between different revisions of a specific type of Phidget, and is
        only really of use if you need to troubleshoot device problems with Phidgets Inc.
        
        Returns:
            The Device Version <int>.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If there is no Phidget attached.
        """
        version = c_int()
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_getDeviceVersion(self.handle, byref(version))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            return version.value

    def isAttached(self):
        """Returns the attached status of this Phidget.
        
        This method returns True or False, depending on whether the Phidget is phisically plugged into the computer, initialized, and ready to use - or not.
        If a Phidget is not attached, many functions calls will fail with a PhidgetException, so either checking this function, or using the Attach and Detach events, is recommended, if a device is likely to be attached or detached during use.
        
        Returns:
            Attached Status of the Phidget <boolean>
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened.
        """
        status = c_int()
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_getDeviceStatus(self.handle, byref(status))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            if status.value == 1:
                return True
            else:
                return False

    def getLibraryVersion(self):
        """Returns the library version.
        
        This is the library version of the underlying phidget21 C library and not the version of the Python wrapper module implementation.
        The version is retured as a string which contains the version number and build date.
        
        Returns:
            The Library Version <string>.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened and attached.
        """
        libVer = c_char_p()
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_getLibraryVersion(byref(libVer))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            return libVer.value

    def getSerialNum(self):
        """Returns the unique serial number of this Phidget.
        
        This number is set during manufacturing, and is unique across all Phidgets. This number can be used in calls to open to specify this specific Phidget to be opened.
        
        Returns:
            The Serial Number <int>.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened and attached.
        """
        serialNo = c_int()
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_getSerialNumber(self.handle, byref(serialNo))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            return serialNo.value

    def __nativeAttachEvent(self, handle, usrptr):
        if self.__attach != None:
            self.__attach(AttachEventArgs(self))
        return 0

    def setOnAttachHandler(self, attachHandler):
        """Sets the Attach Event Handler.
        
        The attach handler is a method that will be called when this Phidget is physically attached to the system, and has gone through its initalization, and so is ready to be used.
        
        Parameters:
            attachHandler: hook to the attachHandler callback function
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened.
        """
        self.__attach = attachHandler
        self.__onAttach = self.__ATTACHHANDLER(self.__nativeAttachEvent)
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_set_OnAttach_Handler(self.handle, self.__onAttach, None)
        except RuntimeError:
            self.__attach = None
            self.__onAttach = None
            raise
        
        if result > 0:
            raise PhidgetException(result)

    def __nativeDetachEvent(self, handle, usrptr):
        if self.__detach != None:
            self.__detach(DetachEventArgs(self))
        return 0

    def setOnDetachHandler(self, detachHandler):
        """Sets the Detach Event Handler.
        
        The detach handler is a method that will be called when this Phidget is phisically detached from the system, and is no longer available.
        This is particularly usefull for applications when a phisical detach would be expected.
        
        Remember that many of the methods, if called on an unattached device, will throw a PhidgetException.
        This Exception can be checked to see if it was caused by a device being unattached, but a better method would be to regiter the detach handler,
        which could notify the main program logic that the device is no longer available, disable GUI controls, etc.
        
        Parameters:
            detachHandler: hook to the detachHandler callback function
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened.
        """
        self.__detach = detachHandler
        self.__onDetach = self.__DETACHHANDLER(self.__nativeDetachEvent)
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_set_OnDetach_Handler(self.handle, self.__onDetach, None)
        except RuntimeError:
            self.__detach = None
            self.__onDetach = None
            raise
        
        if result > 0:
            raise PhidgetException(result)

    def __nativeErrorEvent(self, handle, usrptr, errorCode, errorMessage):
        if self.__error != None:
            code = errorCode
            message = errorMessage
            self.__error(ErrorEventArgs(self, message, code))
        return 0

    def setOnErrorhandler(self, errorHandler):
        """Sets the Error Event Handler.
        
        The error handler is a method that will be called when an asynchronous error occurs.
        Error events are not currently used, but will be in the future to report any problems that happen out of context from a direct function call.
        
        Parameters:
            errorHandler: hook to the errorHandler callback function.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened.
        """
        self.__error = errorHandler
        self.__onError = self.__ERRORHANDLER(self.__nativeErrorEvent)
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_set_OnError_Handler(self.handle, self.__onError, None)
        except RuntimeError:
            self.__error = None
            self.__onError = None
            raise
        
        if result > 0:
            raise PhidgetException(result)

    def waitForAttach(self, timeout):
        """Waits for this Phidget to become available.
        
        This method can be called after open has been called to wait for thid Phidget to become available.
        This is usefull because open is asynchronous (and thus returns immediately), and most methods will throw a PhidgetException is they are called before a device is actually ready.
        This method is synonymous with polling the isAttached method until it returns True, or using the Attach event.
        
        This method blocks for up to the timeout, at which point it will throw a PhidgetException. Otherwise, it returns when the phidget is attached and initialized.
        
        A timeout of 0 is infinite.
        
        Parameters:
            timeout<long>: Timeout in milliseconds
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened.
        """
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_waitForAttachment(self.handle, c_long(timeout))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)

    def __nativeServerConnectEvent(self, handle, usrptr):
        if self.__serverConnect != None:
            self.__serverConnect(ServerConnectArgs(self))
        return 0

    def setOnServerConnectHandler(self, serverConnectHandler):
        """Sets the Server Connect Event Handler.
        
        The serverConnect handler is a method that will be called when a connection to a server is made. This is only usefull for Phidgets opened remotely.
        
        Parameters:
            serverConnectHandler: hook to the serverConnectHandler callback function
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened
        """
        self.__serverConnect = serverConnectHandler
        self.__onServerConnect = self.__SERVERATTACHHANDLER(self.__nativeServerConnectEvent)
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_set_OnServerConnect_Handler(self.handle, self.__onServerConnect, None)
        except RuntimeError:
            self.__serverConnect = None
            self.__onServerConnect = None
            raise
        
        if result > 0:
            raise PhidgetException(result)

    def __nativeServerDisconnectEvent(self, handle, usrptr):
        if self.__serverDisconnect != None:
            self.__serverDisconnect(ServerConnectArgs(self))
        return 0

    def setOnServerDisconnectHandler(self, serverDisconnectHandler):
        """Set the Server Disconnect event handler.
        
        The serverDisconnect handler is a method that will be called when a connection to a server is terminated. This is only usefull for Phidgets opened remotely.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened
        """
        self.__serverDisconnect = serverDisconnectHandler
        self.__onServerDisconnect = self.__SERVERDETACHHANDLER(self.__nativeServerDisconnectEvent)
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_set_OnServerDisconnect_Handler(self.handle, self.__onServerDisconnect, None)
        except RuntimeError:
            self.__serverDisconnect = None
            self.__onServerDisconnect = None
            raise
        
        if result > 0:
            raise PhidgetException(result)

    def getServerAddress(self):
        """Returns the Address of a Phidget Webservice.
        
        Returns the Address of a Phidget Webservice when this Phidget was opened as remote.
        This may be an IP Address or a hostname.
        
        Returns:
            The Address of the Webservice <string>.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: if this Phidget was open opened as a remote Phidget.
        """
        serverAddr = c_char_p()
        port = c_int()
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_getServerAddress(self.handle, byref(serverAddr), byref(port))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            return serverAddr.value

    def getServerID(self):
        """Returns the Server ID of a Phidget Webservice.
        
        Returns the Server ID of a Phidget Webservice when this Phidget was opened as remote.
        This is an arbitrary server identifier, independant of IP address and Port.
        
        Returns:
            The ServerID of the Webservice <string>.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: if this Phidget was open opened as a remote Phidget.
        """
        serverID = c_char_p()
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_getServerID(self.handle, byref(serverID))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            return serverID.value

    def isAttachedToServer(self):
        """Returns the network attached status for remotely opened Phidgets.
        
        This method returns True or False, depending on whether a connection to the Phidget WebService is open - or not.
        If this is false for a remote Phidget then the connection is not active - either because a connection has not yet been established,
        or because the connection was terminated.
        
        Returns:
            Phidget Network Attached Status <boolean>.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened remotely.
        """
        serverStatus = c_int()
        
        try:
            result = PhidgetLibrary.getDll().CPhidget_getServerStatus(self.handle, byref(serverStatus))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            if serverStatus == 1:
                return True
            else:
                return False

    @staticmethod
    def enableLogging(level, file):
        """Turns on logging in the native C Library.
        
        This is mostly usefull for debugging purposes - when an issue needs to be resolved by Phidgets Inc.
        The output is mostly low-level library information, that won't be usefull for most users.
        
        Logging may be usefull for users trying to debug their own problems, as logs can be inserted by the user using log.
        The level can be one of:
        PhidgetLogLevel.PHIDGET_LOG_VERBOSE (1),
        PhidgetLogLevel.PHIDGET_LOG_INFO (2),
        PhidgetLogLevel.PHIDGET_LOG_DEBUG (3),
        PhidgetLogLevel.PHIDGET_LOG_WARNING (4),
        PhidgetLogLevel.PHIDGET_LOG_ERROR (5)or
        PhidgetLogLevel.PHIDGET_LOG_CRITICAL (6)
        
        Parameters:
            level<int>: highest level of logging that will be output, the PhidgetLogLevel object has been provided for a readable way to set this.
            file<string>: path and name of file to output to.  specify NULL to output to the console.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException
        """
        try:
            result = PhidgetLibrary.getDll().CPhidget_enableLogging(c_int(level), c_char_p(file))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)

    @staticmethod
    def disableLogging():
        """Turns off logging in the native C Library.
        
        This only needs to be called if enableLogging was called to turn logging on.
        This will turn logging back off.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException
        """
        try:
            result = PhidgetLibrary.getDll().CPhidget_disableLogging()
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)

    @staticmethod
    def log(level, id, log):
        """Adds a log entry into the phidget log.
        
        This log is enabled by calling enableLogging and this allows the entry of user logs in amongst the phidget library logs.
        
        The level can be one of:
        PhidgetLogLevel.PHIDGET_LOG_VERBOSE,
        PhidgetLogLevel.PHIDGET_LOG_INFO,
        PhidgetLogLevel.PHIDGET_LOG_DEBUG,
        PhidgetLogLevel.PHIDGET_LOG_WARNING,
        PhidgetLogLevel.PHIDGET_LOG_ERROR or
        PhidgetLogLevel.PHIDGET_LOG_CRITICAL
        
        Note: PhidgetLogLevel.PHIDGET_LOG_DEBUG should not be used, as these logs are only printed when using the debug library,
        which is not generally available.
        
        Parameters:
            level<int>: level to enter the log at.
            id<string>: an arbitrary identifier for this log.  This can be NULL. The C library uses this field for source filename and line number.
            log<string>: the message to log.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException
        """
        try:
            result = PhidgetLibrary.getDll().CPhidget_log(c_int(level), c_char_p(id), c_char_p(log))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
