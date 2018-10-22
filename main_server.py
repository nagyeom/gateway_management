
import json
from flask import Flask
from flask import render_template
from flask import request
import control_gateway as ct_gt
import gateway_status
import gateway_status_scheduler


app = Flask(__name__)

app.config['DEBUG'] = False


@app.route("/", methods=['GET','POST'])
def index():
    cpu_total = gateway_data.status['cpu']
    mem_info = gateway_data.status['memory']
    disk_list = gateway_data.status['disk']
    ap_list = gateway_data.status['ap']
    net_info = gateway_data.status['network']
    proc_list = gateway_data.status['process']
    gt_ip = gateway_data.status['ip']

    return render_template('status.html', cpu_total=cpu_total, mem_info=mem_info, disk_list=disk_list, ap_list=ap_list,
                           net_info=net_info, proc_list=proc_list, gt_ip=gt_ip)

@app.route("/control", methods=['GET','POST'])
def control():
    test = 'test var'
    if request.method == 'POST':
        if request.form['submit'] == 'reboot':
            ct_gt.rebootGateway()
    return render_template('control.html')

@app.route("/blepower", methods=['POST'])
def blePower():
    if request.method == 'POST':
        ble_radio =request.data.decode('utf-8')
        if ble_radio == 'on':
            ct_gt.onBluetooth()
        elif ble_radio == 'off':
            ct_gt.offBluetooth()
    return ''

@app.route("/lescan", methods=['GET'])
def lescan():
    scan_result = []
    result_dict = {}
    if request.method == 'GET':
        #print('BLE scanning...')
        scan_result = ct_gt.scan_for_devices()
        result_dict = {'result':scan_result}
        #print("scan_result:",scan_result, "result_dict:",result_dict)

    return json.dumps(result_dict)


if __name__ == '__main__':
    gateway_data = gateway_status.GatewayStatus()
    gateway_data.callStatus()
    scheduler = gateway_status_scheduler.GatewayStatusScheduler(gateway_data)

    try:
        scheduler.scheduler('interval', "1")
        app.run(host='0.0.0.0', port=8700)
    except KeyboardInterrupt:
        scheduler.shutdown()
