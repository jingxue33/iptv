#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPTV频道源获取模块
负责从各种来源获取IPTV频道数据
"""

import os
import re
import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

logger = logging.getLogger(__name__)

class IPTVFetcher:
    def __init__(self, config):
        self.config = config
        self.sources = config.get('sources', {})
        self.timeout = 30  # 请求超时时间
    
    def fetch_url_content(self, url):
        """从URL获取内容"""
        try:
            response = requests.get(url, timeout=self.timeout)
            response.encoding = 'utf-8'
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"获取URL内容失败 {url}: {e}")
            return None
    
    def read_local_file(self, file_path):
        """读取本地文件内容"""
        try:
            full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.error(f"本地文件不存在: {full_path}")
                return None
        except Exception as e:
            logger.error(f"读取本地文件失败 {file_path}: {e}")
            return None
    
    def parse_m3u_content(self, content, source_name):
        """解析M3U格式的内容"""
        channels = []
        if not content:
            return channels
        
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('#EXTINF:'):
                # 提取频道信息
                tvg_name_match = re.search(r'tvg-name="([^"]*)"', line)
                tvg_id_match = re.search(r'tvg-id="([^"]*)"', line)
                tvg_logo_match = re.search(r'tvg-logo="([^"]*)"', line)
                group_title_match = re.search(r'group-title="([^"]*)"', line)
                
                # 频道名称
                channel_name = line.split(',')[-1].strip()
                if channel_name.startswith('#'):
                    i += 1
                    continue
                
                # URL在下一行
                if i + 1 < len(lines):
                    url = lines[i + 1].strip()
                    if url and not url.startswith('#'):
                        channel = {
                            'name': channel_name,
                            'url': url,
                            'source': source_name,
                            'tvg_id': tvg_id_match.group(1) if tvg_id_match else None,
                            'tvg_logo': tvg_logo_match.group(1) if tvg_logo_match else None,
                            'group_title': group_title_match.group(1) if group_title_match else '未分类',
                            'tvg_name': tvg_name_match.group(1) if tvg_name_match else None,
                            'updated_at': datetime.now().isoformat()
                        }
                        channels.append(channel)
                i += 2
            else:
                i += 1
        
        return channels
    
    def fetch_source_channels(self, source_name, source_config):
        """从单个源获取频道"""
        if not source_config.get('enabled', False):
            logger.info(f"源 {source_name} 已禁用，跳过")
            return []
        
        logger.info(f"开始获取源 {source_name} 的频道")
        channels = []
        
        # 获取内容
        if 'url' in source_config:
            content = self.fetch_url_content(source_config['url'])
        elif 'file' in source_config:
            content = self.read_local_file(source_config['file'])
        else:
            logger.error(f"源 {source_name} 配置错误，缺少url或file")
            return []
        
        # 解析内容
        if content:
            channels = self.parse_m3u_content(content, source_name)
            logger.info(f"从源 {source_name} 获取了 {len(channels)} 个频道")
        
        return channels
    
    def fetch_all_channels(self):
        """从所有启用的源获取频道"""
        all_channels = []
        max_workers = 5  # 最大线程数
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_source = {}
            for source_name, source_config in self.sources.items():
                if source_config.get('enabled', False):
                    future = executor.submit(self.fetch_source_channels, source_name, source_config)
                    future_to_source[future] = source_name
            
            # 收集结果
            for future in as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    channels = future.result()
                    all_channels.extend(channels)
                except Exception as e:
                    logger.error(f"处理源 {source_name} 时出错: {e}")
        
        logger.info(f"总共获取了 {len(all_channels)} 个频道")
        return all_channels