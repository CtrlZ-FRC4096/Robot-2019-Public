import sys
import time
import socket
from networktables import NetworkTables
import logging

local_ip = socket.gethostbyname(socket.gethostname())

remote_ip = '10.40.96.2' if '40.96' in local_ip else '127.0.0.1'

logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize(server = remote_ip)

is_connected = False

def connectionListener(connected, info):
	global is_connected
	print("---------------------------")
	print(info, "; Connected=%s" % connected)
	print("---------------------------")
	if remote_ip == '127.0.0.1':
		print("Connected to SIMULATOR")
	else:
		print("Connected to ROBOT")
	print("---------------------------")
	is_connected = connected

if remote_ip == '127.0.0.1':
	print("Trying to connect to SIMULATOR")
else:
	print("Trying to connect to ROBOT")

NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

time.sleep(3)
while(not is_connected):
	time.sleep(2)
	print("Not connected yet")


table = NetworkTables.getTable("Robot")

print("Record Network Tables Values to lists tool")
print("This program requires the use of the ENTER key. Do not run on the DS.")
print('')
print("instructions | type 'r' or 'rv' to record another set of values (stilt height, arm angle, arm current, arm speed, arm voltage)")
print("instructions | type 'rp' or 'rpid' to record another set of pid values")
print("insturctions | type 'print' or 'p' print all stored non-pid values")
print("instructions | type 'ppid' to print out all stored pid values")
print("instructions | type 'quit' and press ENTER to quit")
print("instructions | type 'pp', 'pi', or 'pd' to GET the cargo arm (climb)'s current p, i or d value")
print("instructions |   ^ 'p' for print")
print("instructions | type 'sp', 'si', or 'sd' to SET the cargo arm (climb)'s current p, i or d value")
print("instructions |   ^ 's' for store")

stilt_height_list = []
arm_angle_list = []
arm_current_list = []
arm_speed_list = []
arm_voltage_list = []

stilt_height_list2 = []
p_list = []
i_list = []
d_list = []

while True:
	user_input = input('>')

	if(user_input == 'r' or user_input == 'rv'):
		stilt_height = table.getNumber("Front Climber Encoder", -1111)
		arm_angle = table.getNumber("AnalogPot value", -1111)
		arm_current = table.getNumber("Cargo Arm Current", -1111)
		arm_speed = table.getNumber("Cargo Arm Speed", -1111)
		arm_voltage = table.getNumber("Cargo Arm Voltage", -1111)

		stilt_height_list.append(stilt_height)
		arm_angle_list.append(arm_angle)
		arm_current_list.append(arm_current)
		arm_speed_list.append(arm_speed)
		arm_voltage_list.append(arm_voltage)

	if(user_input == 'rp' or user_input == 'rpid'):
		p_list.append(table.getNumber("climbP", -1111))
		i_list.append(table.getNumber("climbI", -1111))
		d_list.append(table.getNumber("climbD", -1111))
		stilt_height_list2.append(table.getNumber("Front Climber Encoder", -1111))

	if(user_input[:3] == 'sp '):
		table.putNumber("climbP", user_input[3:])

	if(user_input[:3] == 'si '):
		table.putNumber("climbI", user_input[3:])

	if(user_input[:3] == 'sd '):
		table.putNumber("climbD", user_input[3:])

	if(user_input[:2] == 'pp'):
		print(table.getNumber("climbP", -1111))

	if(user_input[:2] == 'pi'):
		print(table.getNumber("climbI", -1111))

	if(user_input[:2] == 'pd'):
		print(table.getNumber("climbD", -1111))

	if(user_input == 'quit' or user_input == 'print' or user_input == 'p'):
		print('STORED VALUES')

		print('--------------')
		print('Stilt Heights')
		print(stilt_height_list)

		print('--------------')
		print('Arm Angles')
		print(arm_angle_list)

		print('--------------')
		print('Arm Currents')
		print(arm_current_list)

		print('--------------')
		print('Arm Speeds')
		print(arm_speed_list)

		print('--------------')
		print('Arm Voltages')
		print(arm_voltage_list)
		print('..........')
		print('..........')

	if(user_input == 'quit' or user_input == 'ppid'):
		print('STORED >pid< VALUES')

		print('--------------')
		print('Stilt Heights for PID')
		print(stilt_height_list2)

		print('--------------')
		print('Arm Climb P Values')
		print(p_list)
		print('---')
		print('Arm Climb I Values')
		print(i_list)
		print('---')
		print('Arm Climb D Values')
		print(d_list)
		print('..........')
		print('..........')

	if(user_input == 'quit'):
		sys.exit()