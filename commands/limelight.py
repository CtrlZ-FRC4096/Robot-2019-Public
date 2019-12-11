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
import subsystems.limelight

from commands import hatch

import const

class Check_Line(Command):

	def __init__(self, robot):
		super().__init__()
		self.robot = robot

		self.requires(self.robot.limelight)
		self.setInterruptible(True)

	def execute(self):
		if self.robot.limelight.is_line_visible() and self.robot.limelight.get_line_position() != None:
			self.robot.scheduler.add(hatch.Auto_Strafe_Carriage(self.robot, self.robot.limelight.get_line_position()))

	def isFinished(self):
		return False