#!/usr/bin/env python

class MVC_Model:
    def __init__(self, _passengers, _purpose, _area, _weather, _situation):
        self.passengers = _passengers
        self.purpose = _purpose
        self.area = _area
        self.weather = _weather
        self.situation = _situation
        self.record_type = None
        self.record_state = "STATE_NONE"
        self.ros_data = {"sec":0,"nsec":0,"bag_name":None, "topic_list":None}

    # @property
    # def passengers(self):
    #     return self.passengers
    # @passengers.setter
    # def passengers(self, passengers):
    #     self.passengers = passengers

    # @property
    # def purpose(self):
    #     return self.purpose
    # @purpose.setter
    # def purpose(self, purpose):
    #     self.purpose = purpose

    # @property
    # def area(self):
    #     return self.area
    # @area.setter
    # def area(self, area):
    #     self.area = area

    # @property
    # def weather(self):
    #     return self.weather
    # @weather.setter
    # def weather(self, weather):
    #     self.weather = weather

    # @property
    # def situation(self):
    #     return self.situation
    # @situation.setter
    # def situation(self, situation):
    #     self.situation = situation        
              
    
