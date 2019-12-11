"""
Ctrl-Z FRC Team 4096
FIRST Robotics Competition 2019
Code for robot "Saba-Z"
contact@team4096.org
"""

import wpilib

###  IMPORTS ###

# Subsystems

# Commands
import commands.drivetrain
import commands.hatch
import commands.cargo
import commands.climber
import commands.limelight

# Controls
from customcontroller.xbox_command_controller import XboxCommandController

import const

## CONSTANTS ##

class OI:
	"""
	Operator Input - This class ties together controls and commands.
	"""
	def __init__(self, robot):
		self.robot = robot

		# Controllers
		# Xbox
		self.driver1 = XboxCommandController(0)
		self.driver2 = XboxCommandController(1)

		self.driver1.RIGHT_JOY_X.setDeadzone(.1)
		self.driver1.LEFT_JOY_Y.setDeadzone(.1)
		self.driver1.RIGHT_JOY_X.setInverted(True)

		self.driver1.addCustomButton('28-30 secs', lambda: 28 < self.robot.match_time < 30)

		self.driver2.LEFT_JOY_Y.setDeadzone(.1)
		self.driver2.LEFT_JOY_Y.setInverted(True)
		self.driver2.RIGHT_JOY_Y.setInverted(True)

		self.driver2.addCustomButton('Joystick_Up', lambda: self.driver2.RIGHT_JOY_Y() > .9)
		self.driver2.addCustomButton('Joystick_Down', lambda: self.driver2.RIGHT_JOY_Y() < -.9)
		self.driver2.addCustomButton('Joystick_Left', lambda: self.driver2.RIGHT_JOY_X() < -.9)
		self.driver2.addCustomButton('Joystick_Right', lambda: self.driver2.RIGHT_JOY_X() > .9)
		self.driver2.addCustomButton('Joystick_None', lambda: abs(self.driver2.RIGHT_JOY_X()) < .3 and abs(self.driver2.RIGHT_JOY_Y()) < .3)
		self.driver2.addCustomButton('Check_Joystick', lambda: -0.02 < self.driver2.LEFT_JOY_Y() < 0.02)

		### COMMANDS ###

		# DRIVE COMMANDS #
		self.drive_command = commands.drivetrain.Drive_With_Tank_Values(
			self.robot,
			self.driver1.RIGHT_JOY_X,
			self.driver1.LEFT_JOY_Y,
		)

		# HATCH #
		# Manually control the hatch
		self.hatch_command_manual = commands.hatch.Strafe_Carriage(self.robot,
			self.driver2.BOTH_TRIGGERS
		)

		# Run the hatch based on the front-facing limelight
		self.hatch_command_auto = commands.hatch.Auto_Strafe_Carriage_Continuous(self.robot,
			self.robot.limelight.get_line_position
		)

		# CARGO #
		self.cargo_arm_command = commands.cargo.Run_Cargo_Arm(self.robot,
			self.driver2.LEFT_JOY_Y
		)

		# LIMELIGHT #
		# self.limelight_command = commands.limelight.Check_Line(self.robot)

		# CLIMBER #

		# Set default commands
		self.robot.drive.setDefaultCommand(self.drive_command)
		self.robot.hatch.setDefaultCommand(self.hatch_command_auto)
		# self.robot.cargo.setDefaultCommand(self.cargo_arm_command)
		# self.robot.limelight.setDefaultCommand(self.limelight_command)

		'''
			By default run the auto hatch using the front limelight. If driver 2 tries to move the hatch manually with
			the triggers, do that instead. When driver 2 stops manually controlling the hatch, don't immediately go back
			to auto. Wait until driver2 presses the right stick.
		'''
		self.driver2.RIGHT_STICK.whenActive(self.hatch_command_auto)
		self.driver2.addCustomButton("Triggers In Use", lambda: abs(self.driver2.BOTH_TRIGGERS()) > .05)
		self.driver2.getCustomButton("Triggers In Use").whenActive(self.hatch_command_manual)

		# Controller 1: driver
		# self.driver1.START.whenActive(commands.drivetrain.Driver1_Controller_Rumble(self.robot))

		# Climber - front stilts only

		#self.driver1.POV.LEFT.whenActive(commands.climber.Climber_Down_With_Accel(self.robot))
		#self.driver1.POV.LEFT.whenInactive(commands.climber.Stop_Stilts(self.robot))

		self.driver1.POV.LEFT.whenActive(commands.climber.Run_Back_Stilts(self.robot, speed = 0.7, direction = 'Down'))
		self.driver1.POV.LEFT.whenInactive(commands.climber.Stop_Back_Stilts(self.robot))

		self.driver1.POV.RIGHT.whenActive(commands.climber.Run_Back_Stilts(self.robot, speed = 0.7, direction = 'Up'))
		self.driver1.POV.RIGHT.whenInactive(commands.climber.Stop_Back_Stilts(self.robot))

		self.driver1.Y.whenActive(commands.climber.Run_Both_Stilts_Down_With_Accel(self.robot))
		self.driver1.Y.whenInactive(commands.climber.Stop_Back_Stilts(self.robot))
		self.driver1.Y.whenInactive(commands.climber.Stop_Stilts(self.robot))

		self.driver1.POV.UP.whenActive(commands.climber.Run_Front_Stilts(self.robot, speed = 0.9, direction = 'Up'))
		self.driver1.POV.UP.whenInactive(commands.climber.Stop_Stilts(self.robot))

		self.driver1.POV.DOWN.whenActive(commands.climber.Run_Front_Stilts(self.robot, speed = 0.9, direction = 'Down'))
		self.driver1.POV.DOWN.whenInactive(commands.climber.Stop_Stilts(self.robot))

		self.driver1.A.whenActive(lambda: self.robot.climber.run_climber_drive(.3))
		self.driver1.A.whenInactive(lambda: self.robot.climber.run_climber_drive(0))

		self.driver1.B.toggleWhenActive(commands.climber.Climb_Stilts_And_Arm(self.robot))
		self.driver1.X.toggleWhenActive(commands.climber.Climb_Stilts_And_Arm_Level_2(self.robot))

		# Other
		#self.driver1.LEFT_BUMPER.whenActive(commands.drivetrain.Rotate_To_Angle_Limelight(self.robot))

		#self.driver1.START.whenActive(lambda: self.robot.limelight.toggle_driver_mode())

		# self.driver1.RIGHT_TRIGGER_AS_BUTTON.whenActive(self.robot.hatch.light_sensor_down)
		# self.driver1.RIGHT_TRIGGER_AS_BUTTON.whenInactive(self.robot.hatch.light_sensor_up)

		self.driver1.customButtons['28-30 secs'].whenActive(lambda: self.driver1.setRumble())
		self.driver1.customButtons['28-30 secs'].whenInactive(lambda: self.driver1.setRumble(0))

		# Controller 2: everything else
		# self.driver2.START.whenActive(commands.drivetrain.Driver1_Controller_Rumble(self.robot))

		# Cargo...
		self.driver2.RIGHT_BUMPER.whenActive(commands.cargo.Run_Cargo_Intake(self.robot, speed = 1))
		self.driver2.RIGHT_BUMPER.whenInactive(commands.cargo.Stop_Cargo_Intake(self.robot))

		self.driver2.LEFT_BUMPER.whenActive(commands.cargo.Run_Cargo_Intake(self.robot, speed = -1))
		self.driver2.LEFT_BUMPER.whenInactive(commands.cargo.Stop_Cargo_Intake(self.robot))

		self.driver2.START.whenActive(lambda: self.robot.cargo.toggle_manual_mode())

		self.driver2.customButtons['Joystick_Up'].whenActive(commands.cargo.Run_Cargo_Arm_Distance(self.robot, 141.5))
		self.driver2.customButtons['Joystick_Down'].whenActive(commands.cargo.Run_Cargo_Arm_Distance(self.robot, 3))
		self.driver2.customButtons['Joystick_Left'].whenActive(commands.cargo.Run_Cargo_Arm_Distance(self.robot, 64))
		self.driver2.customButtons['Joystick_Right'].whenActive(commands.cargo.Run_Cargo_Arm_Distance(self.robot, 38))
		self.driver2.customButtons['Joystick_None'].whenActive(commands.cargo.Stop_Cargo_Arm(self.robot))
		self.driver2.customButtons['Check_Joystick'].whenActive(commands.cargo.Stop_Cargo_Arm(self.robot))
		self.driver2.customButtons['Check_Joystick'].whenInactive(commands.cargo.Run_Cargo_Arm(self.robot, self.driver2.LEFT_JOY_Y))

		self.driver2.LEFT_STICK.whenActive(commands.cargo.Run_Cargo_Arm_Unsafe(self.robot, self.driver2.LEFT_JOY_Y))
		self.driver2.LEFT_STICK.whenInactive(commands.cargo.Stop_Cargo_Arm(self.robot))

		# Hatch...

		self.driver2.POV.UP.whenActive(commands.hatch.Push_Out_Carriage(self.robot))
		self.driver2.POV.DOWN.whenActive(commands.hatch.Pull_In_Carriage(self.robot))
		self.driver2.POV.LEFT.whenActive(commands.hatch.Close_Beak(self.robot))
		self.driver2.POV.RIGHT.whenActive(commands.hatch.Open_Beak(self.robot))

		self.driver2.A.whenActive(commands.hatch.Intake_Hatch(self.robot))
		self.driver2.Y.whenActive(commands.hatch.Place_Hatch(self.robot))

		self.driver2.B.whenActive(commands.hatch.Auto_Strafe_Carriage_To_Line(self.robot))
		self.driver2.X.whenActive(commands.hatch.Auto_Strafe_Carriage(self.robot, 5.5))



		# self.robot.arduino.set_led_state(self.robot.arduino.Led_State.DEFAULT)
		# self.driver2.POV.UP.whenActive(lambda: self.robot.arduino.set_led_state(self.robot.arduino.Led_State.DEFAULT))
		# self.driver2.POV.DOWN.whenActive(lambda: self.robot.arduino.set_led_state(self.robot.arduino.Led_State.HAVE_CARGO))
		# self.driver2.POV.LEFT.whenActive(lambda: self.robot.arduino.set_led_state(self.robot.arduino.Led_State.END_GAME))
