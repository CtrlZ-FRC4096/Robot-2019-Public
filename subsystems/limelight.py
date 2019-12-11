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

class Limelight(wpilib.command.Subsystem):
	def __init__(self, robot):
		super().__init__('limelight')

		self.robot = robot

		self.driver_camera_mode = const.LIMELIGHT_DRIVER_CAMERA_MODE_DEFAULT
		self.table_bottom = networktables.NetworkTables.getTable("limelight-bottom")
		# self.table_top = networktables.NetworkTables.getTable("limelight-top")


	def set_startup_modes(self):
		# Bottom/Line-Finder Limelight
		self.table_bottom.putNumber('camMode', 0)								# 0 = vision processing
		self.table_bottom.putNumber('ledMode', const.LIMELIGHT_LED_MODE)

		# Top/Front-facing Limelight
		self.table_bottom.putNumber('stream', const.LIMELIGHT_STREAM_MODE)		# 0 = side-by-side, 1 = PIP Main, 2 = PIP Secondary
		# self.table_top.putNumber('ledMode', const.LIMELIGHT_LED_MODE)
		self.set_driver_mode(const.LIMELIGHT_DRIVER_CAMERA_MODE_DEFAULT)


	def get_angle_to_target(self):
		return self.table_bottom.getNumber( 'tx', None )

	def is_line_visible(self):
		# See if there's any target in view
		#print(self.table_bottom.getNumber('tv', 0) == 1)
		return self.table_bottom.getNumber('tv', 0) == 1

	def get_line_position(self):
		if not self.is_line_visible( ):
			return None

		# See if there's raw corners, and there's the expected number of them
		corners = self.table_bottom.getNumberArray('tcornx', [ ])
		# print('corners = {0}'.format(corners))

		if corners:
			current_position = sum(corners) / len(corners)
		else:
			return None

		# print( 'LL line position = {0:.2f}'.format( current_position ))

		pixel_min = const.LIMELIGHT_CARRIAGE_PIXEL_MIN
		pixel_max = const.LIMELIGHT_CARRIAGE_PIXEL_MAX

		if current_position < pixel_min or current_position > pixel_max:
			return None

		return (current_position - pixel_min) * const.CARRIAGE_POS_MAX / (pixel_max - pixel_min)


	def set_driver_mode(self, mode):
		self.driver_camera_mode = mode
		self.table_bottom.putNumber('camMode', mode)


	def toggle_driver_mode(self):
		if self.driver_camera_mode == const.LIMELIGHT_DRIVER_CAMERA_MODE_ENABLED:
			self.set_driver_mode(const.LIMELIGHT_DRIVER_CAMERA_MODE_DISABLED)
		else:
			self.set_driver_mode(const.LIMELIGHT_DRIVER_CAMERA_MODE_ENABLED)


	def log(self):
		# Put number & red/green indicator on Shuffleboard
		if not self.is_line_visible():
			self.robot.nt_robot.putBoolean('Line Sensor Active', False)
			self.robot.nt_robot.putNumber('Line Sensor', -1)
			return

		self.robot.nt_robot.putBoolean('Line Sensor Active', True)

		line_value = self.get_line_position()

		if line_value is None:
			line_value = -1

		self.robot.nt_robot.putNumber('Line Sensor', line_value)
