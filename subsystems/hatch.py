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

import const

class Hatch(wpilib.command.Subsystem):

	def __init__(self, robot):

		super().__init__('hatch')
		self.robot = robot

		# set up motor controllers
		self.carriage_motor = ctre.WPI_VictorSPX(const.CAN_MOTOR_HATCH_CARRIAGE)
		self.carriage_motor.setInverted(True)

		# set up string potentiometer
		self.string_pot = wpilib.AnalogPotentiometer(const.AIN_HATCH_STRING_POT, const.HATCH_STRING_POT_MULTIPLIER,
			const.HATCH_STRING_POT_OFFSET)

		# set up solenoids
		self.beak_piston = wpilib.DoubleSolenoid(const.CAN_PCM_A, const.PCM_HATCH_SOLENOID_BEAK_1,
			const.PCM_HATCH_SOLENOID_BEAK_2)

		self.carriage_piston = wpilib.DoubleSolenoid(const.CAN_PCM_A, const.PCM_HATCH_SOLENOID_CARRIAGE_1,
			const.PCM_HATCH_SOLENOID_CARRIAGE_2)

		# self.line_sensor_piston_1 = wpilib.DoubleSolenoid(const.CAN_PCM_B, const.PCM_LIGHT_SENSOR_SOLENOID_1,
		#	const.PCM_LIGHT_SENSOR_SOLENOID_2)


		# set up carriage PID - values need to be tuned
		self.carriage_kP = 3/11
		self.carriage_kI = 0.007
		self.carriage_kD = 0.0

		self.carriage_pid = wpilib.PIDController(
			self.carriage_kP,
			self.carriage_kI,
			self.carriage_kD,
			self.get_carriage_pid_input,
			self.set_carriage_pid_output,
		)

		self.carriage_pid_output = 0
		self.carriage_pid.setInputRange(const.CARRIAGE_POS_MIN, const.CARRIAGE_POS_MAX)
		self.carriage_pid.setOutputRange(-1, 1)
		self.carriage_pid.setAbsoluteTolerance(.25)
		self.carriage_pid.setContinuous(False)
		self.carriage_pid.disable()


	def move_carriage(self, speed):
		#if pot isnt working properly add safety bypass to be able to continue using carriage strafe

		if speed == 0:
			speed = 0
		if speed < 0:
			if self.get_pot() < 1:
				speed = 0
		if speed > 0:
			if self.get_pot() > 11:
				speed = 0

		self.carriage_motor.set(speed)

	def stop_carriage(self):
		self.move_carriage(0)

	def open_beak(self):
		self.beak_piston.set(1)

	def close_beak(self):
		self.beak_piston.set(2)

	def depressurize_beak(self):
		self.beak_piston.set(0)

	def push_out_carriage(self):
		self.carriage_piston.set(1)

	def pull_in_carriage(self):
		self.carriage_piston.set(2)

	"""
	def light_sensor_down(self):
		self.line_sensor_piston_1.set(2)

	def light_sensor_up(self):
		self.line_sensor_piston_1.set(1)
	"""

	def get_hatch_target_position_limelight(self):
		"""
		Takes the limelight value (0 - 320) and converts it into inches
		"""
		return self.robot.limelight.get_line_position()

	def get_hatch_target_position_light_sensors(self):
		"""
		Takes the Arduino line sensor value (currently 0-23) and converts it
		into inches, used to position the hatch carriage
		"""
		# line_position = self.robot.arduino.get_line_sensor_value()
		line_position = self.robot.arduino.current_line_value

		if line_position is None:
			return None

		# Sees a line, so calculate position in inches for carriage
		pos_percent = line_position / const.ARDUINO_LINE_SENSOR_MAX_VALUE
		inches = 11 * pos_percent

		return inches

	def get_pot(self):
		return self.string_pot.get()

	def get_carriage_pid_input(self):
		return self.string_pot.get()

	def set_carriage_pid_output(self, output):
		self.carriage_pid_output = output

	def log(self):
		self.robot.nt_robot.putString( 'Hatch String Pot', '{0:.2f}'.format( self.string_pot.get()))

