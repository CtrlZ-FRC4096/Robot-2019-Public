"""
Ctrl-Z FRC Team 4096
FIRST Robotics Competition 2019
Code for robot "Saba-Z"
contact@team4096.org
"""

from commands.command_call import Command_Call

import ctre
from wpilib.command.command import Command
from wpilib.command.commandgroup import CommandGroup
from wpilib.command import WaitCommand
import wpilib
from wpilib import Timer
from commands import cargo
from commands import drivetrain
from commands import hatch

import const
import subsystems.climber

"""
TO DO:
- Step 1 with PID controller to keep position
of front and back to be exactly the same
- Ultrasonic sensors for Steps 2 & 4
"""

"""
CLIMB STEPS:
1. Run both axles downward so that the robot raises
2. Drive forward so that the first two wheels of the real drivetrain
	are on the platform
3. Run front axles upward so that they are all the way up
4. Drive forward until the center of mass is on the platform
	(use actual drivetrain)
5. Run back axle upward slightly
"""

class Run_Front_Stilts(Command):

	def __init__(self, robot, speed, direction):
		super().__init__()

		self.robot = robot
		self.speed = speed
		self.direction = direction

		self.requires(self.robot.climber)
		self.setInterruptible(True)

	def execute(self):
		# print("EXECUTING RUN_FRONT_STILTS")
		if self.direction == 'Up':
			# print("RUN STILTS UP")
			if self.robot.climber.percentage_up_front() < 0.2:
				self.robot.climber.run_climber(-self.speed*0.5)
				#self.robot.climber.run_climber(-self.speed)
				# print('slowing down up')
			else:
				self.robot.climber.run_climber(-self.speed)


		elif self.direction == 'Down':
			# print("RUN STILS DOWN")
			if self.robot.climber.percentage_up_front() > 0.8:
				self.robot.climber.run_climber(self.speed*0.5)
				#self.robot.climber.run_climber(self.speed)
				# print ('slowing down down')
			else:
				self.robot.climber.run_climber(self.speed)
		else:
			self.robot.climber.stop_climber()

	def isFinished(self):
		if self.direction == 'Up':
			return self.robot.climber.front_bottom_hit() #or self.robot.climber.climber_motor_1.getSelectedSensorPosition() > const.CLIMB_STILT_UP_STOP_VALUE
		elif self.direction == 'Down':
			return self.robot.climber.front_top_hit()
		else:
			return True

	def end(self):
		self.robot.climber.stop_climber()

class Run_Front_Stilts_Level_2(Command):

	def __init__(self, robot, speed, direction):
		super().__init__()

		self.robot = robot
		self.speed = speed
		self.direction = direction

		self.requires(self.robot.climber)
		self.setInterruptible(True)

	def execute(self):
		# print("EXECUTING RUN_FRONT_STILTS")
		if self.direction == 'Up':
			# print("RUN STILTS UP")
			if self.robot.climber.percentage_up_front() < 0.2:
				self.robot.climber.run_climber(-self.speed*0.3)
				#self.robot.climber.run_climber(-self.speed)
				# print('slowing down up')
			else:
				self.robot.climber.run_climber(-self.speed)


		elif self.direction == 'Down':
			# print("RUN STILS DOWN")
			if self.robot.climber.percentage_up_front() > 0.8:
				self.robot.climber.run_climber(self.speed*0.3)
				#self.robot.climber.run_climber(self.speed)
				# print ('slowing down down')
			else:
				self.robot.climber.run_climber(self.speed)
		else:
			self.robot.climber.stop_climber()

	def isFinished(self):
		if self.direction == 'Up':
			return self.robot.climber.front_bottom_hit() #or self.robot.climber.climber_motor_1.getSelectedSensorPosition() > const.CLIMB_STILT_UP_STOP_VALUE
		elif self.direction == 'Down':
			return self.robot.climber.front_top_hit() or self.robot.climber.percentage_up_front() > const.CLIMB_LEVEL_STILT_VALUES_LEVEL_2[1]
		else:
			return True

	def end(self):
		self.robot.climber.stop_climber()

class Run_Back_Stilts(Command):
	def __init__(self, robot, speed, direction):
		super().__init__()

		self.robot = robot
		self.speed = speed
		self.direction = direction

		self.requires(self.robot.climber)
		self.setInterruptible(True)

	def execute(self):
		if self.direction == 'Up':
			self.robot.climber.run_back_climber(-self.speed)
		elif self.direction == 'Down':
			self.robot.climber.run_back_climber(self.speed)
		else:
			self.robot.climber.stop_back_climber

	def isFinished(self):
		if self.direction == 'Up':
			return self.robot.climber.back_bottom_hit()
		elif self.direction == 'Down':
			return self.robot.climber.back_top_hit()
		else:
			return True

	def end(self):
		self.robot.climber.stop_back_climber()

class Run_Both_Stilts_Down_With_Accel(Command):
	def __init__(self, robot):
		super().__init__()
		self.robot = robot

		self.requires(self.robot.climber)
		self.setInterruptible(True)

	def initalize(self):
		pass

	def execute(self):
		kP = 0.025
		deg = self.robot.climber.tilt_degree()
		output = kP*deg

		self.front_speed = min(max(0.5 - output, 0), 1)
		self.back_speed = min(max(0.8 + output, 0), 1)

		if not self.robot.climber.front_top_hit():
			self.robot.climber.run_climber(self.front_speed)
		else:
			self.robot.climber.stop_climber()

		if not self.robot.climber.back_top_hit():
			self.robot.climber.run_back_climber(self.back_speed)
		else:
			self.robot.climber.stop_back_climber()

	def isFinished(self):
		if self.robot.climber.back_top_hit() and self.robot.climber.front_top_hit():
			return True

	def end(self):
		self.robot.climber.stop_climber()
		self.robot.climber.stop_back_climber()

	def isInterrupted(self):
		self.end()

class Trigger_Hit(Command):
	def __init__(self, robot):
		super().__init__()

		self.robot = robot
		self.setInterruptible(True)

	def isFinished(self):
		return self.robot.climber.stilts_hit_platform()


class Climber_Down_With_Accel(Command):
	def __init__(self,robot):
		super().__init__()

		self.robot = robot
		self.requires(self.robot.climber)
		self.setInterruptible(True)

	def initialize(self):
		pass

	def execute(self):
		kP = 0.02
		deg = self.robot.climber.tilt_degree()
		output = kP*deg

		self.front_speed = min(max(0.7 - output, 0), 1)

		if not self.robot.climber.front_top_hit():
			self.robot.climber.run_climber(self.front_speed)
		else:
			self.robot.climber.stop_climber()

	def isFinished(self):
		self.robot.climber.front_top_hit()

	def end(self):
		self.robot.climber.stop_climber()

class Climber_Drive(Command):
	def __init__(self, robot, speed):
		super().__init__()

		self.robot = robot
		self.speed = speed
		self.setInterruptible(True)

	def initialize(self):
		self.robot.climber.run_climber_drive(self.speed)

	def isFinished(self):
		return False

	def end(self):
		self.robot.climber.stop_climber_drive()

class Stop_Climber_Drive(Command):
	def __init__(self, robot):
		super().__init__()

		self.robot = robot
		self.setInterruptible(True)

	def initialize(self):
		pass

	def isFinished(self):
		return True

	def end(self):
		self.robot.climber.stop_climber_drive()

class Stop_Stilts(Command):
	def __init__(self, robot):
		super().__init__()

		self.robot = robot

		self.requires(self.robot.climber)
		self.setInterruptible(True)

	def initialize(self):
		self.robot.climber.stop_climber()

	def isFinished(self):
		return True

class Stop_Back_Stilts(Command):
	def __init__(self, robot):
		super().__init__()

		self.robot = robot

		self.requires(self.robot.climber)
		self.setInterruptible(True)

	def initialize(self):
		self.robot.climber.stop_back_climber()

	def isFinished(self):
		return True

class Cargo_Arm_Follows_Stilts(Command):
	def __init__(self, robot):
		super().__init__()

		self.robot = robot

		self.requires(self.robot.cargo)
		self.setInterruptible(True)

	def initialize(self):

		self.uh_oh_sensors = False
		self.robot.cargo.release_brake()

		self.robot.cargo.climb_pid.reset()
		self.robot.cargo.climb_pid.setSetpoint(const.CLIMB_LEVEL_ARM_VALUES[0])
		self.robot.cargo.climb_pid.enable()

	def execute(self):
		# tilt = self.robot.climber.tilt_degree()
		# if abs(tilt) > 5:
		# 	self.uh_oh_sensors = True
		# if self.uh_oh_sensors:
		# 	self.robot.cargo.climb_pid.disable()
		# 	kP = .02
		# 	min_power = .05
		# 	self.robot.cargo.run_arm_unsafe(kP * tilt - min_power)
		# 	return

		climber_pos = self.robot.climber.percentage_up_front()
		arm_pos = self.robot.climber.get_climb_level_arm_value(climber_pos)

		# arm_pos = 0.0000829396*climber_pos + 47.0503

		self.robot.cargo.climb_pid.setSetpoint(arm_pos)
		# print("setpoint: " + str(arm_pos))

	def isFinished(self):
		return False

	def end(self):
		self.robot.cargo.climb_pid.disable()
		self.robot.cargo.stop_arm()
		self.robot.cargo.set_brake()

class Climb_Stilts_And_Arm(CommandGroup):
	def __init__(self, robot):
		super().__init__()
		self.robot = robot
		self.setInterruptible(False)

		self.addParallel(hatch.Auto_Strafe_Carriage(self.robot, 5.5))
		self.addSequential(cargo.Run_Cargo_Arm_Distance(self.robot, const.CLIMB_LEVEL_ARM_VALUES[0] + 3))

		self.addParallel(drivetrain.Drive_Distance_Time(self.robot, 10, -0.4))
		self.addParallel(Cargo_Arm_Follows_Stilts(self.robot))
		self.addParallel(Run_Front_Stilts(self.robot, 1.0, 'Down'))
		self.addParallel(Climber_Drive(self.robot, 0.4))
		self.addSequential(Trigger_Hit(self.robot))

		self.addParallel(Run_Front_Stilts(self.robot, 1.0, 'Up'))
		self.addSequential(cargo.Run_Cargo_Arm_Distance(self.robot, 120))
		#self.addSequential(drivetrain.Drive_Distance_Time(self.robot, 6.5, -0.4))

class Cargo_Arm_Follows_Stilts_Level_2(Command):
	def __init__(self, robot):
		super().__init__()

		self.robot = robot

		self.requires(self.robot.cargo)
		self.setInterruptible(True)

	def initialize(self):

		self.uh_oh_sensors = False
		self.robot.cargo.release_brake()

		self.robot.cargo.climb_pid.reset()
		self.robot.cargo.climb_pid.setSetpoint(const.CLIMB_LEVEL_ARM_VALUES_LEVEL_2[0])
		self.robot.cargo.climb_pid.enable()

	def execute(self):
		# tilt = self.robot.climber.tilt_degree()
		# if abs(tilt) > 5:
		# 	self.uh_oh_sensors = True
		# if self.uh_oh_sensors:
		# 	self.robot.cargo.climb_pid.disable()
		# 	kP = .02
		# 	min_power = .05
		# 	self.robot.cargo.run_arm_unsafe(kP * tilt - min_power)
		# 	return

		climber_pos = self.robot.climber.percentage_up_front()
		arm_pos = self.robot.climber.get_climb_level_arm_value_level_2(climber_pos)

		# arm_pos = 0.0000829396*climber_pos + 47.0503

		self.robot.cargo.climb_pid.setSetpoint(arm_pos)
		# print("setpoint: " + str(arm_pos))

	def isFinished(self):
		return False

	def end(self):
		self.robot.cargo.climb_pid.disable()
		self.robot.cargo.stop_arm()
		self.robot.cargo.set_brake()

class Climb_Stilts_And_Arm_Level_2(CommandGroup):
	def __init__(self, robot):
		super().__init__()
		self.robot = robot
		self.setInterruptible(False)

		self.addParallel(hatch.Auto_Strafe_Carriage(self.robot, 5.5))
		self.addSequential(cargo.Run_Cargo_Arm_Distance(self.robot, const.CLIMB_LEVEL_ARM_VALUES_LEVEL_2[0] + 3))
		# self.addSequential(drivetrain.Drive_Distance_Time(self.robot, 10, -0.4))

		self.addParallel(Cargo_Arm_Follows_Stilts_Level_2(self.robot))
		self.addParallel(Run_Front_Stilts_Level_2(self.robot, 1.0, 'Down'))
		self.addParallel(Climber_Drive(self.robot, 0.4))
		self.addParallel(drivetrain.Drive_Distance_Time(self.robot, 10, -0.4))
		self.addSequential(Trigger_Hit(self.robot))

		self.addParallel(Run_Front_Stilts(self.robot, 1.0, 'Up'))
		self.addSequential(cargo.Run_Cargo_Arm_Distance(self.robot, 120))