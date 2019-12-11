"""
Ctrl-Z FRC Team 4096
FIRST Robotics Competition 2019
Code for robot "Saba-Z"
contact@team4096.org
"""

from wpilib.command.commandgroup import Command

import subsystems.cargo

import const
import ctre

import math
import sys
import time

import wpilib
import networktables

class Test_Cargo_Brake(Command):
	def __init__(self, robot, position):
		super().__init__()
		self.robot = robot
		self.position = position

		self.requires(self.robot.cargo)
		self.setInterruptible(True)

	def initialize(self):
		if self.position == True:
			print('TRUE!')
			self.robot.cargo.set_brake()
		elif self.position == False:
			print('FALSE!')
			self.robot.cargo.release_brake()

	def execute(self):
		pass

	def isFinished(self):
		return True

class Run_Cargo_Arm_Unsafe(Command):
	def __init__(self, robot, speed = 0):
		super().__init__()

		self.robot = robot
		self.speed = speed

		self.requires(self.robot.cargo)
		self.setInterruptible(True)

	def initialize(self):
		self.robot.cargo.release_brake()

	def execute(self):
		if callable(self.speed):
			speed = self.speed()

		speed = math.copysign(speed * speed, speed)

		if speed == 0:
			self.robot.cargo.stop_arm()
			self.robot.cargo.set_brake()
		else:
			self.robot.cargo.release_brake()
			self.robot.cargo.run_arm_unsafe(speed)

	def isFinished(self):
		return False

	def end(self):
		self.robot.cargo.stop_arm()
		self.robot.cargo.set_brake()

	def isInterrupted(self):
		self.end()


class Run_Cargo_Arm(Command):
	def __init__(self, robot, speed = 0):

		super().__init__()

		self.robot = robot
		self.speed = speed

		self.requires(self.robot.cargo)
		self.setInterruptible(True)

	def initialize(self):
		self.robot.cargo.release_brake()

	def execute(self):
		if callable(self.speed):
			speed = self.speed()

			if speed < 0:
				speed = speed * -speed
			else:
				speed = speed * speed

		if speed == 0:
			self.robot.cargo.stop_arm()
			self.robot.cargo.set_brake()
		else:
			self.robot.cargo.release_brake()
			self.robot.cargo.run_arm(speed)

	def isFinished(self):
		return False

	def end(self):
		self.robot.cargo.stop_arm()
		self.robot.cargo.set_brake()

	def isInterrupted(self):
		self.end()

class Run_Cargo_Arm_Distance(Command):
	def __init__ (self, robot, setpoint, max_speed = None):
		super().__init__()

		self.robot = robot
		self.setpoint = setpoint

		self.setInterruptible(True)

		self.requires(self.robot.cargo)
		self.setTimeout(5)

	def initialize(self):
		if self.robot.cargo.manual_mode == True:
			self.robot.cargo.stop_arm()

		else:
			self.robot.cargo.release_brake()
			self.robot.cargo.arm_pid.reset()

			print('Cargo Arm Setpoint:', self.setpoint)

			self.robot.cargo.arm_pid.setSetpoint(self.setpoint)
			self.robot.cargo.arm_pid.enable()

	def execute(self):
		if self.robot.cargo.manual_mode == True:
			self.robot.cargo.stop_arm()

		else:
			self.robot.cargo.run_arm(self.robot.cargo.arm_pid_output)

	def isFinished(self):
		if self.robot.cargo.manual_mode == True:
		 	return True

		else:
			on_target = self.robot.cargo.arm_pid.onTarget()
			timed_out = self.isTimedOut()

		if timed_out:
		 	print('Cargo Arm Timed out!')
		if on_target:
			self.distance_traveled = self.robot.cargo.get_arm_pid_input()
			print('Cargo Arm On Target! {0:.2f}'.format(self.distance_traveled))

		finished = on_target

		return finished

	def end(self):
		if self.robot.cargo.manual_mode == True:
			self.robot.cargo.stop_arm()

		else:
			print("Ending Cargo Arm Movement")
			self.robot.cargo.arm_pid.reset()
			self.robot.cargo.stop_arm()
			self.robot.cargo.set_brake()

	def interrupted(self):
		self.end()

class Run_Cargo_Arm_Distance_Continuous(Command):
	def __init__ (self, robot, setpoint, max_speed = None):
		super().__init__()

		self.robot = robot
		self.setpoint = setpoint

		self.setInterruptible(True)

		self.requires(self.robot.cargo)

	def initialize(self):
		if self.robot.cargo.manual_mode == True:
			print("STOP ARM CONTINUOUS")
			self.robot.cargo.stop_arm()

		else:
			self.robot.cargo.release_brake()
			self.robot.cargo.arm_pid.reset()

			print('Cargo Arm Setpoint:', self.setpoint)

			self.robot.cargo.arm_pid.setSetpoint(self.setpoint)
			self.robot.cargo.arm_pid.enable()

	def execute(self):
		if self.robot.cargo.manual_mode == True:
			print("MANUAL MODE STOP ARM")
			self.robot.cargo.stop_arm()

	def isFinished(self):
		return False

	def end(self):
		if self.robot.cargo.manual_mode == True:
			self.robot.cargo.stop_arm()

		else:
			print("Ending Cargo Arm Movement")
			self.robot.cargo.arm_pid.reset()
			self.robot.cargo.stop_arm()
			self.robot.cargo.set_brake()

	def interrupted(self):
		self.end()


class Stop_Cargo_Arm(Command):
	def __init__(self, robot):

		super().__init__()

		self.robot = robot

		self.requires(self.robot.cargo)
		self.setInterruptible(True)

	def initialize(self):
		if self.robot.cargo.manual_mode:
			self.robot.cargo.stop_arm()
			self.robot.cargo.set_brake()
		#else:
			#self.robot.scheduler.add(Run_Cargo_Arm_Distance_Continuous(self.robot, self.robot.cargo.get_pot()))

	def execute(self):
		pass

	def isFinished(self):
		return True

class Run_Cargo_Intake(Command):

	def __init__(self, robot, speed):

		super().__init__()
		self.robot = robot
		self.speed = speed

		self.requires(self.robot.cargo)
		self.setInterruptible(True)

	def execute(self):
		self.robot.cargo.run_intake(self.speed)

	def isFinished(self):
		return False

class Run_Cargo_Intake_Inward(Run_Cargo_Intake):
	def isFinished(self):
		# if intaking a ball, and current threshold is hit, stop command
		if self.robot.cargo.current_threshold_hit() == True:
			if const.LEDS_ENABLED:
				self.robot.arduino.set_led_state(self.robot.arduino.Led_State.HAVE_CARGO)

			return True

class Run_Cargo_Intake_Outward(Run_Cargo_Intake):
	def execute(self):
		self.robot.cargo.run_intake(-self.speed)

class Stop_Cargo_Intake(Command):
	def __init__(self, robot):

		super().__init__()

		self.robot = robot

		self.requires(self.robot.cargo)
		self.setInterruptible(True)

	def execute(self):
		self.robot.cargo.stop_intake()

	def isFinished(self):
		return True
