

import psutil

def list_processes():
    procs = list()

    for p in psutil.process_iter(attrs=None, ad_value=None):
        try:
            p_info = p.as_dict(attrs=['pid'])
            process = psutil.Process(pid=p_info['pid'])
            process.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    for p in psutil.process_iter(attrs=None, ad_value=None):
        try:
            p_info = p.as_dict(
                attrs=['pid', 'name', 'username', 'memory_percent'])
            current_process = psutil.Process(pid=p_info['pid'])
            p_info["cpu_percent"] = current_process.cpu_percent(interval=0.01)
            if (p_info['cpu_percent']):
                procs.append(p_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    processes = sorted(procs, key=lambda p: p['cpu_percent'], reverse=True)

    return processes

processes = list_processes()[:5]

for p in processes:
    print(p)
