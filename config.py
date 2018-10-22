import os

pid_config = {
    'lora': os.environ.get('LORA_PID'),
    'parsing': os.environ.get('PARSING_PID'),
    'mqtt': os.environ.get('MQTT_PID'),
    'tcp': os.environ.get('TCP_PID'),
    'broker': os.environ.get('BROKER_PID')
}

config={
    'log_file':'/var/www/gateway_management/management_service.log'
}