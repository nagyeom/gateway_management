# -*- coding: utf-8 -*-

import time
import os
import requests
import json
import monitoring_gateway as mt_gt


class CentralServerData:

    def __init__(self):
        # self.url = '192.168.56.1' #중앙서버 주소
        self.url = '172.30.1.2' #중앙서버 주소

    def parsingCentral(self):
        self.url = '192.168.219.33' #중앙서버 주소
        # self.url = '172.30.1.2' #중앙서버 주소

    def sendCentral(self):
        """
        외부에서 CentralServerData 클래스를 사용할때 작업순서에 따라 클래스함수를 주기적으로 호출한다.
        ***현재는 while문을 사용하여 주기적으로 전송, 변경가능
        """
        total = self.callMonitoring()
        self.sendData(total)
        time.sleep(5)

    def callMonitoring(self):
        """
        monitoring_gateway의 모듈을 이용해 gateway의 상태정보를 수집한다.
        """
        data = {}
        cpu_total = {}
        mem_info = {}
        disk_list = []
        ap_list = []
        net_info = {}
        proc_list = []

        cpu_total = mt_gt.getCPUpercent()
        mem_info = mt_gt.getMemoryInfo()
        disk_list = mt_gt.getDiskInfo()
        ap_list = mt_gt.getAPinfo()
        net_info = mt_gt.getNetIOcounters()
        proc_list = mt_gt.searchProcess()
        gt_ip = mt_gt.getIPaddress()

        total = {'gt_ip':gt_ip,'cpu_total':cpu_total,'mem_info':mem_info,'disk_list':disk_list,'ap_list':ap_list,'net_info':net_info,'proc_list':proc_list}

        return total

    def parsingData(self, total):
        """
        중앙서버로 보내는 상태정보 data를 가공한다.
        """
        temp = total
        cpu = temp['cpu_total']['percent']
        mem_total = temp['mem_info']['v_total']
        mem_used = temp['mem_info']['v_used']
        mem_used_rate = temp['mem_info']['percent']
        disk_total = temp['disk_list'][-2]
        disk_used = temp['disk_list'][-1]

        gt_id = os.environ.get('GATEWAY_ID')

        central_data = {'id':gt_id,'cpu':cpu,'mem_total':mem_total,'mem_used':mem_used,'mem_used_rate':mem_used_rate,'disk_total':disk_total,'disk_used':disk_used}
        return central_data

    def sendData(self, total):
        """
        gateway 상태 정보 데이터를 중앙서버로 전송한다.
        """
        central_data = self.parsingData(total)
        r = requests.post('http://%s:5000' % self.url , data=json.dumps(central_data), timeout=None)
        r = requests.post('http://%s:5000' % self.url, data=json.dumps(total))


if __name__ == '__main__':
    test = CentralServerData()
    total = test.callMonitoring()
    test.parsingData(total)

