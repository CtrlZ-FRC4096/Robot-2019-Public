"""
Ctrl-Z FRC Team 4096
FIRST Robotics Competition 2019
Code for robot "Saba-Z"
contact@team4096.org
"""

from wpilib.command.commandgroup import Command, CommandGroup
from wpilib.command.waitcommand import WaitCommand

import const
import subsystems.drivetrain
import networktables

class Drive_With_Tank_Values(Command):
	def __init__(self, robot, get_r, get_y):
		'''
		initializes tank drive movement.
		:param robot: the robot object
		:param get_r: Used to get the x angle, function that determines y direction
		:param get_y: Used to get the y angle, function that determines the y value and direction
		rotation and direction of rotation. Z value must be given if it separate from the joystick.
		'''
		super().__init__()

		self.robot = robot

		self.requires(self.robot.drive)
		self.setInterruptible(True)

		self.get_r = get_r
		self.get_y = get_y

	def execute(self):
		"""
		Get r and y values from our joystick axes and send them to subsystem
		"""

		self.robot.drive.drive_with_tank_values(self.get_r() * const.DRIVE_ROTATION_MULTIPLIER, self.get_y())

	def isFinished(self):
		return False

	def end(self):
		self.robot.drive.stop()

	def interrupted(self):
		self.end()

class Drive_Distance(Command):
	def __init__ (self, robot, distance, max_speed = None):
		super().__init__()

		self.robot = robot
		self.distance = distance
		self.distance_traveled = 0.0
		self.setInterruptible(False)

		self.requires(self.robot.drive)
		self.setTimeout(6)

	def initialize(self):
		self.robot.drive_encoder_left.reset()
		self.robot.drive_encoder_right.reset()

		self.robot.drive.drive_distance_pid.enable()
		print("Setpoint:", self.distance)
		self.robot.drive.drive_distance_pid.setSetpoint(self.distance)

	def isFinished(self):
		on_target = self.robot.drive.drive_distance_pid.onTarget()
		timed_out = self.isTimedOut()

		if timed_out:
			print('Drive Distance Timed out!')
		if on_target:
			self.distance_traveled = self.robot.drive.get_drive_distance_pid_input()
			print('Drive Distance On Target! {0:.2f}'.format(self.distance_traveled))

		return on_target or self.isTimedOut()

	def end(self):
		#print("Ending Drive Distance")
		self.robot.drive.drive_distance_pid.disable()

	def interrupted(self):
		self.end()


class Rotate_To_Angle(Command):
	def __init__(self, robot, angle):
		super().__init__()

		self.robot = robot
		self.angle = angle

		self.requires(self.robot.drive)
		self.setInterruptible(True)
		self.setTimeout(5)

	def initialize(self):
		self.robot.gyro.reset()
		#sleep(.25)
		#print('gyro start = {0:.2f}'.format(self.robot.gyro.getAngle()))
		self.robot.drive.rotate_pid.enable()
		self.robot.drive.rotate_pid.setSetpoint(self.angle)

	def isFinished(self):
		on_target = self.robot.drive.rotate_pid.onTarget()
		timed_out = self.isTimedOut()

		if timed_out:
			print('Rotate To Angle Timed out!')
			return True
		if on_target:
			print('Rotate On Target! {0:.2f}'.format(self.robot.gyro.getAngle()))

		return on_target or self.isTimedOut()

	def end(self):
		self.robot.drive.rotate_pid.disable()

	def interrupted(self):
		self.end()

class Stop(Command):
	def __init__(self, robot):
		super().__init__()

		self.robot = robot

		self.requires(self.robot.drive)
		self.setInterruptible(True)

	def execute(self):
		print( 'Stop' )
		self.robot.drive.drive_with_tank_values(0, 0, 0)

	def isFinished(self):
		return True

class Toggle_Correction(Command):
	# Switches between drive correction and no drive correction
	def __init__(self, robot):
		super().__init__()

		self.robot = robot

		self.requires(self.robot.drive)
		self.setInterruptible(True)

	def execute(self):
		const.DRIVE_CORRECTION_ENABLED = not const.DRIVE_CORRECTION_ENABLED

	def isFinished(self):
		return True

class Drive_Distance_Time(Command):
	def __init__ (self, robot, time, speed):
		super().__init__()

		self.robot = robot
		self.speed = -speed

		self.requires(self.robot.drive)
		self.setInterruptible(True)
		self.setTimeout(time)

	def execute(self):
		print("Driving")
		self.robot.drive.drive_with_tank_values(0, self.speed)

	def isFinished(self):
		timed_out = self.isTimedOut()

		return timed_out

class Set_Quick_Turn(Command):
	def __init__ (self, robot, quick_turn):
		super().__init__()

		self.robot = robot
		self.quick_turn = quick_turn

		self.requires(self.robot.drive)
		self.setInterruptible(False)

	def execute(self):
		self.robot.drive.quick_turn = self.quick_turn

	def isFinished(self):
		return True


class Rotate_To_Angle_Limelight( Command ):
	"""
	Uses the Limelight's "tx" offset value and the rotate PID to align the robot with
	the current vision target. The gyro is not used in this command.
	"""
	def __init__( self, robot ):
		super( ).__init__( )

		self.robot = robot
		self.requires( self.robot.drive )
		self.setTimeout( 5 )

	def initialize( self ):
		"""
		Start the PID with a setpoint of zero. Since "tx" is the degress off of center,
		closing that number to zero will align the robot.
		"""
		self.robot.drive.rotate_pid.disable( )
		self.robot.drive.rotate_pid.setSetpoint( 0.0 )
		self.robot.drive.rotate_pid.enable( )

	def execute( self ):
		"""
		Called repeatedly
		"""
		# print( 'Limelight tx = {0:.2f}'.format( self.robot.limelight.get_angle( ) ) )

	def isFinished( self ):
		"""
		Finished when rotate PID is on target OR we exceed our timeout value.
		"""
		on_target = self.robot.drive.rotate_pid.onTarget( )
		timed_out = self.isTimedOut( )

		if timed_out:
			print( 'Timed out!' )
		elif on_target:
			if self.robot.limelight.get_angle_to_target() is None:
				print ( 'Limelight Rotate PID input is NONE ')
			else:
				print( 'On Target tx! {0:.2f}'.format( self.robot.limelight.get_angle_to_target( ) ) )

		return on_target or self.isTimedOut( )

	def end( self ):
		"""
		Called once after isFinished returns true
		"""
		self.robot.drive.rotate_pid.disable( )


class Driver1_Controller_Rumble(Command):
	def __init__ (self, robot):
		super().__init__()

		self.robot = robot
		self.setInterruptible(True)

	def execute(self):
		self.robot.oi.driver1.setRumble(1.0)

	def isFinished(self):
		return False
