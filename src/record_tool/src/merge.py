#-*- encoding: utf-8 -*-
#!/usr/bin/env python2.7

import sys
import roslib;
import rospy
import rosbag
from rospy import rostime
import argparse
import os

def get_next(bag_iter, reindex = False, 
        main_start_time = None, start_time = None, 
        topics = None):
    try:
        result = bag_iter.next()
        if topics != None:
            while not result[0] in topics:
                result = bag_iter.next()
        if reindex:
            return (result[0], result[1], 
                result[2] - start_time + main_start_time)
        return result
    except StopIteration:
        return None

def get_limits(bagfile):
    print("Determine start and end index of %s..."%bagfile)
    end_time = None
    start_time = None

    for topic, msg, t in rosbag.Bag(bagfile).read_messages():
        if start_time == None or t < start_time:
            start_time = t
        if end_time == None or t > end_time:
            end_time = t
    return (start_time, end_time)

def merge_bag(main_bagfile, bagfile, outfile = None, topics = None, 
        reindex = True, prefix = ''):
    #get min and max time in bagfile
    main_limits = get_limits(main_bagfile)
    limits = get_limits(bagfile)
    #check output file
    if outfile == None:
        pattern = main_bagfile + "_merged_%i.bag"
        outfile = main_bagfile + "_merged.bag"
        index = 0
        while (os.path.exists(outfile)):
            outfile = pattern%index
            index += 1
    #output some information
    print("merge bag %s in %s"%(bagfile, main_bagfile))
    print( "topics filter: ", topics)
    print( "writing to %s."%outfile)
    if prefix:
        print("secondary prefix: %s"%prefix)
    #merge bagfile
    outbag = rosbag.Bag(outfile, 'w')
    main_bag = rosbag.Bag(main_bagfile).__iter__()
    bag = rosbag.Bag(bagfile).__iter__()
    main_next = get_next(main_bag)
    next = get_next(bag, reindex, main_limits[0], limits[0], topics)
    
    try:
        while main_next != None:
            outbag.write(main_next[0], main_next[1], main_next[2])
            main_next = get_next(main_bag)
        while next != None:
            outbag.write(next[0], next[1], next[2])
            next = get_next(bag)                 
    finally:
        outbag.close()