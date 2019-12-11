"""
Robot physics implementation for the pyfrc simulator
"""

### IMPORTS ###

import pyfrc.physics.drivetrains
import pyfrc.physics.motor_cfgs
import pyfrc.physics.tankmodel
import pyfrc.physics.units


### CLASSES ###

class PhysicsEngine( ):
	"""
	Physics model for a simple two-motor WCD-style robot
	"""
	def __init__(self, physics_controller):
		self.physics_controller = physics_controller

		self.drivetrain = pyfrc.physics.drivetrains.FourMotorDrivetrain(
		   deadzone = pyfrc.physics.drivetrains.linear_deadzone(0.5)
		)

		self.drivetrain = pyfrc.physics.tankmodel.TankModel.theory(
		    pyfrc.physics.motor_cfgs.MOTOR_CFG_CIM,
		    gearing = 10.0,
		    nmotors = 4,
		    robot_mass = 120	* pyfrc.physics.units.units.lbs,
		    x_wheelbase = 2.0	* pyfrc.physics.units.units.feet,
		    wheel_diameter = 6	* pyfrc.physics.units.units.inch
		)


	def update_sim(self, hal_data, now, tm_diff):
		l_motor_val = hal_data['pwm'][2]['value']
		r_motor_val = hal_data['pwm'][0]['value']

		vel_x, vel_y, rotation = self.drivetrain.get_distance(l_motor_val, r_motor_val, tm_diff)
		self.physics_controller.distance_drive(-vel_x * 0.5, -vel_y * 0.5, -rotation * 0.3)
