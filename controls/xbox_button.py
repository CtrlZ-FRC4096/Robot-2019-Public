"""
Ctrl-Z FRC Team 4096
FIRST Robotics Competition 2019
Code for robot "Saba-Z"
contact@team4096.org
"""

from wpilib.buttons.joystickbutton import Button

__all__ = ["JoystickButton"]


class Xbox_Button(Button):
    def __init__(self, xbox_controller, buttonNumber):
        '''
        Create a Xbox button for triggering commands.

        :param joystick: The GenericHID object that has the button (e.g.
                         :class:`.Joystick`, :class:`.KinectStick`, etc)
        :param buttonNumber: The button number
                             (see :meth:`GenericHID.getRawButton`)
        '''
        super().__init__()

        self.xbox_controller = xbox_controller
        self.buttonNumber = buttonNumber

    def get(self):
        '''
        Gets the value of the joystick button.
        '''
        return self.xbox_controller.ds.getStickButton(self.xbox_controller.port, self.buttonNumber)