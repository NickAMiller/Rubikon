import RPi.GPIO as GPIO
import time
import kociemba

from RpiMotorLib import RpiMotorLib

from random import seed
from random import random
from random import randint
    
#define GPIO pins
GPIO_pins = (21, 21, 21) # Microstep Resolution MS1-MS3 -> GPIO Pin

direction1 = 22       # Direction -> GPIO Pin
step1 = 23      # Step -> GPIO Pin

direction2 = 9       # Direction -> GPIO Pin
step2 =25      # Step -> GPIO Pin

direction3 = 11       # Direction -> GPIO Pin
step3 = 8      # Step -> GPIO Pin

direction4 = 6       # Direction -> GPIO Pin
step4 = 12      # Step -> GPIO Pin

direction5 = 19       # Direction -> GPIO Pin
step5 = 16      # Step -> GPIO Pin

direction6 = 26       # Direction -> GPIO Pin
step6 = 20      # Step -> GPIO Pin

mymotor = (RpiMotorLib.A4988Nema(direction1, step1, GPIO_pins, "DRV8825"),
    RpiMotorLib.A4988Nema(direction2, step2, GPIO_pins, "DRV8825"),
    RpiMotorLib.A4988Nema(direction3, step3, GPIO_pins, "DRV8825"),
    RpiMotorLib.A4988Nema(direction4, step4, GPIO_pins, "DRV8825"),
    RpiMotorLib.A4988Nema(direction5, step5, GPIO_pins, "DRV8825"),
    RpiMotorLib.A4988Nema(direction6, step6, GPIO_pins, "DRV8825"))


# Declare the compensation for each motor within a tuple
compensation = (12, 15, 8, 10, 3, 5)

# pins to control the DRV8825 enable pins
EN_PIN = (4, 14, 15, 17, 18, 27)

# Internal variables to control code flow
last_dir = [1, 1, 1, 1, 1, 1]
moves_log = []
translation = ['L', 'F', 'R', 'B', 'D', 'U']

GPIO.setup(EN_PIN, GPIO.OUT, initial=GPIO.HIGH)

# seed random number generator
seed(1)

choice = int(input("Choose Operation: 0-Test 1-Scramble 2-Solve:"))

# Testing mode
if choice == 0:    
    while(True):

        motor = int(input("Motor number/0 to exit:")) - 1

        if motor == -1:
            break

        
        steps = int(input("Number of steps:"))
        direction = int(input("0-CounterClockwise 1-Clockwise:"))

        if direction != last_dir[motor]:
            steps += compensation[motor]
            last_dir[motor] = direction


        GPIO.output(EN_PIN[motor],GPIO.LOW) # pull enable to low to enable motor

        mymotor[motor].motor_go((direction == 1), # True=Clockwise, False=Counter-Clockwise
                            "Full" , # Step type (Full,Half,1/4,1/8,1/16,1/32)
                            steps, # number of steps
                            .004, # step delay [sec]
                            False, # True = print verbose output
                            .5) # initial delay [sec]

        GPIO.output(EN_PIN[motor],GPIO.HIGH)

# Scramble mode
if choice == 1:    
    while(True):

        moves = int(input("Number of moves to scramble/0 to unscramble/-1 to exit:"))

        if moves > 0:
            print('Scrambling for ', moves, 'moves')
            for i in range(moves):

                motor = randint(0, 5) # Get a random motor to move
                print('Side: ', motor+1)
                moves_log.append(motor)
                direction = 1 # Always go clockwise
                steps = 50 # Give it a quarter turn

                if direction != last_dir[motor]:
                    steps += compensation[motor]
                    last_dir[motor] = direction

                GPIO.output(EN_PIN[motor],GPIO.LOW) # pull enable to low to enable motor

                mymotor[motor].motor_go((direction == 1), # True=Clockwise, False=Counter-Clockwise
                                    "Full" , # Step type (Full,Half,1/4,1/8,1/16,1/32)
                                    steps, # number of steps
                                    .004, # step delay [sec]
                                    False, # True = print verbose output
                                    .5) # initial delay [sec]

                GPIO.output(EN_PIN[motor],GPIO.HIGH) # pull enable to low to enable motor

                time.sleep(.5)

        if moves == 0:
            print('UnScrambling for ', len(moves_log), 'moves')
            while(len(moves_log)) != 0:

                motor = moves_log.pop()
                print('Side: ', motor)
                direction = 0 # Always go counter-clockwise
                steps = 50 # Give it a quarter turn

                if direction != last_dir[motor]:
                    steps += compensation[motor]
                    last_dir[motor] = direction

                GPIO.output(EN_PIN[motor],GPIO.LOW) # pull enable to low to enable motor

                mymotor[motor].motor_go((direction == 1), # True=Clockwise, False=Counter-Clockwise
                                    "Full" , # Step type (Full,Half,1/4,1/8,1/16,1/32)
                                    steps, # number of steps
                                    .004, # step delay [sec]
                                    False, # True = print verbose output
                                    .5) # initial delay [sec]

                GPIO.output(EN_PIN[motor],GPIO.HIGH) # pull enable to low to enable motor

                time.sleep(.5)


# Solve mode
if choice == 2:
    
    # let the user input the cube state
    cube = input("Input string:")

    # Let the kociemba library solve it and 
    solved = kociemba.solve(cube)
    solution_string = ''.join(solved)
    solution = solution_string.split()

    for move in solution:
	direction = 1
	motor = translation.index(move[0])
	# If one character we don't need to care about the number of rotations
        if len(move) == 1:            
            steps = 50
        if len(move) == 2:
            if(move[1] == '\''):
                steps = 150
            if(move[1] == '2'):
                steps = 100

        GPIO.output(EN_PIN[motor],GPIO.LOW) # pull enable to low to enable motor

        mymotor[motor].motor_go((direction == 1), # True=Clockwise, False=Counter-Clockwise
                            "Full" , # Step type (Full,Half,1/4,1/8,1/16,1/32)
                            steps, # number of steps
                            .002, # step delay [sec]
                            False, # True = print verbose output
                            2) # initial delay [sec]

        GPIO.output(EN_PIN[motor],GPIO.HIGH) # pull enable to low to enable motor





# good practise to cleanup GPIO at some point before exit
GPIO.cleanup()

# Example input string for Kociemba
# RUFDULDDDRFUFRRFRRLBBBFRBLRUDUUDBLDBDFFFLLBLLLBFUBUURD
