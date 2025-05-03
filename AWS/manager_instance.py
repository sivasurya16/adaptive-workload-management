from flask import Flask, request, jsonify, Response
import boto3
import requests
import threading
import time
from datetime import datetime, timedelta
from collections import deque
import signal #for graceful shutdown

app = Flask(__name__,static_folder=None)

# Constants
T1 = 125
T2 = 225
BACKEND_SERVER = "http://load-balancer-1391558584.ap-south-1.elb.amazonaws.com"
INSTANCE_START_TIMEOUT = 300  # 5 minutes in seconds

# AWS Config
region_name = 'ap-south-1'
elbv2 = boto3.client('elbv2', region_name=region_name)
ec2 = boto3.client('ec2', region_name=region_name)

# Target groups
TARGET_GROUPS = {
    'small': 'arn:aws:elasticloadbalancing:ap-south-1:975050195505:targetgroup/tg-small/811961e640771f8a',
    'medium': 'arn:aws:elasticloadbalancing:ap-south-1:975050195505:targetgroup/tg-medium/2b528b0c7d77684c',
    'large': 'arn:aws:elasticloadbalancing:ap-south-1:975050195505:targetgroup/tg-large/ec947ab293c85ae0'
}

# Instances per group
INSTANCE_IDS = {
    'small': ['i-00ff96ed038aa5bd7','i-04e7b7c72e6cac7ac'],
    'medium': ['i-01e61b60cd2b28d88','i-06ba1d9de6cec7609'],
    'large': ['i-02d003274d548e97f','i-0fddff7569d549f0d']
}


# State Management
current_state = 'small'
switching_event = threading.Event()

# Arrival rate calculation from Code 2
REQUEST_COUNT = 0
START_TIME = datetime.now()
HYSTERESIS_BUFFER = 3  # Added from Code 2

def wait_for_instance_state(instance_id, target_state='running'):
    """Wait for instance to reach specific state with timeout"""
    start_time = time.time()
    while time.time() - start_time < INSTANCE_START_TIMEOUT:
        response = ec2.describe_instances(InstanceIds=[instance_id])
        state = response['Reservations'][0]['Instances'][0]['State']['Name']
        if state == target_state:
            return True
        time.sleep(5)
    return False

def manage_instance(operation, group):
    """Manage all instances in a group with state verification"""
    for instance_id in INSTANCE_IDS[group]:
        try:
            if operation == 'start':
                # Check current state first
                current_state = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]['State']['Name']
                if current_state not in ['running', 'pending']:
                    ec2.start_instances(InstanceIds=[instance_id])
                    print(f"Starting {group} instance {instance_id}")
                    if not wait_for_instance_state(instance_id):
                        raise Exception(f"Failed to start {group} instance {instance_id} within timeout")
                else:
                    print(f"Instance {instance_id} already {current_state}")
            elif operation == 'stop':
                ec2.stop_instances(InstanceIds=[instance_id])
                print(f"Stopping {group} instance {instance_id}")
        except Exception as e:
            print(f"Instance management error for {instance_id}: {str(e)}")
            raise

def register_instances(group):
    """Register instances only after confirming running state"""
    # Verify all instances are running
    for instance_id in INSTANCE_IDS[group]:
        if not wait_for_instance_state(instance_id):
            raise Exception(f"Instance {instance_id} not in running state")
            
    # Register all instances
    targets = [{'Id': iid,'Port':8080} for iid in INSTANCE_IDS[group]]
    try:
        elbv2.register_targets(
            TargetGroupArn=TARGET_GROUPS[group],
            Targets=targets
        )
        print(f"Successfully registered {group} instances on port 8080")
    except Exception as e:
        print(f"Registration failed: {str(e)}")
        raise

def deregister_instances(group):
    """Deregister instances safely"""
    try:
        targets = [{'Id': iid,'Port':8080} for iid in INSTANCE_IDS[group]]
        elbv2.deregister_targets(
            TargetGroupArn=TARGET_GROUPS[group],
            Targets=targets
        )
        print(f"Deregistered {group} instances from port 8080")
    except Exception as e:
        print(f"Deregistration error: {str(e)}")


def warmup_and_switch(target_group_to_use):
    global current_state
    if switching_event.is_set():
        return

    switching_event.set()
    print(f"[INFO] Starting warm-up for: {target_group_to_use}")
    
    try:
        # Start and wait for new instance
        manage_instance('start', target_group_to_use)
        
        # Register and wait for health checks
        register_instances(target_group_to_use)
        
        # Verify health status
        start_time = time.time()
        while time.time() - start_time < 60:
            response = elbv2.describe_target_health(
                TargetGroupArn=TARGET_GROUPS[target_group_to_use],
                Targets=[{'Id': iid,'Port':8080} for iid in INSTANCE_IDS[target_group_to_use]]  # Fixed variable name here
            )
            if response['TargetHealthDescriptions'][0]['TargetHealth']['State'] == 'healthy':
                # Switch traffic
                deregister_instances(current_state)
                manage_instance('stop', current_state)
                current_state = target_group_to_use
                print(f"Successfully switched to {target_group_to_use}")
                return
            time.sleep(5)
            
        print(f"Health check timeout for {target_group_to_use}")
        
    except Exception as e:
        print(f"Transition failed: {str(e)}")
        if target_group_to_use != 'small':
            print("Attempting fallback to small")
            warmup_and_switch('small')
    finally:
        switching_event.clear()

# New arrival rate calculation using Code 2 logic
def get_arrival_rate():
    """Calculate requests/sec using total count since start"""
    now = datetime.now()
    return REQUEST_COUNT / (now - START_TIME).total_seconds()

def choose_load_balancer():
    # Using Code 2's arrival rate logic with hysteresis buffer
    rate = get_arrival_rate()
    if current_state == 'small' and rate > T1 + HYSTERESIS_BUFFER:
        return 'medium'
    elif current_state == 'medium' and rate > T2 + HYSTERESIS_BUFFER:
        return 'large'
    elif current_state == 'medium' and rate < T1 - HYSTERESIS_BUFFER:
        return 'small'
    elif current_state == 'large' and rate < T2 - HYSTERESIS_BUFFER:
        return 'medium'
    return current_state

def background_scaler():
    """Background scaling manager"""
    while True:
        try:
            target_state = choose_load_balancer()
            if target_state != current_state and not switching_event.is_set():
                print(f"Triggering scaling to {target_state}")
                threading.Thread(target=warmup_and_switch, args=(target_state,)).start()
            time.sleep(5)
        except Exception as e:
            print(f"Background scaler error: {str(e)}")

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def reverse_proxy(path):
    global REQUEST_COUNT
    REQUEST_COUNT += 1  # Increment request count from Code 2
    
    try:
        headers = dict(request.headers)
        headers['instance-type'] = current_state
        method = request.method
        url = f"{BACKEND_SERVER}/{path}"
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            params=request.args
        )
        
        return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))
    except Exception as e:
        return f"Error routing request: {e}", 500

@app.errorhandler(404)
def not_found(e):
  return Response("bug", status=404)

@app.route('/metrics')
def metrics():
    rate = get_arrival_rate()
    return jsonify({
        "arrival_rate": round(rate, 2),
        "active_group": current_state
    })


def handle_shutdown(signal_received, frame):
    print("\nShutdown requested: Deregistering and stopping all instances")
    for group in TARGET_GROUPS:
        deregister_instances(group)
        manage_instance('stop', group)
    exit(0)

    
if __name__ == '__main__':
    # Initialize with small instance
    try:
        print("Initializing small instance...")
        manage_instance('start', 'small')
        register_instances('small')
        
        # Ensure other groups are stopped
        for group in ['medium', 'large']:
            manage_instance('stop', group)
            deregister_instances(group)
            
        # Start background scaler
        threading.Thread(target=background_scaler, daemon=True).start()
        
        signal.signal(signal.SIGINT, handle_shutdown)  # Handle Ctrl+C

        app.run(host='0.0.0.0', port=8080)
        
    except Exception as e:
        print(f"Initialization failed: {str(e)}")
        # Emergency cleanup
        for group in TARGET_GROUPS:
            deregister_instances(group)
            manage_instance('stop', group)