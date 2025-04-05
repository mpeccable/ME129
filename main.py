# Imports
import pigpio
import sys
import time
import traceback
import time

# Define the motor pins.
PIN_MOTOR1_LEGA = 8
PIN_MOTOR1_LEGB = 7

PIN_MOTOR2_LEGA = 5
PIN_MOTOR2_LEGB = 6

class Motor():
    """
    Motor object has 2 properties. Leg 1 and Leg 2. Drive the motor by
    creating a voltage difference between the two legs.
    """
    LEG_a = 0
    LEG_b = 0

    def __init__(self, lega, legb):
        self.LEG_a = lega
        self.LEG_b = legb


    def __repr__(self):
        return f"Motor(LEGa={self.LEG_a}, LEG_b={self.LEG_b})"


    def drive(self, speed, direction):
        """
        Drives a specified motor at a given speed (PWM Value) for a 
        given amount of time
        """
        if direction:
            io.set_PWM_dutycycle(self.LEG_a, speed)
            io.set_PWM_dutycycle(self.LEG_b, 0)
        else: 
            io.set_PWM_dutycycle(self.LEG_b, speed)
            io.set_PWM_dutycycle(self.LEG_a, 0)   


def stop(rightM, leftM):
    rightM.drive(0, True)
    leftM.drive(0, True)


def turn(rightM, leftM, angle, direction):
    """
    Turns the robot about the center of its wheelbase. Converts an angle 
    into a time for rotation given by the empirically found fudge factors.
    Turns CCW when direction is True, CW if False
    """
    duration = 0.0055 * angle + 0.04
    if direction == True: 
        rightM.drive(200, True)
        leftM.drive(200, True)
        time.sleep(duration)
    else: 
        rightM.drive(200, False)
        leftM.drive(200, False)
        time.sleep(duration)


def driveStraight(rightM, leftM, direction, duration):
    """
    Drives the robot given a speed (PWM Value) and the direction 
    (True = forward / False = backward)
    Fudge factor of 187/200 included
    3.9 s for 1 m of straight driving
    """
    if direction == False:
        rightM.drive(187, True)
        leftM.drive(20, False)
        time.sleep(duration)
        stop(rightM, leftM)
    else:
        rightM.drive(187, False)
        leftM.drive(200, True)
        time.sleep(duration)
        stop(rightM, leftM)


def drivePolygon(rightM, leftM, numSides, direction):
    turnAngle = 360/numSides
    if direction:
        for i in range(numSides):
            # Driving straight for 3.s travels 1 m
            driveStraight(rightMotor, leftMotor, True, 3.9)
            stop(rightMotor, leftMotor)
            turn(rightMotor, leftMotor, turnAngle, True)
            stop(rightMotor, leftMotor)
    else:
        for i in range(numSides):
            # Driving straight for 3.s travels 1 m
            driveStraight(rightMotor, leftMotor, True, 3.9)
            stop(rightMotor, leftMotor)
            turn(rightMotor, leftMotor, turnAngle, False)
            stop(rightMotor, leftMotor)


#
#   Main
#
if __name__ == "__main__":

    ############################################################
    # Prepare the GPIO interface/connection (to command the motors).
    print("Setting up the GPIO...")
    io = pigpio.pi()
    if not io.connected:
        print("Unable to connection to pigpio daemon!")
        sys.exit(0)
    print("GPIO ready...")

    # Set up the four pins as output (commanding the motors).
    io.set_mode(PIN_MOTOR1_LEGA, pigpio.OUTPUT)
    io.set_mode(PIN_MOTOR1_LEGB, pigpio.OUTPUT)
    io.set_mode(PIN_MOTOR2_LEGA, pigpio.OUTPUT)
    io.set_mode(PIN_MOTOR2_LEGB, pigpio.OUTPUT)

    # Prepare the PWM.  The range gives the maximum value for 100%
    # duty cycle, using integer commands (1 up to max).
    io.set_PWM_range(PIN_MOTOR1_LEGA, 255)
    io.set_PWM_range(PIN_MOTOR1_LEGB, 255)
    io.set_PWM_range(PIN_MOTOR2_LEGA, 255)
    io.set_PWM_range(PIN_MOTOR2_LEGB, 255)
    
    # Set the PWM frequency to 1000Hz.
    io.set_PWM_frequency(PIN_MOTOR1_LEGA, 1000)
    io.set_PWM_frequency(PIN_MOTOR1_LEGB, 1000)
    io.set_PWM_frequency(PIN_MOTOR2_LEGA, 1000)
    io.set_PWM_frequency(PIN_MOTOR2_LEGB, 1000)

    # Clear all pins, just in case.
    io.set_PWM_dutycycle(PIN_MOTOR1_LEGA, 0)
    io.set_PWM_dutycycle(PIN_MOTOR1_LEGB, 0)
    io.set_PWM_dutycycle(PIN_MOTOR2_LEGA, 0)
    io.set_PWM_dutycycle(PIN_MOTOR2_LEGB, 0)

    # Initialize both motor objects
    leftMotor = Motor(PIN_MOTOR1_LEGA, PIN_MOTOR1_LEGB)
    rightMotor = Motor(PIN_MOTOR2_LEGA, PIN_MOTOR2_LEGB)

    print("Motors ready...")


    try:
        print("Go, robot!")
        drivePolygon(rightMotor, leftMotor, 3, False)
        print("All done.")
    

    except BaseException as ex:
        # Report the error, but continue with the normal shutdown.
        print("Ending due to exception: %s" % repr(ex))
        traceback.print_exc()
        

    ############################################################
    # Turn Off.
    # Note the PWM will stay at the last commanded value.  So you want
    # to be sure to set to zero before the program closes.  Else your
    # robot will run away...
    print("Turning off...")

    # Clear the PINs (commands).
    io.set_PWM_dutycycle(PIN_MOTOR1_LEGA, 0)
    io.set_PWM_dutycycle(PIN_MOTOR1_LEGB, 0)
    io.set_PWM_dutycycle(PIN_MOTOR2_LEGA, 0)
    io.set_PWM_dutycycle(PIN_MOTOR2_LEGB, 0)
    
    # Also stop the interface.
    io.stop()