- temp：    用于存放用户输出轨迹等临时文件，数据上传至又拍云后会自动删除
- log:      记录运行测试的日志信息
    + logging.conf      日志格式配置文件
    + history.log       日志文件记录
- tester：  测试程序
    + __main__.py       主程序，设定相关参数后运行即可
    + tester.py         顺序执行的测试类
    + thread_tester.py  多进程执行的测试类
- requirements.txt      python环境依赖