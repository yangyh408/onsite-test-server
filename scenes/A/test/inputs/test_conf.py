config ={
    'test_settings': {
        'mode': 'replay',          # "interaction"为交通流仿真测试模块
        'pre_load': False,               # 是否开启场景预加载（建议开启 以提升场景初始化速度）
        'visualize': False,              # 是否进行可视化（建议关闭 开启可视化会大幅降低测试效率）
        'record_time_use': True,        # 是否记录场景仿真时间（存放在outputs文件夹下）
        'skip_exist_scene': False,      # 是否跳过outputs中已有记录的场景（可以避免程序异常中断后重新测试之前已经完成的场景）
    },
}