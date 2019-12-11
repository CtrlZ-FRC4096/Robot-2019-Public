import hal
from wpilib.command.scheduler import Scheduler
from wpilib.interfaces.generichid import GenericHID
from wpilib.xboxcontroller import XboxController
from customcontroller.custom_button import CustomButton
from customcontroller.custom_analog import CustomAnalog
import enum

from customcontroller.extended_trigger import ExtendedTrigger


class XboxCommandController():
	"""This class provides an easy way to link buttons/analogs/triggers/dpad to commands/functions on an Xbox(360/One) controller.

	It is very easy to link a button to a command.  For instance, you could
	link the trigger button of a joystick to a "score" command.
	You can also create custom buttons using any boolean function.
	You can also control the rumble(vibration) feature of the xbox controller
	"""

	def __init__(self, port: int) -> None:
		"""Creates an instance of the XboxCommandController class

		:param port: DriverStation port number for the xbox controller
		"""
		self.xboxController = XboxController(port)
		self.customButtons = {}
		self.createInitialButtons()

	def createInitialButtons(self):
		"""Creates objects for all buttons/triggers/joysticks/dpad on an Xbox(360/One) controller"""
		xbox = self.xboxController

		left = GenericHID.Hand.kLeft
		right = GenericHID.Hand.kRight

		self.A = CustomButton(xbox.getAButton)
		self.B = CustomButton(xbox.getBButton)
		self.X = CustomButton(xbox.getXButton)
		self.Y = CustomButton(xbox.getYButton)
		self.LEFT_BUMPER = CustomButton(lambda: xbox.getBumper(left))
		self.RIGHT_BUMPER = CustomButton(lambda: xbox.getBumper(right))
		self.START = CustomButton(xbox.getStartButton)
		self.BACK = CustomButton(xbox.getBackButton)
		self.LEFT_STICK = CustomButton(lambda: xbox.getStickButton(left))
		self.RIGHT_STICK = CustomButton(lambda: xbox.getStickButton(right))

		self.LEFT_JOY_X = CustomAnalog(lambda: xbox.getX(left))
		self.LEFT_JOY_Y = CustomAnalog(lambda: xbox.getY(left))
		self.RIGHT_JOY_X = CustomAnalog(lambda: xbox.getX(right))
		self.RIGHT_JOY_Y = CustomAnalog(lambda: xbox.getY(right))
		self.LEFT_TRIGGER = CustomAnalog(lambda: xbox.getTriggerAxis(left))
		self.RIGHT_TRIGGER = CustomAnalog(lambda: xbox.getTriggerAxis(right))

		self.POV = POVWrapper(xbox.getPOV)

		self.BOTH_TRIGGERS = CustomAnalog(lambda: -(self.LEFT_TRIGGER.get()) if self.LEFT_TRIGGER.get() > self.RIGHT_TRIGGER.get() else self.RIGHT_TRIGGER.get())
		self.LEFT_TRIGGER_AS_BUTTON = CustomButton(lambda: self.LEFT_TRIGGER.getRaw() > 0.05)
		self.RIGHT_TRIGGER_AS_BUTTON = CustomButton(lambda: self.RIGHT_TRIGGER.getRaw() > 0.05)

	def addCustomButton(self, name, *inputs):
		"""Creates a CustomButton from a combination of existing buttons or any function you want.

		:param inputs: comma separated buttons / functions
		:returns: the created button
		"""
		if name in self.customButtons:
			raise ValueError("A custom button with this name already exists!")

		inputs = list(inputs)

		self.customButtons[name] = CustomButton(*inputs)
		return self.customButtons[name]

	def getCustomButton(self, name):
		"""Gets the desired CustomButton

		:param name: name of the desired CustomButton
		:returns: the desired CustomButton object
		"""
		if name not in self.customButtons:
			raise ValueError("A custom button with this name does not exist!")
		return self.customButtons[name]

	def getController(self):
		"""
		:returns: The wpilib XboxController object stored wihtin this class
		"""
		return self.xboxController

	def setLeftRumble(self, intensity = 1):
		"""Sets the Rumble(Vibration) for the left side of the controller

		:param intensity: How powerful the vibration should be
		"""
		self.xboxController.setRumble(GenericHID.Hand.kLeft, intensity)

	def setRightRumble(self, intensity = 1):
		"""Sets the Rumble(Vibration) for the right side of the controller

		:param intensity: How powerful the vibration should be
		"""
		self.xboxController.setRumble(GenericHID.Hand.kRight, intensity)

	def setRumble(self, intensity = 1):
		"""Sets the Rumble(Vibration) for the entire controller

		:param intensity: How powerful the vibration should be
		"""
		self.setLeftRumble(intensity)
		self.setRightRumble(intensity)

	def setRumbleByLocation(self, baseIntensity = 0, location = 0):
		"""Sets the Rumble(Vibration) based on where the vibration should occur

		:param baseIntensity: How powerful the vibration should be in the center [0, 1]
		:param location: Where the vibration should occur [-1, 1] -1 is full left. 1 is full right
		"""
		self.setLeftRumble(baseIntensity - location)
		self.setRightRumble(baseIntensity + location)


class POVWrapper():

	__getPOV = None

	def __call__(self):
		"""Calls get() on this object.

		:returns: the value of get()
		"""
		if self.__getPOV == None:
			raise RuntimeError("This Controller was not properly initialized")
		return self.get()

	def __init__(self, getPOV):
		"""Creates all CustomButton objects for the POV."""

		self.__getPOV = getPOV

		self.NONE = CustomButton(lambda: self.__isPressed(-1))
		self.ANY = CustomButton(lambda: self.get() != 0)
		self.UP = CustomButton(lambda: self.__isPressed(0))
		self.DOWN = CustomButton(lambda: self.__isPressed(180))
		self.LEFT = CustomButton(lambda: self.__isPressed(270))
		self.RIGHT = CustomButton(lambda: self.__isPressed(90))
		self.DIAG_UP_LEFT = CustomButton(lambda: self.__isPressed(315))
		self.DIAG_UP_RIGHT = CustomButton(lambda: self.__isPressed(45))
		self.DIAG_DOWN_LEFT = CustomButton(lambda: self.__isPressed(225))
		self.DIAG_DOWN_RIGHT = CustomButton(lambda: self.__isPressed(135))

	def get(self):
		"""Gets the raw value of the POV

		:returns: raw value of the POV
		"""
		return self.__getPOV(0)

	def __isPressed(self, value):
		"""Checks if the POV's raw value == the desired value

		:returns: True/False
		"""
		return self.get() == value







