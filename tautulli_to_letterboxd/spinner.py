from sys import stdout
from time import sleep

class Loading:
    '''Bouncing bar spinner for CLI'''
    
    def __init__(self, width=10, block='==='):
        self.width = width
        self.block = block
        self.pos = 0
        self.dir = 1
        self.block_len = len(block)
        self.last_len = 0
        # ANSI colors
        self.color_spinner = '\033[36m'  # cyan
        self.color_success = '\033[32m'  # green
        self.color_fail = '\033[31m'     # red
        self.color_reset = '\033[0m'

    def start(self, text=''):
        bar = [' '] * self.width
        for i, ch in enumerate(self.block):
            bar[self.pos + i] = ch

        output = f"{self.color_spinner}[{''.join(bar)}]{self.color_reset} {text}"
        padding = max(0, self.last_len - len(output))
        stdout.write(f'\r' + output + ' ' * padding)
        stdout.flush()
        self.last_len = len(output)

        self.pos += self.dir
        if self.pos <= 0 or self.pos >= self.width - self.block_len:
            self.dir *= -1

        sleep(0.05)

    def succeed(self, message):
        stdout.write(f'{self.color_success}\r✔{self.color_reset} {message}\n')
        stdout.flush()
        self.last_len = 0

    def fail(self, message):
        stdout.write(f'{self.color_fail}\r✖{self.color_reset} {message}\n')
        stdout.flush()
        self.last_len = 0
