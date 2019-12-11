"""
Ctrl-Z FRC Team 4096
FIRST Robotics Competition 2018
Code for robot "Atla-Z"
contact@team4096.org
"""

from wpilib.buttons.joystickbutton import Button

__all__ = ["JoystickButton"]

class Xbox_Trigger(Button):
    def __init__(self, xbox_controller, axisNumber):
        '''
        Create a Xbox button for triggering commands.
        '''
        super().__init__()
        self.xbox_controller = xbox_controller
        self.axisNumber = axisNumber

    def get(self):
        '''
        Gets the value of the joystick button.

        :returns: The value of the joystick button
        '''
        return self.xbox_controller.ds.getStickAxis(self.xbox_controller.port, self.axisNumber) > 0.05
