# validated: 2018-10-30 EN 0a2ab4f0d782 edu/wpi/first/wpilibj/buttons/Trigger.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from wpilib.command import command
from wpilib.command.command import Command
from wpilib.sendablebase import SendableBase
from wpilib.sendablebuilder import SendableBuilder
from customcontroller.command_call import Command_Call

__all__ = ["ExtendedTrigger"]


class ExtendedTrigger(SendableBase):
	"""This class provides an easy way to link commands to inputs.

	It is very easy to link a button to a command.  For instance, you could
	link the trigger button of a joystick to a "score" command.

	It is encouraged that teams write a subclass of Trigger if they want to
	have something unusual (for instance, if they want to react to the user
	holding a button while the robot is reading a certain sensor input).
	For this, they only have to write the :func:`get` method to get the full
	functionality of the Trigger class.
	"""

	def get(self) -> bool:
		"""Returns whether or not the trigger is active

		This method will be called repeatedly a command is linked to the
		Trigger.

		:returns: whether or not the trigger condition is active.
		"""
		raise NotImplementedError

	def grab(self) -> bool:
		"""Returns whether :meth:`get` returns True or the internal table for
		:class:`.SmartDashboard` use is pressed.
		"""
		return self.get() or getattr(self, "sendablePressed", False)

	def whenActive(self, command) -> None:
		"""Starts the given command whenever the trigger just becomes active.

		:param command: the command to start
		"""
		command = self._checkInput(command)

		def execute() -> None:
			pressed = self.grab()

			if not execute.pressedLast and pressed:
				command.start()

			execute.pressedLast = pressed

		execute.pressedLast = self.grab()
		from wpilib.command import Scheduler

		Scheduler.getInstance().addButton(execute)
		return self

	def whileActive(self, command) -> None:
		"""Constantly starts the given command while the button is held.

		:meth:`Command.start` will be called repeatedly while the trigger is
		active, and will be canceled when the trigger becomes inactive.

		:param command: the command to start
		"""

		command = self._checkInput(command)

		def execute() -> None:
			pressed = self.grab()

			if pressed:
				command.start()
			elif execute.pressedLast and not pressed:
				command.cancel()

			execute.pressedLast = pressed

		execute.pressedLast = self.grab()
		from wpilib.command import Scheduler

		Scheduler.getInstance().addButton(execute)

	def whenInactive(self, command) -> None:
		"""Starts the command when the trigger becomes inactive.

		:param command: the command to start
		"""

		command = self._checkInput(command)

		def execute() -> None:
			pressed = self.grab()

			if execute.pressedLast and not pressed:
				command.start()

			execute.pressedLast = pressed

		execute.pressedLast = self.grab()
		from wpilib.command import Scheduler

		Scheduler.getInstance().addButton(execute)

	def whileInactive(self, command) -> None:
		"""Constantly starts the command while the trigger becomes inactive.

		:param command: the command to start
		"""

		command = self._checkInput(command)

		def execute() -> None:
			pressed = self.grab()

			if not execute.pressedLast and not pressed:
				command.start()

			execute.pressedLast = pressed

		execute.pressedLast = self.grab()
		from wpilib.command import Scheduler

		Scheduler.getInstance().addButton(execute)

	def toggleWhenActive(self, command) -> None:
		"""Toggles a command when the trigger becomes active.

		:param command: the command to toggle
		"""

		command = self._checkInput(command)

		def execute() -> None:
			pressed = self.grab()

			if not execute.pressedLast and pressed:
				if command.isRunning():
					command.cancel()
				else:
					command.start()

			execute.pressedLast = pressed

		execute.pressedLast = self.grab()
		from wpilib.command import Scheduler

		Scheduler.getInstance().addButton(execute)

	def cancelWhenActive(self, command) -> None:
		"""Cancels a command when the trigger becomes active.

		:param command: the command to cancel
		"""

		command = self._checkInput(command)

		def execute() -> None:
			pressed = self.grab()

			if not execute.pressedLast and pressed:
				command.cancel()

			execute.pressedLast = pressed

		execute.pressedLast = self.grab()
		from wpilib.command import Scheduler

		Scheduler.getInstance().addButton(execute)

	def cancelWhenInactive(self, command) -> None:
		"""Cancels a command when the trigger becomes inactive.

		:param command: the command to cancel
		"""

		command = self._checkInput(command)

		def execute() -> None:
			pressed = self.grab()

			if execute.pressedLast and not pressed:
				command.cancel()

			execute.pressedLast = pressed

		execute.pressedLast = self.grab()
		from wpilib.command import Scheduler

		Scheduler.getInstance().addButton(execute)

	def _safeState(self) -> None:
		self.sendablePressed = False

	def _setPressed(self, value: bool) -> None:
		self.sendablePressed = value

	def initSendable(self, builder: SendableBuilder) -> None:
		builder.setSmartDashboardType("Button")
		builder.setSafeState(self._safeState)
		builder.addBooleanProperty("pressed", self.grab, self._setPressed)


	@staticmethod
	def _checkInput(command) -> command.Command:
		"""Checks if the input is a command or a function. Converts a function to a command.

		:param command: the command or function to check
		:returns: An executable Command
		"""
		if callable(command):
			return Command_Call(command)
		return command
