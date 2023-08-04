#-*- encoding: utf-8 -*-
#!/usr/bin/env python2.7

import Model
import Control
import View
import os
import sys

if __name__ == '__main__':
    meta_data = Model.MVC_Model("", "", "", "", "")
    app = View.QApplication(sys.argv)
    view = View.MyApp()
    control = Control.MVC_Control(meta_data, view)

    app.exec_()  #UI 종료


