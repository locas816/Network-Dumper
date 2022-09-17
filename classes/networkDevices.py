from PyQt5.QtWidgets import QWidget, QTreeWidget, QLabel, QTreeWidgetItem, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QApplication
from PyQt5 import uic
from PyQt5.Qt import QColor
import sys
import subprocess
import os
import multiprocessing


class NetworkDevices(QWidget):
    def __init__(self, localip, file_path):
        super().__init__()
        self.myip = localip
        self.deviceIpList = []
        # load template
        uic.loadUi(file_path+"/templates/networkDevices.ui", self)
        # finding children
        self.myIP = self.findChild(QLabel, "my_ip")
        self.devices = self.findChild(QLabel, "devices")
        self.deviceList = self.findChild(QTreeWidget, "deviceList")
        self.myGraph = self.findChild(QGraphicsView, "ipgraph")
        self.remain = self.findChild(QLabel, "remain_ip")
        # local IP
        self.myIP.setText(self.myip)
        ip = self.myip.split(".")
        ip[3]='{0}'
        self.ip = ".".join(ip)
        self.start()
        for ip in self.deviceIpList:
            self.deviceList.addTopLevelItem(QTreeWidgetItem([ip]))
        self.totalDevices = len(self.deviceIpList)
        self.devices.setText(str(self.totalDevices))
        self.remain_Ip = 254 - self.totalDevices
        self.remain.setText(str(self.remain_Ip))
        self.myGraph.setScene(self.chart())
        self.show()
    def chart(self):
        chart = QGraphicsScene()
        self.rem = 254 - self.totalDevices
        families = [self.totalDevices, self.rem, ]
        total = 0
        set_angle = 0
        count1 = 0
        colours = []
        total = sum(families)
        colours.append(QColor(100, 100, 100))
        colours.append(QColor(50, 205, 50))
        for family in families:
            angle = round(float(family * 5760) / total)
            ellipse = QGraphicsEllipseItem(0, 0, 300, 300)
            ellipse.setPos(0, 0)
            ellipse.setStartAngle(set_angle)
            ellipse.setSpanAngle(angle)
            ellipse.setBrush(colours[count1])
            set_angle += angle
            count1 += 1
            chart.addItem(ellipse)
        return chart

    def pinger(self, job_q, result_q):
        DEVNULL = open(os.devnull, 'w')
        while True:
            ip = job_q.get()
            if ip is None: break
            try:
                subprocess.check_call(['ping', '-c1', ip], stdout=DEVNULL)
                result_q.put(ip)
            except:
                pass
    def start(self):
        pool_size = 255
        jobs = multiprocessing.Queue()
        results = multiprocessing.Queue()
        pool = [multiprocessing.Process(target=self.pinger, args=(jobs, results)) for i in range(pool_size)]
        for p in pool:
            p.start()
        for i in range(1, 255):
            jobs.put(self.ip.format(i))
        for p in pool:
            jobs.put(None)
        for p in pool:
            p.join()
        while not results.empty():
            self.deviceIpList.append(results.get())


#
#
# if __name__ == "__main__":
# 	app = QApplication(sys.argv)
# 	mainWindow = NetworkDevices("192.168.1.127")
# 	sys.exit(app.exec_())
