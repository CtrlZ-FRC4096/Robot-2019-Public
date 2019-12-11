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
import wpilib.timer
import wpilib.command
import ctre
import networktables

import const

class Cargo(wpilib.command.Subsystem):
	def __init__(self, robot):

		super().__init__('cargo')
		self.robot = robot

		self.manual_mode = False
		self.current_arm_speed = 0.0

		# set up motor controllers
		self.cargo_arm_motor = ctre.WPI_VictorSPX(const.CAN_MOTOR_CARGO_ARM)
		self.cargo_intake_motor = ctre.WPI_VictorSPX(const.CAN_MOTOR_CARGO_INTAKE)

		self.cargo_arm_motor.setInverted(False)
		self.cargo_intake_motor.setInverted(False)

		# set up solenoids
		self.cargo_brake = wpilib.DoubleSolenoid(
			const.CAN_PCM_A,
			const.PCM_CARGO_SOLENOID_BRAKE_1,
			const.PCM_CARGO_SOLENOID_BRAKE_2)

		# set up limit switches
		#self.limit_1 = wpilib.DigitalInput(const.DIO_CARGO_LIMIT_1)

		# set up potentiometer
		self.pot = wpilib.AnalogPotentiometer(
			const.AIN_CARGO_ARM_POT,
			const.CARGO_ARM_POT_MULTIPLIER,
			const.CARGO_ARM_POT_OFFSET
		)

		# set up arm PID
		self.arm_kP = 0.036
		self.arm_kI = 0		# is 0.0025 when doing continuous pid
		self.arm_kD = 0.03

		self.arm_pid = wpilib.PIDController(
			self.arm_kP,
			self.arm_kI,
			self.arm_kD,
			self.get_arm_pid_input,
			self.set_arm_pid_output,
		)

		self.arm_pid_output = 0
		self.arm_pid.setInputRange(0, 135)
		self.arm_pid.setOutputRange(-1, 1)
		self.arm_pid.setAbsoluteTolerance(2.5) # is 1 when doing continuous pid
		self.arm_pid.setContinuous(False)
		self.arm_pid.disable()

		self.climb_kP = 0.04
		self.climb_kI = 0.004
		self.climb_kD = 0.0

		self.climb_pid = wpilib.PIDController(
			self.climb_kP,
			self.climb_kI,
			self.climb_kD,
			self.get_arm_climb_pid_input,
			self.set_arm_climb_pid_output,
		)

		self.climb_pid_output = 0
		self.climb_pid.setInputRange(-5, 135)
		self.climb_pid.setOutputRange(-1, 1)
		#self.climb_pid.setAbsoluteTolerance(2.5)
		self.climb_pid.setContinuous(False)
		self.climb_pid.disable()

		# self.robot.nt_robot.putNumber("climbP", self.arm_kP)
		# self.robot.nt_robot.putNumber("climbI", self.arm_kI)
		# self.robot.nt_robot.putNumber("climbD", self.arm_kD)

		# Timer for running average on intake motor current
		self._current_samples = []
		self._last_current_value = 0.0
		self.current_timer = wpilib.Timer()
		self.current_timer.start()
		self.current_timer_delay = 0.1		# times per second

		self.stop_arm()

	def toggle_manual_mode(self):
		if self.manual_mode == False:
			self.manual_mode = True

		elif self.manual_mode == True:
			self.manual_mode = False

	def run_arm(self, speed):
		if self.manual_mode == False:
			if speed == 0:
				speed = 0
			if speed < 0:
				if self.get_pot() < 2:
					speed = 0
			if speed > 0:
				if self.get_pot() > 142:
					speed = 0

			if self.get_pot() < 15:
				speed = speed * 0.5

			self.cargo_arm_motor.set(speed)

		elif self.manual_mode == True:
			self.cargo_arm_motor.set(speed)

	def run_arm_unsafe(self, speed):
		self.current_arm_speed = speed
		self.cargo_arm_motor.set(speed)

	def stop_arm(self):
		self.run_arm(0)

	def run_intake(self, value):
		if self.get_pot() > 130:
			self.cargo_intake_motor.set(value*0.75)
		else:
			self.cargo_intake_motor.set(value)

	def stop_intake(self):
		self.run_intake(0)

	def current_threshold_hit(self):
		"""
		Calculate a running average of current values.
		"""

		new_current = self.robot.pdp.getCurrent(const.CARGO_PDP_ID)

		self._current_samples.append(new_current)

		if len(self._current_samples) > 10:
			self._current_samples.pop(0)

		# Calculate new running average
		new_avg = sum(self._current_samples) / len(self._current_samples)

		return new_avg > const.CARGO_INTAKE_THRESHOLD

	def set_brake(self):
		self.cargo_brake.set(2)

	def release_brake(self):
		self.cargo_brake.set(1)

	def get_pot(self):
		return self.pot.get()

	def get_arm_pid_input(self):
		return self.pot.get()

	def update_pid(self, p = None, i = None, d = None):
		# Updates the PID values
		if p:
			self.arm_kP = p
		if i:
			self.arm_kI = i
		if d:
			self.arm_kD = d

		self.arm_pid.setPID(self.arm_kP, self.arm_kI, self.arm_kD)

	def set_arm_pid_output(self, output):

		# Make sure we're outputing at least enough to move the cargo arm at all
		if output < 0:
			output = output - const.CARGO_MIN
		else:
			output = output + const.CARGO_MIN

		output = output * (math.cos(math.radians(self.get_pot())) + 5) / 6

		if self.arm_pid.onTarget():
			output = 0


		self.arm_pid_output = output

		self.run_arm_unsafe(self.arm_pid_output)


	# ARM WHEN CLIMBING PID METHODS

	def get_arm_climb_pid_input(self):
		return self.robot.cargo.get_pot()

	def set_arm_climb_pid_output(self, output):
		holding_power = .07
		output -= holding_power

		self.arm_pid_output = output
		print("cargo output: " + str(output))
		self.run_arm_unsafe(self.arm_pid_output)

	def update_climb_pid(self, p = None, i = None, d = None):
		# Updates the PID values
		if p:
			self.climb_kP = p
		if i:
			self.climb_kI = i
		if d:
			self.climb_kD = d

		self.climb_pid.setPID(self.climb_kP, self.climb_kI, self.climb_kD)

	def log(self):
		self.robot.nt_robot.putNumber("AnalogPot value", round(self.pot.get(), 2))
		self.robot.nt_robot.putNumber("Cargo Arm Current", round(self.robot.pdp.getCurrent(const.CARGO_PDP_ID), 2))
		self.robot.nt_robot.putNumber("Cargo Arm Speed", round(self.cargo_arm_motor.getMotorOutputPercent(), 2))
		self.robot.nt_robot.putNumber("Cargo Arm Voltage", round(self.cargo_arm_motor.getMotorOutputVoltage(), 2))

		#lp = self.robot.nt_robot.getNumber("climbP", 0)
		#li = self.robot.nt_robot.getNumber("climbI", 0)
		#ld = self.robot.nt_robot.getNumber("climbD", 0)

		#self.update_pid(lp, li, ld)
		# self.arm_kP = lp
		# self.arm_kI = li
		# self.arm_kD = ld
		# self.arm_pid.setPID(lp, li, ld)
		#print("zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz")

		# if(lp != self.arm_kP or li != self.arm_kI or ld != self.arm_kD):
		# 	if(lp != -1111 and li != -1111 and ld != -1111):
		# 		self.update_pid(lp, li, ld)