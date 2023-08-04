#-*- encoding: utf-8 -*-
#!/usr/bin/env python2.7

import rospy
from std_msgs.msg import Bool
from std_msgs.msg import String
from std_msgs.msg import Header

class republsh :
    dbw_enabled = False
    def __init__(self):
        self.listener()
	rospy.spin()

    def ros_callback(self, msg):
        if msg.data == True:
            self.dbw_enabled = True
        else : 
            if self.dbw_enabled == True:
                pub_msg = Header()
                pub_msg.stamp = rospy.get_rostime()
                pub_msg.frame_id = "Emergency or Override"
                self.pub.publish(pub_msg)
                self.dbw_enabled = False

    def listener(self):
        rospy.init_node('republish', anonymous=True)
        rospy.Subscriber('/vehicle/dbw_enabled', Bool, self.ros_callback, queue_size=10)
        self.pub = rospy.Publisher('/MKZ_events', Header, queue_size=10)
        
if __name__ == '__main__':
	repub = republsh()
