"""
Ctrl-Z FRC Team 4096
FIRST Robotics Competition 2019
Code for robot "------"
contact@team4096.org
"""
import math
import time
import sys

import wpilib
import wpilib.command
import networktables

import const
from enum import Enum

class Arduino(wpilib.command.Subsystem):

	class Led_State(Enum):
		DEFAULT = 'a'
		HAVE_CARGO = 'b'
		END_GAME = 'c'

	def __init__(self, robot):
		super().__init__('arduino')
		self.table = networktables.NetworkTables.getTable("arduino")
		self.i2c = wpilib.I2C(wpilib.I2C.Port.kOnboard, const.ARDUINO_DEVICE_ADDRESS)
		self.robot = robot

		self.led_state = self.Led_State.DEFAULT
		self.set_led_state(self.Led_State.DEFAULT)

		# Used in log below, to print/log line sensor value only when it changes
		self._last_line_value = -1

		# Current line value
		self.current_line_value = -1


	def periodic(self):
		# if haveCargo():
		# 	self.set_led_state(self.Led_State.HAVE_CARGO)
		#else
		if const.LEDS_ENABLED and self.robot.driverstation.isOperatorControl() and self.robot.driverstation.getMatchTime() < 30:
			self.set_led_state(self.Led_State.END_GAME)


	def get_line_sensor_value(self):
		try:
			line_data = self.i2c.readOnly(1)
		except:
			#print('ERROR reading from Arduino I2C')
			return None

		if line_data[0] == 127:
			# Sensor doesn't see a line
			return None

		# It sees a line
		return line_data[0]


	def set_led_state(self, new_state: Led_State):
		#return #for now
		if self.led_state != new_state:
			self.led_state = new_state
			try:
				self.i2c.transaction([ord(new_state.value)], 1)
			except:
				print('LED set_led_state - i2c transaction failed, skipping')
				pass



	def log(self):
		pass
		# line_value = self.get_line_sensor_value()

		# if line_value is None:
		# 	line_value = -1

		# # If value has changed, log/print it.
		# if line_value != self._last_line_value:
		# 	print('Line Sensor Value = {0}'.format(line_value))
		# 	self._last_line_value = line_value
		# 	self.current_line_value = line_value

		# # Put number & red/green indicator on Shuffleboard
		# self.robot.nt_robot.putNumber('Line Sensor', line_value)
		# if line_value == -1:
		# 	self.robot.nt_robot.putBoolean('Line Sensor Active', False)
		# else:
		# 	self.robot.nt_robot.putBoolean('Line Sensor Active', True)


