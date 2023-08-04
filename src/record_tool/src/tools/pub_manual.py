#-*- encoding: utf-8 -*-
#!/usr/bin/env python2.7

import rospy
from dbw_mkz_msgs.msg import Misc1Report


def talker():
    pub = rospy.Publisher('/vehicle/misc_1_report', Misc1Report, queue_size=10)
    rospy.init_node('pub', anonymous=True)
    msg = Misc1Report()
    msg.btn_ld_right = True
    while True:
        key = input()
#        if key == 'q':
#            rospy.on_shutdown()
        msg.header.stamp = rospy.get_rostime()
        rospy.loginfo("publish right btn")
        pub.publish(msg)

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
