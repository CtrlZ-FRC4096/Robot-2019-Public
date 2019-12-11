#! python3

"""
Ctrl-Z FRC Team 4096
FIRST Robotics Competition 2019
Code for robot "Saba-Z"
contact@team4096.org
"""

# Import our files
import logging
import time

import wpilib
import wpilib.command
import wpilib.timer

import networktables

import const
import oi

import subsystems.drivetrain
import subsystems.limelight
import subsystems.hatch
import subsystems.cargo
import subsystems.climber
import subsystems.arduino


log = logging.getLogger('robot')


class Robot(wpilib.TimedRobot):
	"""
	Main robot class.

	This is the central object, holding instances of all the robot subsystem
	and sensor classes.

	It also contains the init & periodic methods for autonomous and
	teloperated modes, called during mode changes and repeatedly when those
	modes are active.

	The one instance of this class is also passed as an argument to the
	various other classes, so they have full access to all its properties.
	"""
	def robotInit(self):

		# NetworkTables
		self.nt_robot = networktables.NetworkTables.getTable('Robot')

		### Subsystems ###

		# Drivetrain
		self.drive = subsystems.drivetrain.Drivetrain(self)

		# Driverstation
		self.driverstation = wpilib.DriverStation.getInstance()

		# Power Distribution Panel
		self.pdp = wpilib.PowerDistributionPanel()

		# Robot Components -- subsystems
		self.hatch = subsystems.hatch.Hatch(self)
		self.cargo = subsystems.cargo.Cargo(self)
		self.climber = subsystems.climber.Climber(self)

		# Limelight / camera
		self.limelight = subsystems.limelight.Limelight(self)

		# wpilib.CameraServer.launch()

		# Arduino / line sensors
		self.arduino = subsystems.arduino.Arduino(self)

		# Gyro
		# self.gyro = wpilib.ADXRS450_Gyro()

		# Ultrasonics
		# self.ultrasonic_front = wpilib.AnalogInput(const.AIN_ULTRASONIC_FRONT)
		# self.ultrasonic_rear = wpilib.AnalogInput(const.AIN_ULTRASONIC_REAR)

		self.match_time = 9999


		# Operator Input
		self.oi = oi.OI(self)

		# Encoders -- change after encoders are decided and added
		self.use_enc_correction = False

		self.drive_encoder_left = wpilib.Encoder(const.DIO_DRIVE_ENC_LEFT_1, const.DIO_DRIVE_ENC_LEFT_2, reverseDirection = const.DRIVE_ENCODER_LEFT_REVERSED)
		self.drive_encoder_right = wpilib.Encoder(const.DIO_DRIVE_ENC_RIGHT_1, const.DIO_DRIVE_ENC_RIGHT_2, reverseDirection = const.DRIVE_ENCODER_RIGHT_REVERSED)

		self.drive_encoder_left.setDistancePerPulse(1 / const.DRIVE_TICKS_PER_FOOT)
		self.drive_encoder_right.setDistancePerPulse(1 / const.DRIVE_TICKS_PER_FOOT)

		self.climber.climber_motor_1.setSelectedSensorPosition(0, 0, 10)
		self.climber.climber_motor_2.setSelectedSensorPosition(0, 0, 10)

		# Built in Accelerometer
		self.accel = wpilib.BuiltInAccelerometer()
		self.accel.setRange(0)	# Sets range from -2g to 2g

		# Array for average accel.
		self.accel_samples = []
		self.last_accel_value = 0.0

		# Pressure Sensor (200 psi)
		# self.pressure_sensor = wpilib.AnalogInput(const.AIN_PRESSURE_SENSOR)

		# Timer for pressure sensor's running average
		# self._pressure_samples = []
		# self._last_pressure_value = 0.0
		# self.pressure_timer = wpilib.Timer()
		# self.pressure_timer.start()
		# self.pressure_timer_delay = 1.0		# times per second

		# Time robot object was created
		self.start_time = time.time()

		## Scheduler ##
		self.scheduler = wpilib.command.Scheduler.getInstance()

		### LOGGING ###
		# Timers for NetworkTables update so we don't use too much bandwidth
		self.log_timer = wpilib.Timer()
		self.log_timer.start()
		self.log_timer_delay = 0.25		# 4 times/second

		# Disable LW telemetry before comp to improve loop times
		wpilib.LiveWindow.disableAllTelemetry()

		self.limelight.set_startup_modes()


	### DISABLED ###

	def disabledInit(self):
		self.match_time = 9999
		wpilib.command.Scheduler.getInstance().removeAll()

		self.arduino.set_led_state(self.arduino.Led_State.DEFAULT)

		self.limelight.set_startup_modes()
		# self.limelight.table_top.putNumber('ledMode', 1)

	def disabledPeriodic(self):
		#self.limelight.set_startup_modes()
		# self.limelight.table_top.putNumber('ledMode', 1)

		# if(self.oi.driver1.BACK() or self.oi.driver2.BACK()):
		# 	self.oi.driver1.setRumble(1)
		# else:
		# 	self.oi.driver1.setRumble(0)

		self.log()


	### AUTONOMOUS ###

	def autonomousInit(self):
		self.hatch.open_beak()
		self.teleopInit()

	def autonomousPeriodic(self):
		self.teleopPeriodic()


	### TELEOPERATED ###

	def teleopInit(self):
		self.match_time = 9999

		#self.arduino.set_led_state(self.arduino.Led_State.DEFAULT)

		self.limelight.set_startup_modes()
		# self.limelight.table_top.putNumber('ledMode', 1)

		# Removes any leftover commands from the scheduler
		wpilib.command.Scheduler.getInstance().removeAll()

		self.climber.stop_climber()

		# Reset all robot parts
		#self.gyro.reset()

		# Drive encoders
		self.drive_encoder_left.reset()
		self.drive_encoder_right.reset()

	def teleopPeriodic(self):
		wpilib.command.Scheduler.getInstance().run()
		self.log()

		#if self.match_time > 28 and self.match_time < 30:
		#	self.arduino.set_led_state(self.arduino.Led_State.END_GAME)


	### MISC ###

	def get_pressure(self):
		"""
		Calculate a running average of pressure values.  The sensor seems to jitter its values
		a lot, so this should smooth it out and make the SD display more readable.
		"""

		# voltage_pressure = self.pressure_sensor.getVoltage()
		# new_value = (250 * voltage_pressure / 5) - 25

		# self._pressure_samples.append(new_value)

		# if not self.pressure_timer.hasPeriodPassed(self.pressure_timer_delay):
		# 	return self._last_pressure_value

		# # Calculate new running average
		# new_avg = sum(self._pressure_samples) / len(self._pressure_samples)

		# self._pressure_samples = [ ]
		# self._last_pressure_value = new_avg

		#return new_avg

	def get_average_accel(self, axis):
		"""
		Calculates an average of the built in accelerometer values for any of the axis
		(X, Y, or Z)
		"""
		if axis == 'X':
			new_accel = self.accel.getX()
		elif axis == 'Y':
			new_accel = self.accel.getY()
		elif axis == 'Z':
			new_accel = self.accel.getZ()

		self.accel_samples.append(new_accel)

		if len(self.accel_samples) > 10:
			self.accel_samples.pop(0)

		new_avg = sum(self.accel_samples) / len(self.accel_samples)


		return new_avg


	def log(self):
		"""
		Logs some info to shuffleboard, and standard output
		"""

		# Only every 1/10 second or so to avoid flooding networktables
		if not self.log_timer.running or not self.log_timer.hasPeriodPassed(self.log_timer_delay):
			return

		#self.match_time = self.driverstation.getMatchTime()

		# self.nt_robot.putString('Pressure', '{0:.2f}'.format(self.get_pressure()))
		#self.nt_robot.putString('Ultrasonic', '{0:.2f}'.format(self.ultrasonic.getVoltage( ) / ( 5 / 512 )))

		self.drive.log()
		self.hatch.log()
		self.cargo.log()
		self.climber.log()
		self.limelight.log()
		self.arduino.log()

### MAIN ###

if __name__ == "__main__":
	wpilib.run(Robot)