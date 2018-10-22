import requests
import json
from apscheduler.schedulers.background import BackgroundScheduler


class GatewayStatusScheduler:

    def __init__(self, gateway_data):
        self.gateway_data = gateway_data
        self.sched = BackgroundScheduler()
        self.sched.start()
        self.job_id = ''
        self.url = '172.30.1.33'
        #self.url = '192.168.219.10'

    def shutdown(self):
        """
        모든 job들을 종료시켜주는 함수
        """
        self.sched.shutdown()

    def sendCentral(self):
        """
        가공된 게이트웨이 상태정보 함수의 내용을 중앙서버로 전달
        """
        summary_status = self.gateway_data.setSummary()
        r = requests.post('http://%s:10002/gateway_status' % self.url, data=json.dumps(summary_status))

    def scheduler(self, type, job_id):
        """
        스케쥴러가 실행되면서 combineMonitoring을 실행시키는 쓰레드 생성
        인수값이 cron일 경우, 날짜, 요일, 시간, 분, 초 등의 형식으로 지정하여,
        특정 시각에 실행되도록 합니다.(cron과 동일)****
        interval의 경우, 설정된 시간을 간격으로 일정하게 실행
        """
        print("%s Scheduler Start" % type)
        self.sendCentral()
        try:
            if type == 'interval':
                # self.sched.add_job(self.combineMonitoring, type, seconds=10, id=job_id, args=(job_id))
                self.sched.add_job(self.sendCentral, type, seconds=120)
        except:
            pass
