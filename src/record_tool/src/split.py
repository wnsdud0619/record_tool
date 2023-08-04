#-*- encoding: utf-8 -*-
#!/usr/bin/env python2.7


import glob
import os
import io
import yaml
import time

bagfile_list = glob.glob('./merged/*.bag')
yamlfile_list = glob.glob('./merged/*.yaml')

bagfile_list.sort()
yamlfile_list.sort()

file_list = []

for idx in range(len(bagfile_list)):
    for jdx in range(len(yamlfile_list)):
        if bagfile_list[idx][:-3] == yamlfile_list[jdx][:-4]:
            pair = (bagfile_list[idx], yamlfile_list[jdx])
            file_list.append(pair)

if len(file_list) == 0:
    return

return_cmd = os.popen('rosbag info '+ file_list[0][0] + '| grep start').read()
start_time_bag = float(return_cmd[-15:-2])

return_cmd = os.popen('rosbag info '+ file_list[0][0] + '| grep end').read()
end_time_bag = float(return_cmd[-15:-2])

with io.open(file_list[0][1],'r', encoding="UTF-8") as f:
    meta_yaml = yaml.load(f, Loader=yaml.FullLoader)

start_time_yaml = float(meta_yaml['event_rostime']) - 25.0
end_time_yaml = float(meta_yaml['event_rostime']) + 5.0

if start_time_bag > start_time_yaml:
    start_time = start_time_bag
else :
    start_time = start_time_yaml

if end_time_bag > end_time_yaml:
    end_time = end_time_yaml
else:
    end_time = end_time_bag

# rosbag filter input.bag output.bag "t.secs >= 1531425960 and t.secs <= 1531426140"
print(start_time)
print(end_time)

result_path = './result'
if not os.path.exists(result_path):
    os.makedirs(result_path)  

cmd = 'rosbag filter '+ file_list[0][0] + ' ' + result_path +'/' + str(0)+'.bag' + ' "t.secs >= ' + str(start_time) + ' and t.secs <= ' + str(end_time) + '"'
print(cmd)
os.system(cmd)
time.sleep(1)
os.system('mv '+ file_list[0][1]+ ' '+ result_path + '/' + str(0) + '.yaml')
#print('mv '+ file_list[0][1]+ ' '+ result_path + '/' + str(0) + '.yaml')
time.sleep(1)
os.system('rm '+ file_list[0][0])