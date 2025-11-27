# IPTV系统

这是一个IPTV频道管理系统，用于获取、处理和过滤IPTV频道列表，并生成可用于播放器的M3U文件。

## 功能特性

- 自动从多个源获取IPTV频道数据
- 支持频道过滤，只保留指定的目标频道（央视、卫视、动画等）
- 实现卡顿频道检测和过滤
- 按频道类型自动分组（央视频道、卫视频道、动画频道）
- 生成标准M3U格式文件和TXT列表文件
- 支持定时更新IPTV频道数据

## 目录结构

```
iptv/
├── config/              # 配置文件目录
│   └── config.json      # 主配置文件
├── scripts/             # 脚本文件目录
│   ├── iptv_fetcher.py  # 频道数据获取模块
│   ├── iptv_processor.py # 频道数据处理模块
│   ├── main.py          # 主程序入口
│   ├── update_scheduler.py # 定时更新调度器
│   ├── utils.py         # 工具函数
│   ├── setup_scheduled_task.ps1 # 定时任务设置脚本
│   ├── start_scheduler.bat # 启动调度器批处理
│   └── update_iptv.bat  # 更新IPTV批处理
├── sources/             # 源文件目录
│   └── unicom.txt       # 联通源频道列表
├── output/              # 输出文件目录
│   ├── m3u/             # M3U文件输出目录
│   └── txt/             # TXT文件输出目录
├── requirements.txt     # Python依赖文件
└── .gitignore           # Git忽略文件
```

## 安装和使用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置文件设置

编辑 `config/config.json` 文件，根据需要调整配置：

- `target_channels`: 设置要保留的目标频道列表
- `output_directories`: 设置输出文件路径
- `update_interval`: 设置定时更新间隔（秒）

### 3. 运行程序

```bash
python scripts/main.py
```

### 4. 设置定时更新（Windows）

运行 `setup_scheduled_task.ps1` 脚本创建Windows定时任务，或者直接运行 `start_scheduler.bat` 启动后台更新服务。

## 频道过滤说明

系统会根据 `config.json` 中的 `target_channels` 配置，只保留以下三类频道：

1. **央视频道**：CCTV系列频道
2. **卫视频道**：各省级卫视频道
3. **动画频道**：儿童动画相关频道

同时会自动过滤包含特定关键词（如"low"、"卡顿"等）的卡顿频道。

## 自定义配置

- 修改 `target_channels` 可添加或移除目标频道
- 修改 `stutter_keywords` 可自定义卡顿频道的过滤关键词
- 系统使用宽松匹配规则，只要频道名称中包含目标关键词即可匹配

## 注意事项

- 请确保网络连接正常，以便获取最新的频道数据
- 输出目录会自动创建，请确保有写入权限
- 定期更新可能会消耗一定的网络资源

## License

MIT
