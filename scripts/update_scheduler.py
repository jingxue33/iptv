#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPTV频道自动更新调度模块
负责按照配置的时间间隔自动更新频道数据
"""

import os
import sys
import time
import logging
import schedule
from datetime import datetime

# 添加上级目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 导入自定义模块 - 适配不同的运行环境
try:
    # 直接导入（在scripts目录内运行时）
    from main import update_channels
    from utils import setup_logging, ensure_directory
except ImportError:
    # 相对导入（在项目根目录运行时）
    from scripts.main import update_channels
    from scripts.utils import setup_logging, ensure_directory

logger = logging.getLogger(__name__)

class IPTVScheduler:
    def __init__(self, config):
        self.config = config
        self.update_interval = config.get('update_interval', 2)  # 默认2天更新一次
        self.running = False
    
    def update_task(self):
        """执行频道更新任务"""
        logger.info(f"[{datetime.now()}] 开始执行定时更新任务")
        try:
            # 调用主程序中的更新函数
            update_channels(self.config)
            logger.info(f"[{datetime.now()}] 定时更新任务执行完成")
        except Exception as e:
            logger.error(f"[{datetime.now()}] 定时更新任务执行失败: {e}")
    
    def setup_schedule(self):
        """设置定时任务"""
        # 根据配置的更新间隔设置定时任务
        if self.update_interval <= 1:
            # 如果更新间隔小于等于1天，使用小时单位
            logger.info(f"设置更新频率: 每 {self.update_interval * 24} 小时")
            schedule.every(self.update_interval * 24).hours.do(self.update_task)
        else:
            # 否则使用天单位
            logger.info(f"设置更新频率: 每 {self.update_interval} 天")
            schedule.every(self.update_interval).days.do(self.update_task)
        
        # 立即执行一次更新任务
        logger.info("首次启动时立即执行一次更新任务")
        self.update_task()
    
    def start(self):
        """启动调度器"""
        self.running = True
        logger.info("IPTV自动更新调度器已启动")
        
        # 设置定时任务
        self.setup_schedule()
        
        try:
            # 保持运行，不断检查定时任务
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logger.info("收到中断信号，停止调度器")
            self.stop()
        except Exception as e:
            logger.error(f"调度器运行出错: {e}")
            self.stop()
    
    def stop(self):
        """停止调度器"""
        self.running = False
        logger.info("IPTV自动更新调度器已停止")

if __name__ == "__main__":
    # 配置日志
    setup_logging()
    
    # 加载配置
    import json
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 确保输出目录存在
        output_path = config.get('output', {}).get('save_path', './output')
        ensure_directory(os.path.join(output_path, 'm3u'))
        ensure_directory(os.path.join(output_path, 'txt'))
        
        # 启动调度器
        scheduler = IPTVScheduler(config)
        scheduler.start()
    except Exception as e:
        logger.error(f"程序启动失败: {e}")
        sys.exit(1)