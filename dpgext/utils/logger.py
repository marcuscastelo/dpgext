from dataclasses import dataclass
import re
import sys
import time
import traceback
from typing import Deque, List, Optional

from collections import deque

from enum import Enum
from termcolor import colored
import inspect

class MessageLevel(Enum):
    OUT = -1
    ERROR = 0
    WARNING = 2
    INFO = 3
    DEBUG = 4
    TRACE = 5

MESSAGE_LEVEL_COLORS = {
    MessageLevel.OUT: 'white',
    MessageLevel.ERROR: 'red',
    MessageLevel.WARNING: 'yellow',
    MessageLevel.INFO: 'green',
    MessageLevel.DEBUG: 'cyan',
    MessageLevel.TRACE: 'magenta'
}

@dataclass
class Message:
    level: MessageLevel
    message: str
    category: Optional[str] = 'general'
    time: str = ''

    def __post_init__(self):
        self.time = time.strftime("%H:%M:%S")

class Logger:
    def __init__(self):
        self.messages: Deque[Message] = deque(maxlen=1000)
        self.total_log_count: int = 0
   
    def _format_message(self, message: Message, show_time: bool = True, show_level: bool = True, show_category: bool = True):
        color = []
        time_str = message.time + ':' if show_time else ''
        level_str = ''
        
        if message.level == MessageLevel.OUT:
            color=[0, 127, 127]
        elif message.level == MessageLevel.ERROR:
            level_str = '[ERROR]'
            color=[255, 0, 0]
        elif message.level == MessageLevel.WARNING:
            level_str = '[WARNING]'
            color=[255, 127, 0]
        elif message.level == MessageLevel.INFO:
            level_str = '[INFO]'
            color=[0, 255, 0]
        elif message.level == MessageLevel.DEBUG:
            level_str = '[DEBUG]'
            color=[0, 0, 255]
        elif message.level == MessageLevel.TRACE:
            level_str = '[TRACE]'
            color=[127, 127, 127]
        else:
            level_str = '[UNKNOWN]'
            color=[255, 0, 0]
            
        level_str = level_str if show_level else ''

        category_str = f'<{message.category}>' if message.category != '' and show_category else ''

        return re.sub('[ ]+',' ',f'{time_str} {level_str} {category_str} {message.message}').strip(), color

    def _generate_stack_trace(self, initial_stack_trace: str = '') -> str:
        cf = inspect.currentframe()
        stack_trace_text = initial_stack_trace
        i = 0
        while cf is not None:
            if cf.f_code.co_filename != __file__: # don't show this file
                stack_trace_text += f'\t{i=}: {inspect.stack()[i][1]}:{cf.f_lineno}\n'

            cf = cf.f_back
            i += 1

        return self._generate_exception_stack_trace() + stack_trace_text

    def _generate_exception_stack_trace(self) -> str:
        info = sys.exc_info()
        if info is None or info[0] is None:
            return ''
        ex_type, ex_value, ex_traceback = info
        trace_back = traceback.extract_tb(ex_traceback)

        ex_stack_trace = '\n'
        
        for trace in trace_back:
            ex_stack_trace = "\t%s:%d, @%s()\n" % (trace[0], trace[1], trace[2]) + ex_stack_trace

        ex_stack_trace =  f'Exception:  {ex_type.__name__}("{ex_value}")\n\n{ex_stack_trace}'

        return ex_stack_trace

    def _log(self, message: Message, initial_stack_trace: str = ''):
        self.total_log_count += 1
        self.messages.append(message)

        if message.level in [MessageLevel.ERROR]:
            message.message += '\nStacktrace:\n' + self._generate_stack_trace(initial_stack_trace)

        print(colored(self._format_message(message)[0], MESSAGE_LEVEL_COLORS[message.level]))

        pass

    def log_out(self, message: str, category: Optional[str] = '', initial_stack_trace: str = ''):
        self._log(Message(MessageLevel.OUT, message, category), initial_stack_trace)

    def log_error(self, message: str, category: Optional[str] = '', initial_stack_trace: str = ''):
        self._log(Message(MessageLevel.ERROR, message, category), initial_stack_trace)

    def log_warning(self, message: str, category: Optional[str] = '', initial_stack_trace: str = ''):
        self._log(Message(MessageLevel.WARNING, message, category), initial_stack_trace)
    
    def log_info(self, message: str, category: Optional[str] = '', initial_stack_trace: str = ''):
        self._log(Message(MessageLevel.INFO, message, category), initial_stack_trace)

    def log_debug(self, message: str, category: Optional[str] = '', initial_stack_trace: str = ''):
        self._log(Message(MessageLevel.DEBUG, message, category), initial_stack_trace)
    
    def log_trace(self, message: str, category: Optional[str] = '', initial_stack_trace: str = ''):
        self._log(Message(MessageLevel.TRACE, message, category), initial_stack_trace)

if __name__ == "__main__":
   pass

LOGGER = Logger()