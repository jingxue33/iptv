#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPTV频道处理模块
负责处理频道数据并生成M3U和TXT格式的文件
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class IPTVProcessor:
    def __init__(self, config):
        self.config = config
        self.output_path = config.get('output', {}).get('save_path', './output')
        self.formats = config.get('output', {}).get('formats', ['m3u'])
        self.channel_groups = config.get('channel_groups', {})
        
        # 从配置文件读取目标频道列表
        self.target_channels = config.get('target_channels', {
            'cctv': [],
            'satellite': [],
            'cartoon': []
        })
        
        # 如果配置中没有目标频道，使用默认值
        if not any(self.target_channels.values()):
            self.target_channels = {
                'cctv': [
                    'CCTV-1', 'CCTV-2', 'CCTV-3', 'CCTV-4', 'CCTV-5',
                    'CCTV-6', 'CCTV-7', 'CCTV-8', 'CCTV-9', 'CCTV-10',
                    'CCTV-11', 'CCTV-12', 'CCTV-13', 'CCTV-14', 'CCTV-15',
                    'CCTV-16', 'CCTV-17'
                ],
                'satellite': [
                    '湖南卫视', '浙江卫视', '河南卫视', '安徽卫视', '江苏卫视',
                    '东方卫视', '东南卫视', '北京卫视', '湖北卫视', '黑龙江卫',
                    '辽宁卫视', '河北卫视', '江西卫视', '山东卫视', '山西卫视',
                    '重庆卫视', '陕西卫视', '四川卫视', '广东卫视', '深圳卫视',
                    '甘肃卫视', '广西卫视', '贵州卫视', '海南卫视', '天津卫视',
                    '吉林卫视', '内蒙古卫', '青海卫视', '西藏卫视', '新疆卫视',
                    '云南卫视', '黑龙江影视', '黑龙江少儿', '黑龙江都市',
                    '黑龙江综合', '黑龙江新闻'
                ],
                'cartoon': [
                    '少儿动画', '卡酷动画', '动漫秀场', '新动漫', '青春动漫',
                    '爱动漫', '中录动漫', '宝宝动画', 'CN卡通', '优漫卡通',
                    '金鹰卡通', '睛彩少儿', '黑莓动画', '炫动卡通', '24H国漫热播',
                    '浙江少儿', '河北少儿科教'
                ]
            }
            logger.warning("配置文件中未找到目标频道列表，使用默认频道列表")
        else:
            logger.info("从配置文件成功加载目标频道列表")
    
    def filter_channels(self, all_channels):
        """
        过滤频道：只保留指定的目标频道，并过滤可能卡顿的频道
        
        功能说明：
        1. 只保留配置文件中指定的目标频道（默认包含央视、卫视和动画频道）
        2. 自动过滤可能卡顿的频道（基于关键词识别）
        3. 将频道按组分类：央视频道、卫视频道、动画频道
        
        配置方法：
        - 修改config.json中的target_channels字段可自定义目标频道列表
        - 如需自定义卡顿频道过滤规则，可在方法中修改stutter_keywords列表
        - 频道匹配采用宽松模式，只要频道名称包含目标名称即可匹配
        """
        # 初始化分组
        filtered_channels = {
            'cctv': [],
            'satellite': [],
            'cartoon': []
        }
        
        # 记录处理的频道数量
        total_processed = 0
        total_kept = 0
        total_stutter_filtered = 0
        
        # 卡顿频道关键词列表
        stutter_keywords = ['low', '卡顿', '不流畅', 'test', '测试', '备用', '备份', 'fail', 'error']
        
        for channel in all_channels:
            total_processed += 1
            channel_name = channel['name']
            channel_url = channel['url'].lower()
            
            # 检查是否为卡顿频道
            is_stutter = any(keyword.lower() in channel_name.lower() or keyword.lower() in channel_url for keyword in stutter_keywords)
            if is_stutter:
                total_stutter_filtered += 1
                logger.debug(f"过滤卡顿频道: {channel_name}")
                continue
            
            # 检查是否为目标频道并放入相应分组
            matched = False
            for group_key, target_names in self.target_channels.items():
                for target_name in target_names:
                    # 宽松匹配，只要频道名称包含目标名称即可
                    if target_name in channel_name:
                        filtered_channels[group_key].append(channel)
                        total_kept += 1
                        matched = True
                        break
                if matched:
                    break
        
        # 移除空分组
        filtered_channels = {k: v for k, v in filtered_channels.items() if v}
        
        logger.info(f"处理了 {total_processed} 个频道，保留了 {total_kept} 个目标频道，过滤了 {total_stutter_filtered} 个可能卡顿的频道")
        return filtered_channels
    
    def generate_m3u_file(self, filtered_channels):
        """生成M3U格式的频道文件"""
        m3u_path = os.path.join(self.output_path, 'm3u', 'iptv_channels.m3u')
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(m3u_path), exist_ok=True)
        
        try:
            with open(m3u_path, 'w', encoding='utf-8') as f:
                # M3U文件头
                f.write('#EXTM3U x-tvg-url="https://epg.51zmt.top:8888/e.xml.gz"\n')
                
                # 遍历所有频道并写入文件
                for group_key, channels in filtered_channels.items():
                    group_name = self.channel_groups.get(group_key, group_key)
                    logger.info(f"写入组 {group_name} 的 {len(channels)} 个频道")
                    for channel in channels:
                        # 简化的EXTINF行
                        f.write(f'#EXTINF:-1 group-title="{group_name}",{channel["name"]}\n')
                        f.write(f'{channel["url"]}\n')
            
            logger.info(f"M3U文件已生成: {m3u_path}")
            return m3u_path
        except Exception as e:
            logger.error(f"生成M3U文件时出错: {str(e)}")
            raise
    
    def generate_txt_file(self, filtered_channels):
        """生成TXT格式的频道文件"""
        txt_path = os.path.join(self.output_path, 'txt', 'iptv_channels.txt')
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            # 写入文件头部信息
            f.write(f'# IPTV频道列表 - 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write('# 格式: 频道名称,频道URL\n\n')
            
            # 按组输出频道
            for group_key, channels in filtered_channels.items():
                group_name = self.channel_groups.get(group_key, group_key)
                # 写入组名
                f.write(f'# {group_name}\n')
                
                # 写入该组的所有频道
                for channel in channels:
                    f.write(f'{channel["name"]},{channel["url"]}\n')
                f.write('\n')
        
        logger.info(f"TXT文件已生成: {txt_path}")
        return txt_path
    
    def process_channels(self, all_channels):
        """处理频道数据并生成文件"""
        # 调试输出：显示前5个获取到的频道
        if all_channels:
            logger.info(f"获取到的前5个频道示例: {[channel['name'] for channel in all_channels[:5]]}")
        
        # 过滤出目标频道（现在保留所有频道）
        filtered_channels = self.filter_channels(all_channels)
        
        # 确保所有频道都能被写入，不进行特殊排序
        # 直接使用过滤后的频道
        
        # 生成相应格式的文件
        if 'm3u' in self.formats:
            self.generate_m3u_file(filtered_channels)
        
        if 'txt' in self.formats:
            self.generate_txt_file(filtered_channels)
        
        logger.info("频道处理完成，所有文件已生成")