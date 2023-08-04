#-*- encoding: utf-8 -*-
#!/usr/bin/env python2.7

import os.path
import os
import glob
import subprocess
import signal
import merge
import time
import rospy
import sys
import io
import yaml

class Data_uploader:

    def __init__(self):
        self.root_path = sys.argv[1]
        self.full_folder_list = glob.glob(self.root_path + '/event/*')

        self.NAS_root_path = sys.argv[2]
        self.NAS_file_name = str(time.strftime('%Y-%m-%d'))
        self.NAS_Event_path = self.NAS_root_path + '/' + self.NAS_file_name + '/Event'

        dir = os.path.join(self.NAS_Event_path)
        if not os.path.exists(dir):
            os.makedirs(dir)

        self.upload_log_file = self.make_log(self.root_path)

    def make_log(self, _base_dir):
        _dir = os.path.join(_base_dir)
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        return open(os.path.join(_dir, "upload_log.txt"), 'w')

    def save(self, msg, _file):
        _file.write(msg + "\n")    

    def run_merge_split(self, _root_path, _event_folder_full_path, _NAS_Event_path, _is_poweroff): #event_folder_full_path
        merged_path = _root_path + '/merged'
        if not os.path.exists(merged_path):
            os.makedirs(merged_path)

        bag_file_list = glob.glob(_event_folder_full_path+'/*.bag') 
        bag_file_list.sort()

        yaml_path = glob.glob(_event_folder_full_path+'/*.yaml')

        with io.open(yaml_path[0],'r', encoding="UTF-8") as f:
            meta_yaml = yaml.load(f, Loader=yaml.FullLoader)
        bag_name = meta_yaml['bag_name']     

        #merge or move
        if len(bag_file_list) == 2:
            merge.merge_bag(bag_file_list[0], bag_file_list[1], merged_path + '/' + bag_name + '.bag')
            cmd = subprocess.Popen('mv ' + _event_folder_full_path + '/*.yaml '+ merged_path + '/' + bag_name + '.yaml', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            cmd.wait()
            print("merged")
        else:
            cmd = subprocess.Popen('mv ' + _event_folder_full_path + '/*.bag '+ merged_path + '/' + bag_name + '.bag', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            cmd.wait()
            cmd = subprocess.Popen('mv ' + _event_folder_full_path + '/*.yaml '+ merged_path + '/' + bag_name + '.yaml', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            cmd.wait()
            print("mvfile")
            cmd = subprocess.Popen('rm -rf ' + _event_folder_full_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            cmd.wait()
        print("*********************mergeing ended***********************************")

        #merge된 bag, yaml 불러옴
        merged_bagfile_full_path = glob.glob(merged_path + '/' + bag_name +'.bag')
        merged_yamlfile_full_path = glob.glob(merged_path + '/' + bag_name +'.yaml')

        file_pair = []
        #merge된 bag, yaml pair확인 
        if merged_bagfile_full_path[0][:-3] == merged_yamlfile_full_path[0][:-4]:
            pair = (merged_bagfile_full_path[0], merged_yamlfile_full_path[0])
            file_pair.append(pair)
        else :
            print("no matching")
            return

        #get start time in bag file
        return_cmd = os.popen('rosbag info '+ file_pair[0][0] + '| grep start').read()
        if return_cmd[0:1] == "":
            rospy.loginfo("no data in bag file")
            return
        start_time_bag = float(return_cmd[-15:-2])

        #get end time in bag file
        return_cmd = os.popen('rosbag info '+ file_pair[0][0] + '| grep end').read()
        if return_cmd[0:1] == "":
            rospy.loginfo("no data in bag file")
            return
        end_time_bag = float(return_cmd[-15:-2])

        #get yaml time
        with io.open(file_pair[0][1],'r', encoding="UTF-8") as f:
            meta_yaml = yaml.load(f, Loader=yaml.FullLoader)

        start_time_yaml = float(meta_yaml['sec']) + float(meta_yaml['nsec'])/1000000000.0 - 25.0
        end_time_yaml = float(meta_yaml['sec']) + float(meta_yaml['nsec'])/1000000000.0 + 5.0

        #bag file에 생성될 시간 정함
        if start_time_bag > start_time_yaml:
            start_time = start_time_bag
        else :
            start_time = start_time_yaml

        if end_time_bag > end_time_yaml:
            end_time = end_time_yaml
        else:
            end_time = end_time_bag

        # rosbag filter input.bag output.bag "t.secs >= 1531425960 and t.secs <= 1531426140"
        result_path = _root_path + '/result'
        if not os.path.exists(result_path):
            os.makedirs(result_path)  

        cmd_str = 'rosbag filter '+ file_pair[0][0] + ' ' + result_path +'/' + bag_name + '.bag' + ' "t.to_sec() >= ' + str(start_time) + ' and t.to_sec() <= ' + str(end_time) + '"'
        print(cmd_str)
        cmd = subprocess.Popen(cmd_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        cmd.wait()
        cmd = subprocess.Popen('mv '+ file_pair[0][1] + ' '+ result_path + '/' + bag_name + '.yaml', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        cmd.wait()
        cmd = subprocess.Popen('rm '+ file_pair[0][0], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        cmd.wait()
        cmd = subprocess.Popen('rm -rf ' + _root_path + '/merged', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        cmd.wait()
        print("*********************spliting ended***********************************")
        # 결과 폴더에서 NAS로 mv 실행
        splited_file_pair = []
        splited_pair = (result_path +'/' + bag_name + '.bag', result_path + '/' + bag_name + '.yaml')
        splited_file_pair.append(splited_pair)
        print(splited_file_pair)

        cmd = subprocess.Popen('mv '+ splited_file_pair[0][0] + ' ' + _NAS_Event_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if cmd.wait() != 0:
            _is_poweroff = False
            self.save("event bag upload error", self.upload_log_file)
            self.save(splited_file_pair[0][0], self.upload_log_file)  
            #print("event bag upload error")
        cmd = subprocess.Popen('mv '+ splited_file_pair[0][1] + ' ' + _NAS_Event_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if cmd.wait() != 0:
            _is_poweroff = False
            self.save("event yaml upload error", self.upload_log_file)
            self.save(splited_file_pair[0][1], self.upload_log_file)
            #print("event yaml upload error")

        print("*********************one cycle ended***********************************")

        return _is_poweroff

if __name__ == "__main__":

    data_uploader = Data_uploader()
    is_poweroff = True

    #event file merge split upload 실행
    for idx in range(len(data_uploader.full_folder_list)):
        is_poweroff = data_uploader.run_merge_split(data_uploader.root_path, data_uploader.full_folder_list[idx], data_uploader.NAS_Event_path, is_poweroff)

    #manual file pair 맞추기 실행
    bagfile_list = glob.glob(data_uploader.root_path + '/manual/*.bag')
    yamlfile_list = glob.glob(data_uploader.root_path + '/manual/*.yaml')

    bagfile_list.sort()
    yamlfile_list.sort()

    file_pair = []

    for idx in range(len(bagfile_list)):
        for jdx in range(len(yamlfile_list)):
            if bagfile_list[idx][:-3] == yamlfile_list[jdx][:-4]:
                pair = (bagfile_list[idx], yamlfile_list[jdx])
                file_pair.append(pair)
                
    print(file_pair)
    
    #manual 서버 업로드
    NAS_Manual_path = data_uploader.NAS_root_path + '/' + data_uploader.NAS_file_name + '/Manual'

    dir = os.path.join(NAS_Manual_path)
    if not os.path.exists(dir):
        os.makedirs(dir)

    for idx in range(len(file_pair)):
        cmd = subprocess.Popen('mv '+ file_pair[idx][0] + ' '+ NAS_Manual_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if cmd.wait() != 0:
            is_poweroff = False
            data_uploader.save("manual bag upload error", data_uploader.upload_log_file)
            data_uploader.save(file_pair[idx][0], data_uploader.upload_log_file)
            #print("manual bag upload error")
        cmd = subprocess.Popen('mv '+ file_pair[idx][1] + ' '+ NAS_Manual_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if cmd.wait() != 0:
            is_poweroff = False
            data_uploader.save("yaml bag upload error", data_uploader.upload_log_file)
            data_uploader.save(file_pair[idx][1], data_uploader.upload_log_file)
            print("manual yaml upload error")

    data_uploader.upload_log_file.close()

    #끝나면 프로그램 종료
    if is_poweroff:
        print("poweroff")
        #cmd = subprocess.Popen('poweroff', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)