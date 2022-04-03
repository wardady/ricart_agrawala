from __future__ import annotations

import sys
import threading
from random import uniform
from time import sleep

from ricart_agrawala.states import ProcessState


class RAProcess(threading.Thread):
    def __init__(self, id: int, ports: dict[int, int]):
        super().__init__()
        self.id = id
        self.port = ports[self.id]
        self.peer_ports = [v for k, v in ports.items() if k != self.id]
        self.state = ProcessState.DO_NOT_WANT
        self.time_out_upper_bound = 5
        self.time_out_cs = 10
        self.running = True

    def run(self):
        while self.running:
            sleep(uniform(5, self.time_out_upper_bound))
            self.state = ProcessState.WANTED
            # TODO: Acquire the critical section
            # TODO: Execute CS
            # TODO: Release CS


class MainProcess(threading.Thread):
    def __init__(self, process_num: int, host: str, initial_port: int):
        super().__init__()
        self.process_num = process_num
        process_ports = {i: initial_port + i for i in range(0, process_num)}
        self.processes = [RAProcess(i, process_ports) for i in range(0, process_num)]
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
                p.time_out_cs = t

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
