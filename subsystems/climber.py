"""
Ctrl-Z FRC Team 4096
FIRST Robotics Competition 2019
Code for robot "Saba-Z"
contact@team4096.org
"""

import math
import time
import sys

import wpilib
import wpilib.command
import ctre
import networktables
import numpy

import const

class Climber(wpilib.command.Subsystem):

	def __init__(self, robot):

		super().__init__('climber')
		self.robot = robot

		# Default max value for climber encoders
		self.front_encoder_min = -530225
		self.front_encoder_max = 0

		# set up motor controllers
		self.climber_motor_1 = ctre.WPI_TalonSRX(const.CAN_MOTOR_CLIMBER_1)
		self.climber_motor_2 = ctre.WPI_VictorSPX(const.CAN_MOTOR_CLIMBER_2)
		self.climber_motor_drive = ctre.WPI_TalonSRX(const.CAN_MOTOR_CLIMBER_DRIVE)

		self.climber_back_motor = ctre.WPI_VictorSPX(const.CAN_MOTOR_BACK_CLIMBER)

		self.climber_motor_1.setInverted(False)
		self.climber_motor_2.setInverted(False)
		self.climber_motor_drive.setInverted(False)

		# PROBABLY NEEDS TO CHANGE
		self.climber_back_motor.setInverted(False)

		self.climber_kP = 0.02
		self.climber_kI = 0.0
		self.climber_kD = 0.0

		#self.climber_motor_1.configOpenLoopRamp(1)
		self.climber_motor_2.follow(self.climber_motor_1)

		self.climber_pid = wpilib.PIDController(
		 	self.climber_kP,
		 	self.climber_kI,
		 	self.climber_kD,
		 	self.get_climber_pid_input,
			self.set_climber_pid_output,
		)

		# add methods for range, continuous, tolerance etc.
		self.climber_pid.reset()
		self.climber_pid.setInputRange(-90, 90)
		self.climber_pid.setOutputRange(-1, 1)
		self.climber_pid.setContinuous(False)
		self.climber_pid.setAbsoluteTolerance(0)

		self.stop_climber()

		# set up limit switches
		self.front_top_limit = wpilib.DigitalInput(const.DIO_CLIMBER_FRONT_TOP_LIMIT)
		self.front_bottom_limit = wpilib.DigitalInput(const.DIO_CLIMBER_FRONT_BOTTOM_LIMIT)
		self.stilts_hit_platform_limit = wpilib.DigitalInput(const.DIO_CLIMBER_STILTS_HIT_PLATFORM_LIMIT)

		self.back_top_limit = wpilib.DigitalInput(const.DIO_CLIMBER_BACK_TOP_LIMIT)
		self.back_bottom_limit = wpilib.DigitalInput(const.DIO_CLIMBER_BACK_BOTTOM_LIMIT)

	# FRONT
	def run_climber(self, value):
		if (abs(value) < .03):
			self.stop_climber()
			return
		self.climber_motor_1.set(value)
		#self.climber_motor_2.set(value)

	def stop_climber(self):
		self.climber_motor_1.stopMotor()
		#self.climber_motor_2.set(0)

	# BACK
	def run_back_climber(self, value):
		self.climber_back_motor.set(value)

	def stop_back_climber(self):
		self.climber_back_motor.stopMotor()

	# OMNI WHEELS
	def run_climber_drive(self, value):
		self.climber_motor_drive.set(value)

	def stop_climber_drive(self):
		self.climber_motor_drive.set(0)

	# LIMIT SWITCHES
	def front_top_hit(self):
		return not self.front_top_limit.get()

	def front_bottom_hit(self):
		return not self.front_bottom_limit.get()

	def back_top_hit(self):
		return not self.back_top_limit.get()

	def back_bottom_hit(self):
		return not self.back_bottom_limit.get()

	def stilts_hit_platform(self):
		return not self.stilts_hit_platform_limit.get()

	# OTHER5
	def tilt_degree(self):
		y_accel = self.robot.get_average_accel('Y')
		y_accel = y_accel / const.MAX_ACCEL
		y_accel = min(y_accel, 1)
		y_accel = max(-1, y_accel)
		return math.degrees(math.asin(y_accel))

	def percentage_up_front(self):
		return self.climber_motor_1.getSelectedSensorPosition() / self.front_encoder_min

	def get_climber_pid_input(self):
		return self.tilt_degree()

	def set_climber_pid_output(self, output):
		front_speed = min(max(0.8 + output, 0), 1)

		self.run_climber(front_speed)

	def get_climb_level_arm_value(self, stilt_value):
		"""
		For a given stilt encoder value get the interpolated arm degrees value
		from our lookup table for the level 3 climb.
		"""
		# print("stiltval" + str(stilt_value))
		arm_val = numpy.interp(
			stilt_value,
			const.CLIMB_LEVEL_STILT_VALUES,
			const.CLIMB_LEVEL_ARM_VALUES
		)
		# print("armval" + str(arm_val))
		return arm_val

	def get_climb_level_arm_value_level_2(self, stilt_value):
		"""
		For a given stilt encoder value get the interpolated arm degrees value
		from our lookup table for the level 2 climb.
		"""
		# print("stiltval" + str(stilt_value))
		arm_val = numpy.interp(
			stilt_value,
			const.CLIMB_LEVEL_STILT_VALUES_LEVEL_2,
			const.CLIMB_LEVEL_ARM_VALUES_LEVEL_2
		)
		# print("armval" + str(arm_val))
		return arm_val

	def log( self ):

		self.robot.nt_robot.putNumber( 'Front Climber Encoder', round(self.climber_motor_1.getSelectedSensorPosition(), 2))

		self.robot.nt_robot.putNumber( 'Y Axis Accel: ', self.robot.get_average_accel('Y'))
		self.robot.nt_robot.putNumber( 'Y Axis Degree: ', self.tilt_degree())

		self.robot.nt_robot.putBoolean( 'Platform Hit: ', self.stilts_hit_platform())

		self.robot.nt_robot.putBoolean( 'Front Top Limit Hit:', not self.front_top_limit.get() )
		self.robot.nt_robot.putBoolean( 'Front Bottom Limit Hit:', not self.front_bottom_limit.get() )