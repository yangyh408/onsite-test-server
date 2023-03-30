```
onsite_test_server
├── conf
│   ├── logging.conf	
│   └── test_server.conf
├── log
│   ├── submit.log	
│   ├── database.log	
│   └── history.log
├── temp
├── scenes
└── tester
```

+   文件结构：

    1.   conf文件夹：评测程序涉及的配置文件

    2.   log文件夹：评测程序的日志文件

    3.   temp文件夹：用于存放用户输出轨迹等临时文件（数据上传至又拍云后会自动删除）

    4.   scenes文件夹：存放评测的场景信息

         ```
         scenes
         ├── A
         │   ├── highway
         │   ├── ramp
         │   ├── intersection
         │   ├── complex
         │   └── test
         └── B
             ├── highway
             ├── ramp
             ├── intersection
             └── complex
         ```

         +   一级文件夹：A、B代表试卷类型(paperType)，在到达竞赛指定日期后自动切换
         +   二级文件夹：
             1.   highway：高速路基本段专项赛
             2.   ramp：高速路汇入汇出区专项赛
             3.   intersection：交叉口专项赛
             4.   complex：综合赛
             5.   test：内测赛（调试）使用的输入场景文件夹，仅在A卷下有此文件夹
         +   三级文件夹：统一命名为`inputs`并在该文件夹下添加各场景文件夹

    5.   tester文件夹：评测程序主体

         +   `__main__.py` 运行评测主程序（通过subprocess多进程并行）
         +   `load_conf.py`加载评测部分配置文件test_server.conf，确定评测的competitionId与场景文件夹对应情况
         +   `connector.py`通过连接池维护的数据库连接类
         +   `logger.py`用于加载logging配置并生成logger对象供项目日志记录使用
         +   `tester.py`针对单一提交的测评流程控制
         +   `docker_tool.py`拉取镜像、测试镜像、删除镜像
         +   `run_evaluator.py`运行评价体系
         +   `uploader.py`上传文件至又拍云

    6.   requirements.txt：python环境依赖

+   更新场景
    1.   场景文件统一放置在scenes文件夹下
    2.   一级文件夹根据试卷类型分别创建或进入A、B、C文件夹中
    3.   二级文件夹根据试卷类型选择对应分项赛事的文件夹
    4.   场景文件夹放入对应赛事文件夹下的inputs文件中

+ 更新评价体系

    1.   在tester/evaluate文件夹下修改评价体系代码
    2.   运行tester/run_evaluator.py保证程序顺利执行
    3.   查看temp/test_outputs文件夹中score.csv文件是否为期望输出信息