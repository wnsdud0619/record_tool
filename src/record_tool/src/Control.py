#!/usr/bin/env python

import yaml
import io
import os.path
import os
import rospy
from std_msgs.msg import Header
from dbw_mkz_msgs.msg import Misc1Report
import time
from threading import Timer
from PyQt5.QtCore import *
import sys
import subprocess
import signal
from record_tool.srv import *

# steering btn check   
class CustomSignal_ros_steeringbtn(QObject):                
    signal = pyqtSignal(str)

    def run(self):
        signal__str = ""        
        self.signal.emit(signal__str)

# emergency, override check
class CustomSignal_ros_event(QObject):                
    signal = pyqtSignal(str)

    def run(self):
        signal__str = ""        
        self.signal.emit(signal__str)

# 남은 공간 확인
class space_checker(QThread):
    space_checker = pyqtSignal(str)
    def __init__(self,parent=None):
        super(space_checker, self).__init__()
        self.power = True 

    def run(self):  #무조건 run이라는 함수만 실행하게 되어 있음
        while self.power:
            st_home = os.statvfs("/")
            free = st_home.f_bavail * st_home.f_frsize
            free_space = (free/1024/1024/1024) - 15
            
            text = str(round(free_space, 3))
            self.space_checker.emit(text)
            time.sleep(1)

    def stop(self):
        self.power = False
        self.quit()       

# split bag 실행
class Thread_make_rosbag(QThread):
    def __init__(self,parent=None):
        super(Thread_make_rosbag, self).__init__()
        self.cmd = None
        self.root_path = sys.argv[1]

        #topic_path = self.root_path + '/data/hyper_param.yaml' 
        topic_path = './data/hyper_param.yaml' 
        with io.open(topic_path,'r', encoding="UTF-8") as f:
            self.topic_yaml = yaml.load(f, Loader=yaml.FullLoader) 

    def run_split(self):  #무조건 run이라는 함수만 실행하게 되어 있음
        #buffer_full_path = self.root_path + '/buffer'
        buffer_full_path = './buffer'
        if not os.path.exists(buffer_full_path):
            os.makedirs(buffer_full_path)
    
        #event_full_path = self.root_path + '/event'
        event_full_path = './event'
        if not os.path.exists(event_full_path):
            os.makedirs(event_full_path) 

        bag_name = time.strftime('%Y-%m-%d-%H-%M-%S')
        cmd_str = 'rosbag record -b 1024 -O ' + buffer_full_path + '/' + str(bag_name) + ' --split --max-splits 1 --duration=30 ' + self.topic_yaml["topics"]
        self.cmd = subprocess.Popen(cmd_str.split(), preexec_fn=os.setsid)

        return bag_name, event_full_path

    def run_manual(self):  #무조건 run이라는 함수만 실행하게 되어 있음
        #manual_full_path = self.root_path + '/manual'
        manual_full_path = './manual'
        if not os.path.exists(manual_full_path):
            os.makedirs(manual_full_path)

        bag_name = time.strftime('%Y-%m-%d-%H-%M-%S')
        cmd_str = 'rosbag record -b 1024 -O ' + manual_full_path + '/' + str(bag_name) + ' ' + self.topic_yaml["topics"]
        self.cmd = subprocess.Popen(cmd_str.split(), preexec_fn=os.setsid)

        return bag_name, manual_full_path

    def kill(self):
        if self.cmd != None:
            os.kill(self.cmd.pid, signal.SIGINT)
            self.cmd = None        

    def stop(self): 
        if self.cmd != None:
            os.kill(self.cmd.pid, signal.SIGINT)
            self.cmd = None        
        self.quit()
        self.wait(1000)

class MVC_Control:
    def __init__(self, _model, _view):
        self.buffer_size = 0
        self.is_situation_confirm = False
        self.save_path = None
        self.manual_btn_delay = None
        self.t_event = None
        self.root_path = sys.argv[1]
        self.model = _model
        self.view = _view
        self.view.set_control(self)
        self.dic_meta = {"passengers":self.model.passengers, "purpose":self.model.purpose, "area":self.model.area, "weather":self.model.weather, "situation":self.model.situation}
        self.load_meta_data()
        self.ros_listener()
        self.buffer_clear()

        #ros signal생성
        self.ros_event_signal = CustomSignal_ros_event()
        self.ros_event_signal.signal.connect(self.set_record_type_event)
        self.steering_btn_signal = CustomSignal_ros_steeringbtn()
        self.steering_btn_signal.signal.connect(self.set_record_type_manual)

        #쓰레드 생성
        self.Thread_make_rosbag = Thread_make_rosbag()
        self.Thread_space = space_checker(self)
        self.Thread_space.space_checker.connect(self.space_update)

        self.Thread_space.start()
        self.model.ros_data['bag_name'], self.save_path = self.Thread_make_rosbag.run_split()

        # UI init update
        self.view.update_label_record_state('Record type: ' + self.model.record_state)

    def ros_listener(self):
        rospy.init_node('ros_event', anonymous=True)
        rospy.Subscriber('/vehicle/misc_1_report', Misc1Report, self.ros_callback_steering_btn, queue_size=1)
        rospy.Service('add_two_ints', Record, self.return_bag_name)
  
    def return_bag_name(self, req): #req emergency override
        is_running = True        

        if self.model.record_state == 'STATE_NONE':
            self.model.ros_data["sec"] = req.stamp.secs
            self.model.ros_data["nsec"] = req.stamp.nsecs
            self.save_path = req.save_path
            is_running = False

            self.ros_event_signal.run()

        return RecordResponse(self.save_path ,self.model.ros_data['bag_name'], is_running)

    def buffer_clear(self):
        #cmd_str = 'rm -f ' + self.root_path + '/buffer/*'
        cmd_str = 'rm -f ' + './buffer/*'
        cmd = subprocess.Popen(cmd_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        cmd.wait()
        rospy.loginfo("clear buffer")

    def ros_callback_steering_btn(self, _data):
        if self.manual_btn_delay != None:
            if self.manual_btn_delay.is_alive():
                print("manual btn thread is alived")
                return            
                
        if _data.btn_ld_right:
            self.manual_btn_delay = Timer(2, self.manual_delay, args=()) 
            self.manual_btn_delay.start() 
            rospy.loginfo("steering btn sub")
            self.steering_btn_signal.run()
            if self.model.record_state == "STATE_NONE":
                now = _data.header.stamp
                self.model.ros_data["sec"] = now.secs
                self.model.ros_data["nsec"] = now.nsecs
                #rospy.loginfo("sec: %d, nec: %d",self.model.ros_data["sec"], self.model.ros_data["nsec"])

    def load_yaml(self, _meta_yaml_path):
    # AttributeError: module 'yaml' has no attribute 'FullLoader'  -> $ pip install -U PyYAML  
    # Py yaml > = 5.1
        with io.open(_meta_yaml_path,'r', encoding="UTF-8") as f:
            meta_yaml = yaml.load(f, Loader=yaml.FullLoader)

        for key, value in self.dic_meta.items():
            self.dic_meta[key] = meta_yaml[key]                     

    def load_meta_data(self):
        #meta_yaml_path = self.root_path + '/data/meta_data.yaml'
        #hyper_yaml_path = self.root_path + '/data/hyper_param.yaml'
        meta_yaml_path = './data/meta_data.yaml'
        hyper_yaml_path = './data/hyper_param.yaml'

        if os.path.isfile(hyper_yaml_path):
            with io.open(hyper_yaml_path,'r', encoding="UTF-8") as f:
                hyper_yaml = yaml.load(f, Loader=yaml.FullLoader)
            self.buffer_size = hyper_yaml['buffer_size']

        if os.path.isfile(meta_yaml_path):
            self.load_yaml(meta_yaml_path)
        else : 
            dic = self.view.run_set_all_meta_data()   
            for key, value in self.dic_meta.items():
                self.dic_meta[key] = dic[key] 
        self.model.ros_data['topic_list'] = hyper_yaml['topics']

        self.view.update_label(**self.dic_meta)

    def button_handler(self, text, button_type):
        if button_type == "manual_record":
            self.set_record_type_manual()
        elif button_type == "event_record":
            self.set_record_type_event()  
        else:
            if button_type == "situation":
                self.is_situation_confirm = True
            self.dic_meta[button_type] = text   
            self.view.update_label(**self.dic_meta)     

    def set_record_type_manual(self):
        if self.model.record_state == "STATE_EVENT_ON":
            return  
        self.model.record_type = "TYPE_MANUAL"
        self.record_handler()

    def set_record_type_event(self):
        if self.model.record_state == "STATE_MANUAL_ON":
            return
        self.model.record_type = "TYPE_EVENT"
        self.record_handler()

    def quit(self):
        #실행중인 프로세스, thread 종료
        self.Thread_make_rosbag.kill()
        rospy.logwarn("Event record end")

        while self.is_situation_confirm == False :
            rospy.loginfo("PLZ enter situation")
            time.sleep(1)            

        bag_name = self.write_yaml(self.model.record_type)     
        
        if self.save_path == None:
            #mv_dir = self.root_path + '/event/' + bag_name
            mv_dir = './event/' + bag_name
        else:
            #mv_dir = self.root_path + '/' + self.save_path
            mv_dir = './' + self.save_path

        #이동할 dir 생성 후 이동
        if not os.path.exists(mv_dir):
            os.makedirs(mv_dir)

        print(mv_dir)
        #cmd = subprocess.Popen('mv '+ self.root_path +'/buffer/*.bag ' + mv_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        cmd = subprocess.Popen('mv ./buffer/*.bag ' + mv_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        cmd.wait()
        
        #cmd = subprocess.Popen('mv ' + self.root_path + '/buffer/*.yaml '+ mv_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        cmd = subprocess.Popen('mv ./buffer/*.yaml '+ mv_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        cmd.wait()

        #time.sleep(1)
        self.model.ros_data['bag_name'], self.save_path = self.Thread_make_rosbag.run_split()
        self.model.record_state = "STATE_NONE"
        self.is_situation_confirm = False
        self.save_path = None

        self.view.update_label_record_state('Record type: ' + self.model.record_state)

    def manual_delay(self):
        rospy.loginfo("manual delay 2s")

    def state_update(self):
        self.view.update_label_record_state('Record type: ' + self.model.record_state)

    def kill_all_Thread(self):
        #실행중인 모든 Thread 종료
        self.Thread_make_rosbag.stop()
        self.Thread_space.stop()
        self.buffer_clear()
        #os.system('rm -rf ./buffer')

    def space_update(self, _text):
        self.view.update_space('Free space : ' + _text + 'GB')

        if int(float(_text)) - int(float(self.buffer_size)) < 0:
            self.kill_all_Thread()    
            #안내 box 생성
            self.view.run_messageBox()
            sys.exit()  

    def write_yaml(self, save_path):
        if save_path == "TYPE_MANUAL":
            #root = self.root_path + '/manual'
            root = './manual'
            self.reverse=True
        if save_path == "TYPE_EVENT":
            #root = self.root_path + '/buffer'
            root = './buffer'
            self.reverse=False

        is_not_file = True
        check_time = 0
        while is_not_file:
            file_list = os.listdir(root)
            file_list_avtive = [file for file in file_list if file.endswith(".active")]
            print(file_list_avtive)
            if file_list_avtive != []:
                rospy.loginfo("checking bag files")
                time.sleep(1)
                check_time = check_time + 1 
            else:
                is_not_file = False

        file_list_bag = [file for file in file_list if file.endswith(".bag")]
        file_list_bag.sort(reverse = self.reverse)
        if len(file_list_bag) == 0:
            rospy.loginfo("no search bag files")
            return

        yaml_name = root+'/'+ file_list_bag[0][0:-4]+ '.yaml'

        dic_all = self.model.ros_data
        dic_all.update(self.dic_meta)

        #unicode to str
        STRING_DATA = dict([(str(k), str(v)) for k, v in dic_all.items()])

        with open(yaml_name, 'w') as f:
            yaml.dump(STRING_DATA, f)

        name = self.model.ros_data['bag_name']

        #yaml저장 후 값 초기화
        self.dic_meta['situation'] = "None"           
        self.view.update_label(**self.dic_meta)
        self.model.ros_data['sec'] = 0
        self.model.ros_data['nsec'] = 0
        self.model.ros_data['bag_name'] = None

        return name

    def record_handler(self):
        if self.model.record_state == "STATE_NONE":
            if self.model.record_type == "TYPE_EVENT":
                self.model.record_state = "STATE_EVENT_ON"
                self.view.update_label_record_state('Record type: ' + self.model.record_state)
                rospy.logwarn("Event record start")
                print(self.model.record_type)

                #evnet 작동중 확인
                if self.t_event != None:
                    if self.t_event.is_alive():
                        print("event thread is alived")
                        return    
                #3초 딜레이주고 quit함수 실행
                self.t_event = Timer(3, self.quit, args=())
                self.t_event.start()  

                self.view.showDialog_btn_situation()

            elif self.model.record_type == "TYPE_MANUAL":
                self.model.record_state = "STATE_MANUAL_ON"
                self.view.update_label_record_state('Record type: ' + self.model.record_state)
                
                #실행중인 bag 종료
                self.Thread_make_rosbag.kill()
                
                #manual mode 시작
                rospy.logwarn("Mannual record start")
                self.model.ros_data['bag_name'], self.save_path = self.Thread_make_rosbag.run_manual()
                self.buffer_clear()

        elif self.model.record_state == "STATE_MANUAL_ON":
            if self.model.record_type == "TYPE_MANUAL":             
                self.Thread_make_rosbag.kill()
                print(self.model.passengers)
                rospy.logwarn("Mannual record end")

                self.write_yaml(self.model.record_type)

                #버퍼생성 rosbag 시작
                self.model.ros_data['bag_name'], self.save_path = self.Thread_make_rosbag.run_split()
                
                self.model.record_state = "STATE_NONE"
                self.view.update_label_record_state('Record type: ' + self.model.record_state)
