import rospy
import time

def set_front_arm_angle(world_state, ros_util, target_angle):
    """ Set front arm to absolute angle target_angle in radians. """

    ros_util.status_pub.publish("Setting Front Arm Angle to {} Radians".format(target_angle))
    if target_angle > world_state.state_flags['front_arm_angle']:
        while target_angle > world_state.state_flags['front_arm_angle']:
            ros_util.command_pub.publish(ros_util.commands['front_arm_up'])
            ros_util.rate.sleep()
    else:
        while target_angle < world_state.state_flags['front_arm_angle']:
            ros_util.command_pub.publish(ros_util.commands['front_arm_down'])
            ros_util.rate.sleep()

    ros_util.command_pub.publish(ros_util.commands['null'])


def set_back_arm_angle(world_state, ros_util, target_angle):
    """ Set back arm to absolute angle target_angle in radians. """

    ros_util.status_pub.publish("Setting Back Arm Angle to {} Radians".format(target_angle))
    if target_angle > world_state.state_flags['back_arm_angle']:
        while target_angle > world_state.state_flags['back_arm_angle']:
            ros_util.command_pub.publish(ros_util.commands['back_arm_up'])
            ros_util.rate.sleep()
    else:
        while target_angle < world_state.state_flags['back_arm_angle']:
            ros_util.command_pub.publish(ros_util.commands['back_arm_down'])
            ros_util.rate.sleep()

    ros_util.command_pub.publish(ros_util.commands['null'])

def self_check(world_state, ros_util):
    """ Check for unfavorable states in the system and handle or quit gracefully. """
    if ros_util.auto_function_command == 32:
        ros_util.status_pub.publish("Cancel Auto Function Command Recieved")
        ros_util.command_pub.publish(ros_util.commands['null'])
        ros_util.command_pub.publish(ros_util.commands['kill_bit'])
        return -1
    if world_state.state_flags['on_side'] == True:
        ros_util.status_pub.publish("On Side - Attempting Auto Self Right")
        return 2
    if world_state.state_flags['battery'] < 10:
        ros_util.status_pub.publish("Low Battery - Returning to Base")
        world_state.state_flags['target_location'] = [0,0]
        return 3
    
    if world_state.state_flags['on_back'] == True:
        ros_util.status_pub.publish("On Back - Attempting Auto Self Right")
        return 4

"""
    # The following if statement needs to be implemented still
    if world_state.state_flags['standing_on_front'] == True:
        ros_util.status_pub.publish("Standing On Front - Attempting Auto Self Right")
        return 5

    # The following if statement needs to be implemented still
    if world_state.state_flags['standing_on_back'] == True:
        ros_util.status_pub.publish("Standing on Back - Attmepting Auto Self RIght")
        return 6
        """

    if world_state.state_flags['hardware_status'] == False:
        ros_util.status_pub.publish("Hardware Failure Shutting Down")
        ros_util.command_pub.publish(ros_util.commands['null'])
        ros_util.command_pub.publish(ros_util.commands['kill_bit'])
        return -1
    
    else:
        ros_util.status_pub.publish("Passed Status Check")
        return 1
        


def reverse_turn(world_state, ros_util):
    """ Reverse until object no longer detected and turn left """

    while world_state.state_flags['warning_flag'] == 3:
        ros_util.command_pub.publish(ros_util.commands['reverse'])
        ros_util.rate.sleep()

    new_heading = world_state.state_flags['heading'] + 60

    while (new_heading - 1) < world_state.state_flags['heading'] < (new_heading + 1):
        ros_util.command_pub.publish(ros_util.commands['left'])

def self_right_from_side(world_state, ros_util):
    """ Flip EZ-RASSOR over from its side. """

    ros_util.status_pub.publish("Initiating Self Right")
    self_right_completed = False
    arms_straightened = False
    while(!self_right_completed):
        if world_state.state_flags['on_side'] == False:
            ros_util.command_pub.publish(ros_util.commands['null'])
            return

        command = 0
        if !arms_straightened:
            if world_state.state_flags['front_arm_angle'] != 0:
                if world_state.state_flags['front_arm_angle'] < 0:
                        command |= ros_util.commands['front_arm_up']
                elif world_state.state_flags['front_arm_angle'] > 0:
                        command |= ros_util.commands['front_arm_down']
            if world_state.state_flags['back_arm_angle'] != 0:
                if world_state.state_flags['back_arm_angle'] < 0:
                        command |= ros_util.commands['back_arm_up']
                elif world_state.state_flags['back_arm_angle'] > 0:
                        command |= ros_util.commands['back_arm_down']

        if world_state.state_flags['front_arm_angle'] == 0 and world_state.state_flags['back_arm_angle'] == 0:
            arms_straightened = True

        if arms_straightened:
            if world_state.state_flags['front_arm_angle'] < math.PI / 4:
                command |= ros_util.commands['front_arm_up']
            if world_state.state_flags['back_arm_angle'] < math.PI / 4:
                command |= ros_util.commands['back_arm_up']
            if world_state.state_flags['front_arm_angle'] >= math.PI / 4 and world_state.state_flags['back_arm_angle'] >= math.PI / 4:
                self_right_completed = True
                command = ros_util.commands['null']

        ros_util.command_pub.publish(command)

    ros_util.command_pub.publish(ros_util.commands['null'])


def self_right_from_back(world_state, ros_util):
    """ Flip EZ-RASSOR over from its back. """

    self_right_completed = False
    arms_straightened = False
    arms_90_degrees = False
    tilt_complete = False
    drum_spin_complete = False
    front_arm_tilt = 1.9
    back_arm_tilt= 1.2
    while(not self_right_completed):
        # Might need a different flag for this case
        if world_state.state_flags['on_back'] == False:
            ros_util.command_pub.publish(ros_util.commands['null'])
            return

        command = ros_util.commands['null']
        if not arms_straightened:
            if world_state.state_flags['front_arm_angle'] != 0:
                if world_state.state_flags['front_arm_angle'] < 0:
                        command |= ros_util.commands['front_arm_up']
                elif world_state.state_flags['front_arm_angle'] > 0:
                        command |= ros_util.commands['front_arm_down']
            if world_state.state_flags['back_arm_angle'] != 0:
                if world_state.state_flags['back_arm_angle'] < 0:
                        command |= ros_util.commands['back_arm_up']
                elif world_state.state_flags['back_arm_angle'] > 0:
                        command |= ros_util.commands['back_arm_down']

        if world_state.state_flags['front_arm_angle'] == 0 and world_state.state_flags['back_arm_angle'] == 0:
            arms_straightened = True

        if arms_straightened and not arms_90_degrees:
            if world_state.state_flags['front_arm_angle'] < math.PI / 2:
                command |= ros_util.commands['front_arm_up']
            if world_state.state_flags['back_arm_angle'] < math.PI / 2:
                command |= ros_util.commands['back_arm_up']
            if world_state.state_flags['front_arm_angle'] >= math.PI / 2 and world_state.state_flags['back_arm_angle'] >= math.PI / 2:
                arms_90_degrees = True

        if arms_90_degrees and not tilt_complete:
            if world_state.state_flags['front_arm_angle'] < front_arm_tilt:
                command |= ros_util.commands['front_arm_up']
            if world_state.state_flags['back_arm_angle'] > back_arm_tilt:
                command |= ros_util.commands['back_arm_down']

        if world_state.state_flags['front_arm_angle'] >= front_arm_tilt and world_state.state_flags['back_arm_angle'] <= back_arm_tilt:
            tilt_complete = True

        if tilt_complete:
            command |= ros_util.commands['front_arm_dig']
            arms_straightened = False
            if world_state.state_flags['positionZ'] > -0.4:
                drum_spin_complete = True
                command = ros_util.commands['null']

        if drum_spin_complete and arms_straightened:
            self_right_completed = True

        ros_util.command_pub.publish(command)

    ros_util.command_pub.publish(ros_util.commands['null'])
