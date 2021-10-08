#!/usr/bin/env python3

import signal
import subprocess
import threading
from subprocess import run, Popen
from time import sleep

BACKEND_PORT_BASE=10000
LOCAL_DB_PORT=20000

processes = {}


def run_container(image, name, cmd=None, env={}, volumes=[], ports=[]):
    cmdline = ["docker", "run"]
    if name is not None:
        cmdline += ["--name", name]

    for key, val in env.items():
        cmdline += ["-e", "%s=%s" % (key, val)]

    for volume in volumes:
        cmdline += ["-v", volume]

    for port in ports:
        cmdline += ["-p", port]

    cmdline += [image]

    if cmd is not None:
        if type(cmd) is not list:
            cmd = [ cmd ]
        cmdline += cmd

    proc = Popen(cmdline, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    processes[name] = {
        'name'   : name,
        'proc'   : proc,
        'pipe'   : proc.stdout,
        'docker' : True
    }


def kill_processes():
    for name, process in [v for v in processes.items()]:
        docker = process.get('docker', False)
        if docker:
            run(["docker", "rm", "-f", name], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        else:
            proc = process['proc']
            proc.terminate()
            proc.wait()
        del processes[name]


def run_postgresql(name, image='postgis/postgis', env={}, ports=[]):
    e = {
        'POSTGRES_PASSWORD' : 'irtlab7lw2',
        'PGDATA'            : '/var/lib/postgresql/data/pgdata'
    }

    for key, val in env.items():
        e[key] = val

    return run_container(image, name=name, cmd=['postgres', '-c', 'log_statement=all'], env=e, volumes=[
        f'/srv/sensql/data/{name}:/var/lib/postgresql/data'
    ], ports=ports)


def run_backend_db(number):
    global BACKEND_PORT_BASE
    port = BACKEND_PORT_BASE
    BACKEND_PORT_BASE += 1
    run_postgresql(name=f'backend{number}', image='sensql/storage', env={
        'BACKEND_NUMBER': f'{number}'
    }, ports=[
        f"0.0.0.0:{port}:5432"
    ])
    return port


def run_publisher(number, port):
    name=f'publisher{number}'
    proc = Popen(['publisher/venv/bin/python', '-u', 'publisher/app.py', str(number), str(port)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    processes[name] = {
        'name'   : name,
        'proc'   : proc,
        'pipe'   : proc.stdout,
        'docker' : False
    }


def run_registry(name='registry'):
    proc = Popen(['registry/venv/bin/python', '-u', 'registry/app.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    processes[name] = {
        'name'   : name,
        'proc'   : proc,
        'pipe'   : proc.stdout,
        'docker' : False
    }


def run_local_db():
    return run_postgresql('local-db', image='sensql/local-db', ports=[
        f"{LOCAL_DB_PORT}:5432"
    ])


def logger_thread(name, pipe, spaces):
    sep = ' ' * spaces
    for line in iter(pipe.readline, b''):
        print(f'{name}{sep}| {line.rstrip().decode("utf-8")} ')


def start_loggers():
    max_len = 0
    for name in processes.keys():
        if len(name) > max_len:
            max_len = len(name)

    for name, obj in processes.items():
        pipe = obj['pipe']
        t = threading.Thread(target=logger_thread, args=(name, pipe, max_len - len(name) + 1))
        t.start()


def main():
    run_local_db()
    run_registry()

    for i in range(1, 100 + 1):
       port = run_backend_db(i)
       run_publisher(i, port)

    start_loggers()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass

    kill_processes()


if __name__ == '__main__':
    main()
