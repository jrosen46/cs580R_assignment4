#!/usr/bin/env python

"""
navigation.py

Two methods are given below.
The first uses actionlib and was inspired by the following 2 sources.
    (1) https://github.com/markwsilliman/turtlebot/blob/master/go_to_specific_point_on_map.py
    (2) http://edu.gaitech.hk/turtlebot/map-navigation.html
The second is much simpler (but not as powerful) and publishes PoseStamped
messages to the /move_base_simple/goal topic until the robot has come within
a certain distance from the taget location.
"""
import rospy
from geometry_msgs.msg import Pose, Point, Quaternion, PoseStamped
from nav_msgs.msg import Odometry
import actionlib
from actionlib_msgs.msg import GoalStatus
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal


def main():

    rospy.init_node('auto_navigation', anonymous=False)
    ac = actionlib.SimpleActionClient('move_base', MoveBaseAction)
    ac.wait_for_server(rospy.Duration(5))

    # target positions
    # TODO: check rviz to get approximate locations of target positions
    # TODO: should we add the z argument here? It may not be zero
    # depending on whether or not the room is on a slope
    targets = [
        {'x': -1.45, 'y': 0.582 , 'z': 0.},     # first go to start corner
        {'x': 5.01, 'y': -0.847, 'z': 0.},      # go to area before the door
        {'x': 5.75, 'y': -7.92, 'z': 0.},       # go to hallway to right
        {'x': 9.71, 'y': 2.44, 'z': 0.},        # go to hallway to left
        {'x': -1.45, 'y': 0.582, 'z': 0.},      # go back to start corner
    ]

    # TODO: understand what the quaternion does exactly
    q = {'x': 0., 'y': 0., 'z': 0., 'w': 1.}

    goal = MoveBaseGoal()
    # goal.target_pose is a PoseStamped msg
    # frame_id is constant ... so just set it once
    goal.target_pose.header.frame_id = 'map'

    for target in targets:
        goal.target_pose.header.stamp = rospy.get_rostime()
        goal.target_pose.pose = Pose(Point(**target), Quaternion(**q))
        ac.send_goal(goal)
        ac.wait_for_result(rospy.Duration(60))

        # understand what the GoalStatus object is
        if ac.get_state() != GoalStatus.SUCCEEDED:
            # try and move the robot a bit and try again
            raise NotImplementedError



###############################
# SIMPLE IMPLEMENTATION BELOW #
###############################

x = 0.
y = 0.

def set_current_pos(data):
    global x
    global y

    x = data.pose.pose.position.x
    y = data.pose.pose.position.y

def calc_dist(x1, y1, x2, y2):

    return ((x1-x2)**2 + (y1-y2)**2)**.5

def main_simple():

    rospy.init_node('auto_navigation', anonymous=False)
    pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=10)
    sub = rospy.Subscriber('/odom', Odometry, set_current_pos)

    # target positions
    # TODO: check rviz to get approximate locations of target positions
    # TODO: should we add the z argument here? It may not be zero
    # depending on whether or not the room is on a slope
    targets = [
        {'x': -1.45, 'y': 0.582 , 'z': 0.},     # first go to start corner
        {'x': 5.01, 'y': -0.847, 'z': 0.},      # go to area before the door
        {'x': 5.75, 'y': -7.92, 'z': 0.},       # go to hallway to right
        {'x': 9.71, 'y': 2.44, 'z': 0.},        # go to hallway to left
        {'x': -1.45, 'y': 0.582, 'z': 0.},      # go back to start corner
    ]

    # TODO: understand exactly what the quaternion does
    q = {'x': 0., 'y': 0., 'z': 0., 'w': 1.}

    goal = PoseStamped()
    goal.header.frame_id = 'map'
    for target in targets:
        goal.header.stamp = rospy.get_rostime()
        goal.pose = Pose(Point(**target), Quaternion(**q))
        rate = rospy.Rate(0.2)
        while calc_dist(goal.pose.position.x, goal.pose.position.y, x, y) > .05:
            pub.publish(goal)
            rate.sleep()


if __name__ == '__main__':
    try:
        main()
        #main_simple()
    except rospy.ROSInterruptException:
        pass
