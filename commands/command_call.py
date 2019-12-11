"""
Ctrl-Z FRC Team 4096
FIRST Robotics Competition 2018
Code for robot "Atla-Z"
contact@team4096.org
"""

from wpilib.command import Command


class Command_Call(Command):
	'''
	This class allows us to create simple commands just by supplying a
	callable object (function). The function is called when the command is
	run, then the command immediately finishes.
	Adapted from code by FRC Team 2423.
	'''
	def __init__(self, call):
		'''
		Creates a new Command_Call
		'''
		super().__init__()

		self.call = call

	def isFinished(self):
		return True

	def end(self):
		if callable(self.call):    
			self.call()