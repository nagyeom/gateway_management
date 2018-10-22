# -*- coding: utf-8 -*-

import psutil
import os
import socket


def getIPaddress():
    """
    현재 게이트웨이 IP address 반환 함수
    getfqdn() : 인자 비어있을 시 host로 인식
    :rtype: object
    """
    gt_IP = socket.gethostbyname(socket.getfqdn())
    return gt_IP


def getCPUpercent():
    """
    cpu_percent() : cpu 전체 사용률을 백분율로 반환
    cpu_times_percent() : cpu_times()와 반환 요소는 같으나 소요시간 대신 CPU 사용 백분율로 반환
    [0] : user* / [1] : nice 사용자모드에서 우선순위가 있는 프로세스 실행 사용량* / 
    [2] : system 커널모드에서 프로세스 실행 사용량* / 
    [3] : idle* / [4] : iowait* / 
    [5] : irq 하드웨어 인터럽트 / [6] : softirq 소프트웨어 인터럽트 / 
    [7] : steal 가상환경의 다른 OS에 소요한 시간 / [8] : guest / [9] : guest_nice
    """
    cpu_percent = psutil.cpu_percent() # interval 없이 / 전체 cpu 사용량
    cpu_times_tuple = psutil.cpu_times_percent() 
    
    cpu_total = {
        'percent': cpu_percent,
        'user': cpu_times_tuple[0],
        'nice': cpu_times_tuple[1],
        'system': cpu_times_tuple[2],
        'idle': cpu_times_tuple[3],
        'iowait': cpu_times_tuple[4]}

    return cpu_total


def getMemoryInfo():
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

    #virtual memory, swap memory
    v_total = format_bytes(mem_tuple[0])
    v_used = format_bytes(mem_tuple[3])
    v_free = format_bytes(mem_tuple[4])
    active = format_bytes(mem_tuple[5])
    buffers = format_bytes(mem_tuple[7])
    cached = format_bytes(mem_tuple[8])
    s_total = format_bytes(mem_swap[0])
    s_used = format_bytes(mem_swap[1])
    s_free = format_bytes(mem_swap[2])
    
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


def getDiskInfo():
    """
    disk_partitions() : 파티션 나뉘어져 있는 디스크 정보 리스트를 반환 
    disk_usage(path) : path의 용량 정보들을 튜플형태로 반환
    """
    disk_list = []
    all_total = 0 #마운트된 disk 용량을 모두 갖는 변수
    used_total = 0 #마운트된 disk의 사용중 용량을 모두 갖는 변수

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
        all_total += d_total #disk total*mount disks
        used_total += d_used #used total*mount disks

        disk_vol = {'d_name':device,'d_total':d_total,'d_used':d_used,'d_free':d_free,'d_percent':d_per,'mount_point':mount_point}
        disk_list.append(disk_vol)

    disk_list.append(format_bytes(all_total))
    disk_list.append(format_bytes(used_total))
    return disk_list


def getAPinfo():
    """
    system command 'arp -a'를 이용해 AP모드 연결 정보를 가져온다.
    ap 연결 해제시, 즉시 해제 결과가 보여지지않고(안전한 해제를 위한것으로 보임)
    일정시간이 지나야 연결 해제를 확인할수있다.
    => 이 함수는 현재 ap 연결 된 정보만 확인 가능 
    """
    net_list = []
    ap_info = ''
    ap_list = []

    lines = os.popen('arp -a') #os.popen() 이용해 명령어 실행 결과를 가져온다
    for line in lines:
        net_list.append(line) 

    for i in range(len(net_list)):
        ap_info=net_list[i].split(' ')

        try:
            if ap_info.index('wlan0\n') and ap_info[3]!='<incomplete>': #게이트웨이 AP접속 데이터 있을시           
                ap_dict={'ip':ap_info[1],'mac':ap_info[3]}
                ap_list.append(ap_dict)
        except:
            pass
        
    return ap_list


def getNetIOcounters():
    """
    net_io_counters() : packet이 들어오고 나간 양의 정보(bytes)를 튜플 형식으로 반환
    [0] : bytes_sent / [1] : bytes_recv / [2] : packets_sent / [3] : packets_recv / 
    [4] : errin / [5] : errout / [6] : dropin / [7] : dropout
    """
    net_io = psutil.net_io_counters()
    b_sent = format_bytes(net_io[0])
    b_recv = format_bytes(net_io[1])
    p_sent = format_bytes(net_io[2])
    p_recv = format_bytes(net_io[3])

    net_info = {'b_sent':b_sent,'b_recv':b_recv,'p_sent':p_sent,'p_recv':p_recv}
    #net_info = {'b_sent':net_io[0],'b_recv':net_io[1],'p_sent':net_io[2],'p_recv':net_io[3]}

    return net_info


def searchProcess():
    """
    process_iter() : 실행중인 모든 프로세스의 클래스 인스턴스 생성 반복자(iterator) 반환. 일회성
    cmdline : 해당 프로세스를 실행 하는 커맨드 라인. 이를 통해 우리 프로젝트 개발자들이 지정해놓은 프로세스 이름을 반환 받을 수 있음
    """
    proc_list = []
    hospital_info = []
    for proc in psutil.process_iter(attrs=['pid', 'name', 'username','cmdline']):
        try:
            if proc.info['cmdline'][1] == '/root/hospital/lora_receiver.py':
                proc_list.append(proc.info)
        except:
            pass
    
    return proc_list


def format_bytes(bytes_num):
    """
    bytes를 읽기 편한 메모리 단위로 변환하는 함수
    """
    sizes = [ "B", "KB", "MB", "GB", "TB" ]
 
    i = 0
    dblbyte = bytes_num
 
    while (i < len(sizes) and  bytes_num >= 1024):
            dblbyte = bytes_num / 1024.0
            i = i + 1
            bytes_num = bytes_num / 1024
 
    return str(round(dblbyte, 2)) + " " + sizes[i]


if __name__ == '__main__':
    cpu_total = getCPUpercent()
    mem_info = getMemoryInfo()
    disk_list = getDiskInfo()
    ap_list = getAPinfo()
    net_info = getNetIOcounters()
    proc_list = searchProcess()

    print('----cpu_total----')
    print(cpu_total)
    print('----mem_info----')
    print(mem_info)
    print('----disk_list----')
    print(disk_list)
    print('----ap_list----')
    print(ap_list)
    print('----net_info----')
    print(net_info)
    print('----proc_list----')
    print(proc_list)
    