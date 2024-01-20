import os
from enum import Enum
import threading
import subprocess as sb
from time import time_ns
import json
class ResultEnum(Enum):
    OK = 1
    WA = 2
    TL = 3
    ML = 4
    RE = 5
    CE = 6 


LANGS = ['c++']

class CodeTester:

    def __init__(self, code: str, lang: str) -> None:
        test_set, language = lang.split('_')
        if language not in LANGS:
            raise Exception('Invalid language')
        path = f'tests/{test_set}'
        if not os.path.isdir(path):
            raise Exception('Invalid test set')
        self.__n_tests = len(os.listdir(path)) // 3
        self.__language = language
        self.__code = code
        self.__dir = path + '/{name}.txt'

    def n_tests(self) -> int:
        return self.__n_tests
    
    def test(self, test: int):
        LANG_TESTS = {
            'c++': self.__test_cpp
        }
        return LANG_TESTS[self.__language](test)
    
    def __test_cpp(self, test: int):
        sin, sout, data = '', '', ''
        with open(self.__dir.format(name=str(test) + 'in'), 'r') as f:
            sin = f.read()
        with open(self.__dir.format(name=str(test) + 'out'), 'r') as f:
            sout = f.read()
        with open(self.__dir.format(name=str(test) + 'c'), 'r') as f:
            cntxt = json.load(f)
        
        
        temporary_file_name = f'temp{threading.get_ident()}'
        with open(temporary_file_name + '.cpp', 'w') as f:
            f.write(self.__code)

        try:
            sb.check_call(f"g++ {temporary_file_name}.cpp", shell=True)
        except:
            os.remove(f'{temporary_file_name}.cpp')
            return {'result': ResultEnum.CE, 'time': 0, 'memory': 0}
        times = []
        result = ResultEnum.OK
        for i in range(10):
            timer_start = time_ns()
            try:
                output = sb.run(f"./a.out", shell=True, input=sin, capture_output=True, text=True, timeout=cntxt['max_time'] / 500)
            except:
                result = ResultEnum.TL
                times.append(cntxt['max_time'] * 2000000)
                break
            if output.returncode != 0:
                result = ResultEnum.RE
                break
            timer_end = time_ns()
            times.append(timer_end - timer_start)
            if output.stdout != sout:
                result = ResultEnum.WA
                break
        
        os.remove(f'{temporary_file_name}.cpp')
        os.remove('a.out')

        if len(times) == 0:
            avg_time = 0
        else:
            avg_time = sum(times) / len(times) / 1000000
        memory = 0
        if avg_time > cntxt['max_time']:
            result = ResultEnum.TL
        if memory > cntxt['max_mem']:
            result = ResultEnum.ML

        return {'result': result, 'time': avg_time, 'memory': memory}

# UNIT TESTS
# if __name__ == '__main__':
#     code = '#include<iostream>\nusing namespace std;\nint main() { int a, b, c; cin>>a>>b>>c; cout<<c<<" "<<b<<" "<<a<<endl; return 0; }'
#     code_tester = CodeTester(code, '1_c++')
#     t1 = code_tester.test(1)
#     print(t1)
#     assert t1['result'] == ResultEnum.OK


#     code = '#include<iostream>\nusing namespace std;\nint main() { int a, b, c; cin>>a>>b>>c; cout<<c<<" "<<a<<" "<<b<<endl; return 0; }'
#     code_tester = CodeTester(code, '1_c++')
#     t1 = code_tester.test(1)
#     print(t1)
#     assert t1['result'] == ResultEnum.WA


#     code = '#include<iostream>\nusing namespace std;\nint main() { int a, b, c; cin>>a>>b>>c; for(int i=0;i<99999999;i++); cout<<c<<" "<<b<<" "<<a<<endl; return 0; }'
#     code_tester = CodeTester(code, '1_c++')
#     t1 = code_tester.test(1)
#     print(t1)
#     assert t1['result'] == ResultEnum.TL


#     code = '#include<iostream>\nusing namespace std;\nint main() { int a, b, c; cin>>a>>b>>c; cout<<c<<" "<<b<<" "<<a<<endl; *((int*)0)=0; return 0; }'
#     code_tester = CodeTester(code, '1_c++')
#     t1 = code_tester.test(1)
#     print(t1)
#     assert t1['result'] == ResultEnum.RE


#     code = ''
#     code_tester = CodeTester(code, '1_c++')
#     t1 = code_tester.test(1)
#     print(t1)
#     assert t1['result'] == ResultEnum.CE
############
