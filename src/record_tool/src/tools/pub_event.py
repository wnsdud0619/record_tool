#-*- encoding: utf-8 -*-

import rospy
from std_msgs.msg import Header

def talker():
    pub = rospy.Publisher('/MKZ_events', Header, queue_size=10)
    rospy.init_node('pub_str', anonymous=True)
    pub_msg = Header()
    pub_msg.frame_id = "Emergency or Override"

    while True:
        key = input()
        if key == 'q':
            rospy.on_shutdown()
        rospy.loginfo("publish std_msg/header")
        pub_msg.stamp = rospy.get_rostime()
        pub.publish(pub_msg)

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
