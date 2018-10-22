import os
import logging
import socket
import psutil
from config import pid_config
from config import config

logging.basicConfig(filename=config['log_file'], level=logging.DEBUG,format='%(asctime)s %(message)s')

class GatewayStatus:

    def __init__(self):
        self.status = {
            "cpu": None,
            "memory": None,
            "disk": None,
            "ap": None,
            "network": None,
            "process": None,
            "ip": None,
            "pid": None
        }


    def callStatus(self):
        """
        monitoring_gateway의 모듈을 이용해 gateway의 상태정보를 수집한다.
        """
        cpu_total = self.getCPUpercent()
        mem_info = self.getMemoryInfo()
        disk_list = self.getDiskInfo()
        ap_list = self.getAPinfo()
        net_info = self.getNetIOcounters()
        proc_list = self.getProcess()
        gt_ip = self.getIPaddress()
        ser_dict = self.getPid()

        self.status['cpu'] = cpu_total
        self.status['memory'] = mem_info
        self.status['disk'] = disk_list
        self.status['ap'] = ap_list
        self.status['network'] = net_info
        #self.status['process'] = proc_list
        self.status['ip'] = gt_ip
        self.status['process'] = ser_dict

    def setSummary(self):
        """
        중앙서버로 보내는 상태정보 data를 가공한다.
        """
        self.callStatus()

        summary_status = {}

        cpu = self.status['cpu']['percent']
        mem_total = self.status['memory']['v_total']
        mem_used = self.status['memory']['v_used']
        mem_used_rate = self.status['memory']['percent']
        disk_total = self.status['disk'][-2]
        disk_used = self.status['disk'][-1]
        ser_info = self.status['process']

        gt_id = os.environ.get('GATEWAY_ID')

        summary_status = {
            'id': gt_id,
            'cpu': cpu,
            'mem_total': mem_total,
            'mem_used': mem_used,
            'mem_used_rate': mem_used_rate,
            'disk_total': disk_total,
            'disk_used': disk_used,
            'ser_name': ser_info
        }
        logging.info('summary: %s' % summary_status)

        return summary_status

    def getPid(self):
        """
        서비스가 정상 작동했다면 pid 파일이 생성됨을 이용, 각 서비스의 pid 파일 경로 환경변수로
        pid 파일을 검색, 파일이 있다면 내용을 불러온다.
        """
        process_dict ={}
        for service, pid_path in pid_config.items():
            pid = None
            if os.path.isfile(pid_path):
                with open(pid_path,'r') as f :
                    pid = int(f.read())
                try:
                    # pid파일이 존재해도 해당 파일의 pid가 현재 전체 프로세스 목록에 없을수 있다(=프로세스 종료)
                    psutil.pid_exists(pid)
                except:
                    pid = None
            process_dict.update({service:{'pid':pid}})

        return process_dict

    def getCPUpercent(self):
        """
        cpu_percent() : cpu 전체 사용률을 백분율로 반환
        cpu_times_percent() : cpu_times()와 반환 요소는 같으나 소요시간 대신 CPU 사용 백분율로 반환
        [0] : user* / [1] : nice 사용자모드에서 우선순위가 있는 프로세스 실행 사용량* /
        [2] : system 커널모드에서 프로세스 실행 사용량* /
        [3] : idle* / [4] : iowait* /
        [5] : irq 하드웨어 인터럽트 / [6] : softirq 소프트웨어 인터럽트 /
        [7] : steal 가상환경의 다른 OS에 소요한 시간 / [8] : guest / [9] : guest_nice
        """
        cpu_percent = psutil.cpu_percent()  # interval 없이 / 전체 cpu 사용량
        cpu_times_tuple = psutil.cpu_times_percent()

        cpu_total = {
            'percent': cpu_percent,
            'user': cpu_times_tuple[0],
            'nice': cpu_times_tuple[1],
            'system': cpu_times_tuple[2],
            'idle': cpu_times_tuple[3],
            'iowait': cpu_times_tuple[4]
        }
        return cpu_total

    def getMemoryInfo(self):
        """
        메모리 데이터 튜플로 반환
        virtual_memory() : 시스템 메모리 사용량 통계 byte
        [0] : total* / [1] : available / [2] : percent 사용중 메모리(%) / [3] : used* / [4] : free*
        [5] : active 사용가능한 메모리 / [6] : inactive / [7] : buffers* / [8] : cached* / [9] : shared
        swap_memory() : 스왑 메모리 통계
        [0] : total / [1] : used / [2] : free / [3] : percent /
        [4] : sin 시스템이 디스크로(in) 스왑한 bytes 개수 / [5] : sout 시스템이 디스크로부터(out) 스왑한 bytes 개수
        """
        mem_tuple = psutil.virtual_memory()
        mem_swap = psutil.swap_memory()

        # virtual memory, swap memory
        v_total = self.format_bytes(mem_tuple[0])
        v_used = self.format_bytes(mem_tuple[3])
        v_free = self.format_bytes(mem_tuple[4])
        active = self.format_bytes(mem_tuple[5])
        buffers = self.format_bytes(mem_tuple[7])
        cached = self.format_bytes(mem_tuple[8])
        s_total = self.format_bytes(mem_swap[0])
        s_used = self.format_bytes(mem_swap[1])
        s_free = self.format_bytes(mem_swap[2])

        mem_info = {
            'v_total': v_total,
            'percent': mem_tuple[2],
            'v_used': v_used,
            'v_free': v_free,
            'active': active,
            'buffers': buffers,
            'cached': cached,
            's_total': s_total,
            's_used': s_used,
            's_free': s_free}
        return mem_info

    def getDiskInfo(self):
        """
        disk_partitions() : 파티션 나뉘어져 있는 디스크 정보 리스트를 반환
        disk_usage(path) : path의 용량 정보들을 튜플형태로 반환
        """
        disk_list = []
        all_total = 0  # 마운트된 disk 용량을 모두 갖는 변수
        used_total = 0  # 마운트된 disk의 사용중 용량을 모두 갖는 변수

        for part in psutil.disk_partitions(all=False):
            if 'cdrom' in part.opts or part.fstype == '':
                # skip cd-rom drives with no disk in it; they may raise
                # ENOENT, pop-up a Windows GUI error for a non-ready
                # partition or just hang.
                continue
            mount_point = part.mountpoint
            usage = psutil.disk_usage(mount_point)
            device = part.device
            d_total = usage.total
            d_used = usage.used
            d_free = usage.free
            d_per = usage.percent
            all_total += d_total  # disk total*mount disks
            used_total += d_used  # used total*mount disks

            disk_vol = {
                'd_name': device,
                'd_total': d_total,
                'd_used': d_used,
                'd_free': d_free,
                'd_percent': d_per,
                'mount_point': mount_point
            }
            disk_list.append(disk_vol)

        disk_list.append(self.format_bytes(all_total))
        disk_list.append(self.format_bytes(used_total))
        return disk_list

    def getNetIOcounters(self):
        """
        net_io_counters() : packet이 들어오고 나간 양의 정보(bytes)를 튜플 형식으로 반환
        [0] : bytes_sent / [1] : bytes_recv / [2] : packets_sent / [3] : packets_recv /
        [4] : errin / [5] : errout / [6] : dropin / [7] : dropout
        """
        net_io = psutil.net_io_counters()
        b_sent = self.format_bytes(net_io[0])
        b_recv = self.format_bytes(net_io[1])
        p_sent = self.format_bytes(net_io[2])
        p_recv = self.format_bytes(net_io[3])

        net_info = {'b_sent': b_sent, 'b_recv': b_recv, 'p_sent': p_sent, 'p_recv': p_recv}
        # net_info = {'b_sent':net_io[0],'b_recv':net_io[1],'p_sent':net_io[2],'p_recv':net_io[3]}

        return net_info

    def getAPinfo(self):
        """
        system command 'arp -a'를 이용해 AP모드 연결 정보를 가져온다.
        ap 연결 해제시, 즉시 해제 결과가 보여지지않고(안전한 해제를 위한것으로 보임)
        일정시간이 지나야 연결 해제를 확인할수있다.
        => 이 함수는 현재 ap 연결 된 정보만 확인 가능
        """
        net_list = []
        ap_info = ''
        ap_list = []

        lines = os.popen('arp -a')  # os.popen() 이용해 명령어 실행 결과를 가져온다
        for line in lines:
            net_list.append(line)

        for i in range(len(net_list)):
            ap_info = net_list[i].split(' ')

            try:
                if ap_info.index('wlan0\n') and ap_info[3] != '<incomplete>':
                    # 게이트웨이 AP접속 데이터 있을시
                    ap_dict = {'ip': ap_info[1], 'mac': ap_info[3]}
                    ap_list.append(ap_dict)
            except:
                pass

        return ap_list

    def getProcess(self):
        """
        process_iter() : 실행중인 모든 프로세스의 클래스 인스턴스 생성 반복자(iterator) 반환. 일회성
        cmdline : 해당 프로세스를 실행 하는 커맨드 라인.
        이를 통해 우리 프로젝트 개발자들이 지정해놓은 프로세스 이름을 반환 받을 수 있음
        """
        proc_list =[]
        for proc in psutil.process_iter(attrs=['pid', 'name', 'username', 'cmdline']):
            try:
                if proc.info['cmdline'][1] == '/root/hospital/lora_receiver.py':
                    proc_list.append(proc.info)
            except:
                pass

        return proc_list

    def getIPaddress(self):
        """
        현재 게이트웨이 IP address 반환 함수
        getfqdn() : 인자 비어있을 시 host로 인식
        :rtype: object
        """
        gt_IP = socket.gethostbyname(socket.getfqdn())
        return gt_IP

    def format_bytes(self, bytes_num):
        """
        bytes를 읽기 편한 메모리 단위로 변환하는 함수
        """
        sizes = ["B", "KB", "MB", "GB", "TB"]

        i = 0
        dblbyte = bytes_num

        while (i < len(sizes) and bytes_num >= 1024):
            dblbyte = bytes_num / 1024.0
            i = i + 1
            bytes_num = bytes_num / 1024

        return str(round(dblbyte, 2)) + " " + sizes[i]