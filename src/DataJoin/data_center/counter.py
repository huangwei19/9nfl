import re
import os
import threading
mutex = threading.Lock()
class Counter(threading.Thread):
    def run(self):
        global var
        var = 0
        path = os.getcwd() + '/data_center/counter.py'
        with mutex:
            with open(path, 'r', encoding='utf-8') as fl:
                fl.seek(4)
                var_line = fl.readlines()[7]
                print(var_line)
                num = int(re.search('\d+', var_line).group()) + 1
                fl.seek(0)
                txt = fl.read().replace(var_line, '        var = ' + str(num) + '\n')
            with open(path, 'w', encoding='utf-8') as file:
                file.write(txt)
            return num
