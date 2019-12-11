"""
Ctrl-Z FRC Team 4096
FIRST Robotics Competition 2019
Code for robot "Saba-Z"
contact@team4096.org
"""

import math
import sys

import wpilib
import wpilib.drive

import const

### CLASSES ###

class Drivetrain(wpilib.command.Subsystem):

	def __init__(self, robot):

		super().__init__(name = 'drive')

		self.robot = robot
		self.quick_turn = False

		#rotate PID - values are from 2018 (will need tweaking)
		self.rotate_kP = 0.01
		self.rotate_kI = 0.0
		self.rotate_kD = 0.0

		self.rotate_pid = wpilib.PIDController(
			self.rotate_kP,
			self.rotate_kI,
			self.rotate_kD,
			self.get_rotate_pid_input,
			self.set_rotate_pid_output,
		)

		self.rotate_pid.setAbsoluteTolerance(2.0)
		self.rotate_pid.setInputRange(-360, 360)
		self.rotate_pid.setContinuous(True)
		self.rotate_pid_output = 0

		# Drive distance PID - values are from 2018 (will need tweaking)
		self.distance_kP = 0.35
		self.distance_kI = 0.0
		self.distance_kD = 0.0

		self.drive_distance_pid = wpilib.PIDController(
			self.distance_kP,
			self.distance_kI,
			self.distance_kD,
			self.get_drive_distance_pid_input,
			self.set_drive_distance_pid_output,
		)

		self.drive_distance_pid.setAbsoluteTolerance(0.05) # in feet
		self.drive_distance_pid.setContinuous(False)
		self.drive_distance_pid_output = 0

		# Differential Drive object - 3 MiniCIM's with Victor SPs per side

		self.left1 = wpilib.VictorSP(const.PWM_DRIVE_MOTOR_LEFT_1)
		self.left2 = wpilib.VictorSP(const.PWM_DRIVE_MOTOR_LEFT_2)
		self.left3 = wpilib.VictorSP(const.PWM_DRIVE_MOTOR_LEFT_3)

		self.left1.setInverted(True)
		self.left2.setInverted(True)
		self.left3.setInverted(True)

		self.left = wpilib.SpeedControllerGroup(self.left1, self.left2, self.left3)

		self.right1 = wpilib.VictorSP(const.PWM_DRIVE_MOTOR_RIGHT_1)
		self.right2 = wpilib.VictorSP(const.PWM_DRIVE_MOTOR_RIGHT_2)
		self.right3 = wpilib.VictorSP(const.PWM_DRIVE_MOTOR_RIGHT_3)

		self.right1.setInverted(True)
		self.right2.setInverted(True)
		self.right3.setInverted(True)

		self.right = wpilib.SpeedControllerGroup(self.right1, self.right2, self.right3)

		self.drive = wpilib.drive.DifferentialDrive(self.left, self.right)

		#Drive correction
		self.r = 0.0
		self.corrected_rotation = 0.0
		self.y = 0.0
		self.x = 0.0
		self.sensitivity = 1.0

		self._was_correcting = False
		self._correction_start_angle = None

		self.last_right_enc = 0
		self.last_left_enc = 0

	def get_drive_distance_pid_input(self):
		distance_right = self.robot.drive_encoder_right.getDistance()
		distance_left = self.robot.drive_encoder_left.getDistance()
		avg_distance = (distance_right + distance_left) / 2.0

		return avg_distance

	def set_drive_distance_pid_output(self, output):
		if self.drive_distance_pid.onTarget():
			output = 0

		min_output = const.DRIVE_MIN_OUTPUT_TANK

		if output < 0:
			output = min(output, -min_output)
		elif output > 0:
			output = max(output, min_output)

		self.drive_distance_pid_output = output

		self.drive_with_tank_values(self.rotate_pid_output, -output, 0)

	def update_drive_distance_pid(self, p = None, i = None, d = None):
		'''
		Updates the PID coefficients
		'''
		if p:
			self.distance_kP = p
		if i:
			self.distance_kI = i
		if d:
			self.distance_kD = d

		print('Drive Distance PID updated: {0:.2f}, {1:.2f}, {2:.2f}'.format(self.distance_kP, self.distance_kI, self.distance_kD))
		self.drive_distance_pid.setPID(self.distance_kP, self.distance_kI, self.distance_kD)

	def get_rotate_pid_input(self):
		# print( 'Limelight tx = {0:.2f}'.format( angle ) )
		value = self.robot.limelight.get_angle_to_target()

		if value is None:
			return 0

		return -value

	def set_rotate_pid_output( self, output ):
		# invert it
		output = -float( output )

		# Make sure we're outputing at least enough to move the robot at all
		min_output = const.DRIVE_MIN_ROTATION_OUTPUT_TANK

		if output < 0:
			output = min( output, -min_output )
		elif output > 0:
			output = max( output, min_output )

		#wpilib.SmartDashboard.putString( 'Drive Rotate PID Output: ', '{0:.3f}'.format( output ) )
		# print('Rotate PID output = {0:.3f}'.format( output ) )

		self.rotate_pid_output = output

		self.drive_with_tank_values( output, self.drive_distance_pid_output, 0 )


	def run(self,rotation):
		self.drive_with_tank_values(rotation, 0, 0)

	def drive_with_tank_joysticks(self, left_axis, right_axis):
		"""
		needs work, and support for correction.
		"""
		self.drive.arcadeDrive(left_axis(), right_axis())

	def set_sensitivity (self,sensitivity):
		self.sensitivity = sensitivity

	def _get_corrected_rotation_gyro(self, rotation_value, y_value, strafe_value):

		#If gyro drive correction is enabled, and the user isn't manually rotating the robot, let the gryo angle correct the rotation.

		if not const.DRIVE_CORRECTION_ENABLED:
			self.robot.nt_robot.putString('Drive Correction: ', 'DISABLED')
			self._correction_state_angle = None
			return rotation_value

		if (abs(y_value) > 0.025) and abs(rotation_value) < const.DRIVE_CORRECTION_ROTATION_THRESHOLD:
			#This means driver is moving forward/backward or strafing, but NOT rotating
			if self._correction_start_angle is None:
				#We were not correcting last time, so save gyro angle and start correcting to that
				self.robot.gyro.reset()
				self._correction_start_angle = self.robot.gyro.getAngle()
				return rotation_value

			else:
				#We're correcting so adjust rotation
				if y_value < 0:
					tmp_correction_proportion = const.DRIVE_CORRECTION_PROPORTION_FORWARD
				else:
					tmp_correction_proportion = const.DRIVE_CORRECTION_PROPORTION_REVERSE

				correction_amt = (self._correction_start_angle - self.robot.gyro.getAngle()) * -tmp_correction_proportion
				rotation_value += correction_amt
				self.robot.nt_robot.putString('Drive Correction: ', 'ACTIVE - {0:.4f}'.format(correction_amt))
				self.robot.nt_robot.putNumber('Drive Correction Int: ', 1.0)
		else:
			self.robot.nt_robot.putString('Drive Correction: ', 'INACTIVE')
			self.robot.nt_robot.putNumber('Drive Correction Int: ', 0.0)
			self._correction_start_angle = None

		return rotation_value

	def _get_corrected_rotation_enc(self, rotation_value, y_value, strafe_value):
		"""
		Does drive correction using drivetrain encoders (not the gyro)
		"""
		if not const.DRIVE_CORRECTION_ENABLED:
			self.robot.nt_robot.putString('Drive Correction: ', 'DISABLED')
			self._was_correcting = False
			return rotation_value

		if abs(y_value) > 0.025 and abs(rotation_value) < const.DRIVE_CORRECTION_ROTATION_THRESHOLD:
			#This means driver is moving forward/back, but NOT rotating
			if self._was_correcting == False:
				#We were not correcting last time, so save gyro angle and start correcting to that
				self.robot.drive_encoder_left.reset()
				self.robot.drive_encoder_right.reset()
				self.last_left_enc = self.robot.drive_encoder_left.get()
				self.last_right_enc = self.robot.drive_encoder_right.get()
				self._was_correcting = True
				return rotation_value

			else:
				#We're correcting so adjust rotation
				if y_value > 0:
					tmp_correction_proportion = const.DRIVE_CORRECTION_PROPORTION_FORWARD_ENC
				else:
					tmp_correction_proportion = const.DRIVE_CORRECTION_PROPORTION_REVERSE_ENC

				correction_amt = ((self.last_right_enc + self.robot.drive_encoder_right.get()) - (self.last_left_enc + self.robot.drive_encoder_left.get())) * -tmp_correction_proportion
				rotation_value += correction_amt
				self.robot.nt_robot.putString('Drive Correction: ', 'ACTIVE - {0:.4f}'.format(correction_amt))
				self.robot.nt_robot.putNumber('Drive Correction Int: ', 1.0)
		else:
			self.robot.nt_robot.putString('Drive Correction: ', 'INACTIVE')
			self.robot.nt_robot.putNumber('Drive Correction Int: ', 0.0)
			self._was_correcting = False

		return rotation_value


	def drive_with_tank_values(self, rotation_value, y_value, strafe_value = 0):

		self.r = rotation_value
		self.y = y_value # * self.sensitivity

		if self.robot.use_enc_correction:
			corrected_rotation_value = self._get_corrected_rotation_enc(rotation_value, y_value, strafe_value)
		else:
			corrected_rotation_value = self._get_corrected_rotation_gyro(rotation_value, y_value, strafe_value)

		self.corrected_rotation = corrected_rotation_value

		self.drive.arcadeDrive(y_value, corrected_rotation_value)

	def stop(self):
		self.drive_with_tank_values(0, 0, 0)
		self.drive.stopMotor()

	def log(self):
		'''
		logs various things about the drivetrain
		'''