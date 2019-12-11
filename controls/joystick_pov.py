"""
Ctrl-Z FRC Team 4096
FIRST Robotics Competition 2018
Code for robot "Atla-Z"
contact@team4096.org
"""

from wpilib.buttons.button import Button

__all__ = ["JoystickButton"]


# Angle values for POV switch.
JOY_POV_NONE        = -1
JOY_POV_UP			= 0
JOY_POV_UP_RIGHT	= 45
JOY_POV_RIGHT		= 90
JOY_POV_DOWN_RIGHT	= 135
JOY_POV_DOWN		= 180
JOY_POV_DOWN_LEFT	= 225
JOY_POV_LEFT		= 270
JOY_POV_UP_LEFT		= 315


class Joystick_POV(Button):
    def __init__(self, joystick, pov_number):
        '''
        Create a joystick button for triggering commands.

        :param joystick: The GenericHID object that has the button (e.g.
                         :class:`.Joystick`, :class:`.KinectStick`, etc)
        :param pov_number: The button number
                             (see :meth:`GenericHID.getRawButton`)
        '''
        super().__init__()
        self.joystick = joystick
        self.pov_number = pov_number

    def get(self):
        '''
        Gets the value of the joystick button.
        :returns: The value of the joystick button
        '''
        #return self.joystick.getRawButton(self.buttonNumber)
        pov_val = self.joystick.getPOV()
        #print('pov = {0}'.format(pov_val))
        
        return pov_val == self.pov_number