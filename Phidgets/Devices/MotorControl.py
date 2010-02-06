"""Copyright 2008 Phidgets Inc.
This work is licensed under the Creative Commons Attribution 2.5 Canada License. 
To view a copy of this license, visit http://creativecommons.org/licenses/by/2.5/ca/
"""

__author__ = 'Adam Stelmack'
__version__ = '2.1.6'
__date__ = 'Sep 18 2009'

from threading import *
from ctypes import *
from Phidgets.Phidget import *
from Phidgets.PhidgetException import *
import sys

class MotorControl(Phidget):
    """This class represents a Phidget Motor Controller. All methods to to control a motor controller and read back motor data are implemented in this class.
    
    The Motor Control Phidget is able to control 1 or more DC motors. Both speed and acceleration are controllable. Speed is controlled via PWM.
    The size of the motors that can be driven depends on the motor controller. See your hardware documentation for more information.
    
    The motor Controller boards also has 0 or more digital inputs.
    
    Extends:
        Phidget
    """
    def __init__(self):
        """The Constructor Method for the MotorControl Class
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
        """
        Phidget.__init__(self)
        
        self.__inputChange = None
        self.__velocityChange = None
        self.__currentChange = None
        
        self.__onInputChange = None
        self.__onVelocityChange = None
        self.__onCurrentChange = None
        
        try:
            PhidgetLibrary.getDll().CPhidgetMotorControl_create(byref(self.handle))
        except RuntimeError:
            raise
        
        if sys.platform == 'win32':
            self.__INPUTCHANGEHANDLER = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_int)
            self.__VELOCITYCHANGEHANDLER = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_double)
            self.__CURRENTCHANGEHANDLER = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_double)
        elif sys.platform == 'darwin' or sys.platform == 'linux2':
            self.__INPUTCHANGEHANDLER = CFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_int)
            self.__VELOCITYCHANGEHANDLER = CFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_double)
            self.__CURRENTCHANGEHANDLER = CFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_double)

    def getMotorCount(self):
        """Returns the number of motors supported by this Phidget.
        
        This does not neccesarily correspond to the number of motors actually attached to the board.
        
        Returns:
            The number of supported motors <int>.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened and attached.
        """
        motorCount = c_int()
        
        try:
            result = PhidgetLibrary.getDll().CPhidgetMotorControl_getMotorCount(self.handle, byref(motorCount))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            return motorCount.value

    def getVelocity(self, index):
        """Returns a motor's velocity.
        
        The valid range is -100 - 100, with 0 being stopped.
        
        Parameters:
            index<int>: index of the motor.
        
        Returns:
            The current velocity of the motor <double>.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened and attached, or if the index is invalid.
        """
        veloctiy = c_double()
        
        try:
            result = PhidgetLibrary.getDll().CPhidgetMotorControl_getVelocity(self.handle, c_int(index), byref(veloctiy))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            return veloctiy.value

    def setVelocity(self, index, value):
        """Sets a motor's velocity.
        
        The valid range is from -100 to 100, with 0 being stopped. -100 and 100 both corespond to full voltage,
        with the value in between corresponding to different widths of PWM.
        
        Parameters:
            index<int>: index of the motor.
            value<double>: requested velocity for the motor.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened and attached, or if the index or velocity value are invalid.
        """
        try:
            result = PhidgetLibrary.getDll().CPhidgetMotorControl_setVelocity(self.handle, c_int(index), c_double(value))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)

    def __nativeVelocityChangeEvent(self, handle, usrptr, index, value):
        if self.__velocityChange != None:
            self.__velocityChange(VelocityChangeEventArgs(self, index, value))
        return 0

    def setOnVelocityChangeHandler(self, velocityChangeHandler):
        """Sets the VelocityChange Event Handler.
        
        The velocity change handler is a method that will be called when the velocity of a motor changes.
        These velocity changes are reported back from the Motor Controller and so correspond to actual motor velocity over time.
        
        Parameters:
            velocityChangeHandler: hook to the velocityChangeHandler callback function.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException
        """
        self.__velocityChange = velocityChangeHandler
        self.__onVelocityChange = self.__VELOCITYCHANGEHANDLER(self.__nativeVelocityChangeEvent)
        
        try:
            result = PhidgetLibrary.getDll().CPhidgetMotorControl_set_OnVelocityChange_Handler(self.handle, self.__onVelocityChange, None)
        except RuntimeError:
            self.__velocityChange = None
            self.__onVelocityChange = None
            raise
        
        if result > 0:
            raise PhidgetException(result)

    def getAcceleration(self, index):
        """Returns a motor's acceleration.
        
        The valid range is between getAccelerationMin and getAccelerationMax,
        and refers to how fast the Motor Controller will change the speed of a motor.
        
        Parameters:
            index<int>: index of motor.
        
        Returns:
            The acceleration of the motor <double>.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened and attached, or if the index is invalid.
        """
        accel = c_double()
        
        try:
            result = PhidgetLibrary.getDll().CPhidgetMotorControl_getAcceleration(self.handle, c_int(index), byref(accel))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            return accel.value

    def setAcceleration(self, index, value):
        """Sets a motor's acceleration.
        
        The valid range is between getAccelerationMin and getAccelerationMax.
        This controls how fast the motor changes speed.
        
        Parameters:
            index<int>: index of the motor.
            value<double>: requested acceleration for that motor.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened and attached, or if the index or acceleration value are invalid.
        """
        try:
            result = PhidgetLibrary.getDll().CPhidgetMotorControl_setAcceleration(self.handle, c_int(index), c_double(value))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)

    def getAccelerationMax(self, index):
        """Returns the maximum acceleration that a motor will accept, or return.
        
        Parameters:
            index<int>: Index of the motor.
        
        Returns:
            Maximum acceleration of the motor <double>.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened and attached.
        """
        accelMax = c_double()
        
        try:
            result = PhidgetLibrary.getDll().CPhidgetMotorControl_getAccelerationMax(self.handle, c_int(index), byref(accelMax))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            return accelMax.value

    def getAccelerationMin(self, index):
        """Returns the minimum acceleration that a motor will accept, or return.
        
        Parameters:
            index<int>: Index of the motor.
        
        Returns:
            Minimum acceleration of the motor <double>.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened and attached.
        """
        accelMin = c_double()
        
        try:
            result = PhidgetLibrary.getDll().CPhidgetMotorControl_getAccelerationMin(self.handle, c_int(index), byref(accelMin))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            return accelMin.value

    def getCurrent(self, index):
        """Returns a motor's current usage.
        
        The valid range is 0 - 255. Note that this is not supported on all motor controllers.
        
        Parameters:
            index<int>: index of the motor.
        
        Returns:
            The current usage of the motor <double>.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened and attached, or if the index is invalid.
        """
        current = c_double()
        
        try:
            result = PhidgetLibrary.getDll().CPhidgetMotorControl_getCurrent(self.handle, c_int(index), byref(current))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            return current.value

    def __nativeCurrentChangeEvent(self, handle, usrptr, index, value):
        if self.__currentChange != None:
            self.__currentChange(CurrentChangeEventArgs(self, index, value))
        return 0

    def setOnCurrentChangeHandler(self, currentChangeHandler):
        """Sets the CurrentCHange Event Handler.
        
        The current change handler is a method that will be called when the current consumed by a motor changes.
        Note that this event is not supported with the current motor controller, but will be supported in the future
        
        Parameters:
            currentChangeHandler: hook to the currentChangeHandler callback function.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException
        """
        self.__currentChange = currentChangeHandler
        self.__onCurrentChange = self.__CURRENTCHANGEHANDLER(self.__nativeCurrentChangeEvent)
        
        try:
            result = PhidgetLibrary.getDll().CPhidgetMotorControl_set_OnCurrentChange_Handler(self.handle, self.__onCurrentChange, None)
        except RuntimeError:
            self.__currentChange = None
            self.__onCurrentChange = None
            raise
        
        if result > 0:
            raise PhidgetException(result)

    def getInputCount(self):
        """Returns the number of digital inputs.
        
        Not all Motor Controllers have digital inputs.
        
        Returns:
            The number of digital Inputs <int>.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened and attached.
        """
        inputCount = c_int()
        
        try:
            result = PhidgetLibrary.getDll().CPhidgetMotorControl_getInputCount(self.handle, byref(inputCount))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            return inputCount.value

    def getInputState(self, index):
        """Returns the state of a digital input.
        
        True means that the input is activated, and False indicated the default state.
        
        Parameters:
            index<int> index of the input.
        
        Returns:
            The state of the input <boolean>.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException: If this Phidget is not opened and attached, or if the index is invalid.
        """
        inputState = c_int()
        
        try:
            result = PhidgetLibrary.getDll().CPhidgetMotorControl_getInputState(self.handle, c_int(index), byref(inputState))
        except RuntimeError:
            raise
        
        if result > 0:
            raise PhidgetException(result)
        else:
            if inputState.value == 1:
                return True
            else:
                return False

    def __nativeInputChangeEvent(self, handle, usrptr, index, value):
        if self.__inputChange != None:
            if value == 1:
                state = True
            else:
                state = False
            self.__inputChange(InputChangeEventArgs(self, index, state))
        return 0

    def setOnInputChangeHandler(self, inputChangeHandler):
        """Sets the InputChange Event Handler.
        
        The input change handler is a method that will be called when an input on this Motor Controller board has changed.
        
        Parameters:
            inputChangeHandler: hook to the inputChangeHandler callback function.
        
        Exceptions:
            RuntimeError - If current platform is not supported/phidget c dll cannot be found
            PhidgetException
        """
        self.__inputChange = inputChangeHandler
        self.__onInputChange = self.__INPUTCHANGEHANDLER(self.__nativeInputChangeEvent)
        
        try:
            result = PhidgetLibrary.getDll().CPhidgetMotorControl_set_OnInputChange_Handler(self.handle, self.__onInputChange, None)
        except RuntimeError:
            self.__inputChange = None
            self.__onInputChange = None
            raise
        
        if result > 0:
            raise PhidgetException(result)
