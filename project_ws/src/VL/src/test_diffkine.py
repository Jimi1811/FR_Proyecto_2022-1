#!/usr/bin/env python
 
from __future__ import print_function
import rospy
from sensor_msgs.msg import JointState
 
from markers import *
from functions import *
 
 
# Initialize the node
rospy.init_node("testKineControlPosition")
print('starting motion ... ')
# Publisher: publish to the joint_states topic
pub = rospy.Publisher('joint_states', JointState, queue_size=10)
# Files for the logs
fxcurrent = open("/tmp/diffkine_P_xcurrent.txt", "w")                
fxdesired = open("/tmp/diffkine_P_xdesired.txt", "w")
fq = open("/tmp/q.txt", "w")
 
# Markers for the current and desired positions
bmarker_current  = BallMarker(color['RED'])
bmarker_desired = BallMarker(color['GREEN'])
 
# Joint names
jnames = ['waist_q1', 'shoulder_q2', 'revolution_q3','elbow_q4', 'slider_q5', 'wrist_q6']
 
# Desired position
xd = np.array([0.5, 0.2, 0.4])
# Initial configuration
q0  = np.array([0, 0, 0, 0, 0, 0])
 
# Resulting initial position (end effector with respect to the base link)
T = fkine(q0)
x0 = T[0:3,3]
 
epsilon = 0.0001
k = 3
count = 0
 
# Red marker shows the achieved position
bmarker_current.xyz(x0)
# Green marker shows the desired position
bmarker_desired.xyz(xd)
 
# Instance of the JointState message
jstate = JointState()
# Values of the message
jstate.header.stamp = rospy.Time.now()
jstate.name = jnames
# Add the head joint value (with value 0) to the joints
jstate.position = q0
 
# Frequency (in Hz) and control period 
freq = 200
dt = 1.0/freq
rate = rospy.Rate(freq)
 
# Initial joint configuration
q = copy(q0)
# Main loop
while not rospy.is_shutdown():
    if(q[4]<0):
        q[4]=0
    # Current time (needed for ROS)
    jstate.header.stamp = rospy.Time.now()
    # Kinematic control law for position (complete here)
    # -----------------------------
 
    J = jacobian_position(q)
    x = fkine(q)
    x = x[0:3, 3]
 
    e = x - xd
 
    if(np.linalg.norm(e) < epsilon):
        print('Desired point reached')
        print(x)
        print(q)
        break
 
    de = -k*e
    dq = np.linalg.pinv(J).dot(de)
    q = q + dt*dq
 
    count = count + 1
 
    if(count > 10000):
        print('Max number of iterations reached')
        break
 
    # -----------------------------
 
    # Log values                                                      
    fxcurrent.write(str(x[0])+' '+str(x[1]) +' '+str(x[2])+'\n')
    fxdesired.write(str(xd[0])+' '+str(xd[1])+' '+str(xd[2])+'\n')
    fq.write(str(q[0])+" "+str(q[1])+" "+str(q[2])+" "+str(q[3])+" "+
             str(q[4])+" "+str(q[5])+"\n")
    
    # Publish the message
    jstate.position = q
    pub.publish(jstate)
    bmarker_desired.xyz(xd)
    bmarker_current.xyz(x)
    # Wait for the next iteration
    rate.sleep()
 
print('ending motion ...')
fxcurrent.close()
fxdesired.close()
fq.close()
