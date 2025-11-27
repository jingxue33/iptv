#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPTV镜像仓库工具模块
提供日志配置、目录操作等通用功能
"""

import os
import logging
from datetime import datetime

def setup_logging():
    """配置日志系统"""
    # 创建logs目录
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    ensure_directory(log_dir)
    
    # 日志文件路径
    log_file = os.path.join(log_dir, f'iptv_mirror_{datetime.now().strftime("%Y%m%d")}.log')
    
    # 配置根日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 清除已有的处理器
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def ensure_directory(directory_path):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path, exist_ok=True)
            logging.info(f"创建目录: {directory_path}")
        except Exception as e:
            logging.error(f"创建目录失败 {directory_path}: {e}")
            raise
    else:
        logging.debug(f"目录已存在: {directory_path}")

def get_file_age(file_path):
    """获取文件的年龄（秒）"""
    if not os.path.exists(file_path):
        return float('inf')
    
    file_time = os.path.getmtime(file_path)
    current_time = datetime.now().timestamp()
    return current_time - file_time

def format_size(size_bytes):
    """格式化文件大小显示"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def is_valid_url(url):
    """检查URL是否有效"""
    import re
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def sanitize_filename(filename):
    """清理文件名中的非法字符"""
    import re
    # 替换Windows文件名中的非法字符
    return re.sub(r'[<>:"/\\|?*]', '_', filename)