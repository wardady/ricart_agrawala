from __future__ import annotations

import sys
import threading
import time
import socket as sckt
from random import uniform

from ricart_agrawala.states import ProcessState


class RAProcess(threading.Thread):
    def __init__(self, id: int, host: str, ports: dict[int, int]):
        super().__init__()
        self.id = id
        self.host = host
        self.port = ports[self.id]
        self.init_socket()
        self.peer_ports = [v for k, v in ports.items() if k != self.id]
        self.state = ProcessState.DO_NOT_WANT
        self.time_out_upper_bound = 5
        self.time_out_cs = 10
        self.running = True
        self.delay_start = None
        self.delay = None

    def init_socket(self):
        self.socket = sckt.socket(sckt.AF_INET, sckt.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.setsockopt(sckt.SOL_SOCKET, sckt.SO_REUSEADDR, 1)
        self.socket.settimeout(1)

    def run(self):
        self.socket.listen()
        while self.running:
            self.communicate()
            if self.state == ProcessState.DO_NOT_WANT:
                if self.delay_start is None:
                    self.delay_start = time.time()
                    self.delay = uniform(5, self.time_out_upper_bound)
                self.on_do_not_want()
            if self.state == ProcessState.WANTED:
                self.on_wanted()
            if self.state == ProcessState.HELD:
                self.on_held()

    def on_do_not_want(self):
        if time.time() - self.delay_start >= self.delay:
            self.delay_start = None
            self.delay = None
            self.state = ProcessState.WANTED

    def on_wanted(self):
        if time.time() - self.time_out_cs >= self.delay:
            self.time_out_cs = None
            self.delay = None
            self.state = ProcessState.HELD

    def on_held(self):
        # TODO:
        pass

    def communicate(self):
        try:
            connection, client_address = self.socket.accept()
            message = connection.recv(1024).decode('utf-8')
            request, src_port = message.split()
            if self.state == ProcessState.DO_NOT_WANT:
                self.send_message(src_port, "ok")
            elif self.state == ProcessState.WANTED:
                # TODO: check that all responses are ok?
                pass
            elif self.state == ProcessState.HELD:
                # TODO:
                pass

        except sckt.timeout:
            pass

    def send_message(self, port, message):
        socket = sckt.socket(sckt.AF_INET, sckt.SOCK_STREAM)
        socket.connect((self.host, port))
        socket.send(f"{message} {self.port}".encode('utf-8'))


class MainProcess(threading.Thread):
    def __init__(self, process_num: int, host: str, initial_port: int):
        super().__init__()
        self.process_num = process_num
        process_ports = {i: initial_port + i for i in range(0, process_num)}
        self.processes = [RAProcess(i, host, process_ports) for i in range(0, process_num)]
        self.running = True

    def join(self, timeout: float | None = ...) -> None:
        super().join()
        for p in self.processes:
            p.running = False
        for p in self.processes:
            p.join()

    def execute_command(self):
        try:
            command = input("$ ")
            print(f"Received command: {command}")
            command = command.strip().split()
            command = list(map(lambda x: x.lower(), command))
            if len(command) > 2:
                print(f"Invalid command: {command[0]}", file=sys.stderr)
            if command[0] == "list":
                return self.list_processes()
            elif command[0] == "time-cs":
                if len(command) != 2:
                    print("time-cs requires an argument.", file=sys.stderr)
                else:
                    return self.time_cs(int(command[1]))
            elif command[0] == "time-p":
                if len(command) != 2:
                    print("time-p requires an argument.", file=sys.stderr)
                else:
                    return self.time_p(int(command[1]))
            else:
                print(f"Unsupported command {command[0]}", file=sys.stderr)
        except Exception as e:
            print(e, file=sys.stderr)
            print("Error while handling command! Try again.", file=sys.stderr)
        print("Supported commads: List, time-cs, time-p")

    def list_processes(self):
        for p in self.processes:
            print(f"P{p.id}, {p.state}")

    def time_cs(self, t: int):
        if t < 10:
            print(f"Value must be >= 10. Got {t}", file=sys.stderr)
        else:
            for p in self.processes:
                p.time_out_cs = uniform(10, t)

    def time_p(self, t: int):
        if t < 5:
            print(f"Value must be >= 5. Got: {t}", file=sys.stderr)
        else:
            for p in self.processes:
                p.time_out_upper_bound = t

    def run(self):
        for p in self.processes:
            p.start()
        while self.running:
            self.execute_command()
