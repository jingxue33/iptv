#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPTV镜像仓库主程序入口
负责初始化配置、启动服务和执行更新任务
"""

import os
import json
import logging
import time
from datetime import datetime
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入自定义模块 - 简化导入路径
try:
    # 尝试直接导入
    from iptv_fetcher import IPTVFetcher
    from iptv_processor import IPTVProcessor
    from utils import setup_logging, ensure_directory
except ImportError:
    # 如果失败，使用原路径
    from scripts.iptv_fetcher import IPTVFetcher
    from scripts.iptv_processor import IPTVProcessor
    from scripts.utils import setup_logging, ensure_directory

# 配置日志
setup_logging()
logger = logging.getLogger(__name__)

def load_config(config_path=None):
    """加载配置文件"""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info(f"成功加载配置文件: {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"配置文件未找到: {config_path}")
        # 使用默认配置
        default_config = {
            "update_interval": 2,
            "providers": {},
            "output": {
                "formats": ["m3u", "txt"],
                "save_path": os.path.join(os.path.dirname(__file__), '..', 'output')
            },
            "channel_groups": {
                "cctv": "📺央视频道",
                "satellite": "📡卫视频道",
                "cartoon": "🪁动画频道"
            }
        }
        logger.info("使用默认配置")
        return default_config
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return {}

def update_channels(config=None):
    """更新频道数据的主要函数
    可被调度器调用
    """
    if config is None:
        config = load_config()
    
    # 确保输出目录存在
    output_dir = config.get('output', {}).get('save_path', os.path.join(os.path.dirname(__file__), '..', 'output'))
    ensure_directory(output_dir)
    ensure_directory(os.path.join(output_dir, 'm3u'))
    ensure_directory(os.path.join(output_dir, 'txt'))
    
    try:
        # 初始化抓取器和处理器
        fetcher = IPTVFetcher(config)
        processor = IPTVProcessor(config)
        
        # 抓取所有启用的频道源
        all_channels = fetcher.fetch_all_channels()
        
        # 处理频道数据
        if all_channels:
            processor.process_channels(all_channels)
            logger.info(f"成功更新 {len(all_channels)} 个频道")
            return True
        else:
            logger.warning("未获取到任何频道数据")
            return False
            
    except Exception as e:
        logger.error(f"更新频道时出错: {e}", exc_info=True)
        return False

def main():
    """主程序入口函数"""
    logger.info("=== IPTV镜像库服务启动 ===")
    
    try:
        # 加载配置
        config = load_config()
        if not config:
            logger.error("无法加载配置，程序将退出")
            return
        
        # 执行频道更新
        logger.info("开始更新频道数据")
        start_time = time.time()
        
        success = update_channels(config)
        
        end_time = time.time()
        logger.info(f"频道更新{'成功' if success else '失败'}，耗时: {end_time - start_time:.2f} 秒")
        
    except Exception as e:
        logger.error(f"程序执行出错: {e}", exc_info=True)
    finally:
        logger.info("=== IPTV镜像库服务结束 ===")

if __name__ == "__main__":
    main()