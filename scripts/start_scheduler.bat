@echo off
:: IPTV自动更新调度器启动脚本
:: 用于启动后台更新服务，按照配置的时间间隔自动更新频道

setlocal

:: 设置项目根目录
set "PROJECT_ROOT=%~dp0.."
set "SCRIPTS_DIR=%PROJECT_ROOT%\scripts"
set "LOG_DIR=%PROJECT_ROOT%\logs"
set "LOG_FILE=%LOG_DIR%\scheduler_%date:~0,4%%date:~5,2%%date:~8,2%.log"

:: 创建logs目录
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: 输出信息
echo =================================================
echo IPTV自动更新调度器
set datetime=%date:~0,4%-%date:~5,2%-%date:~8,2% %time:~0,2%:%time:~3,2%:%time:~6,2%
echo 启动时间: %datetime%
echo =================================================
echo 此窗口将保持运行，请勿关闭！
echo 自动更新频率: 每两天（根据配置文件）
echo 日志文件: %LOG_FILE%
echo =================================================

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python。请确保已安装Python并添加到系统路径。
    pause
    exit /b 1
)

:: 检查必要的Python库
echo 检查必要的Python库...
python -c "import schedule" >nul 2>&1
if %errorlevel% neq 0 (
    echo 安装必要的Python库...
    pip install schedule >nul 2>&1
    if %errorlevel% neq 0 (
        echo 错误: 安装Python库失败。
        pause
        exit /b 1
    )
)

:: 进入scripts目录
cd /d "%SCRIPTS_DIR%"

:: 启动调度器
echo 正在启动IPTV自动更新调度器...
python update_scheduler.py >> "%LOG_FILE%" 2>&1

:: 如果程序意外退出
if %errorlevel% neq 0 (
    echo 调度器意外退出！
    echo 错误代码: %errorlevel%
    echo 请查看日志文件获取详细信息: %LOG_FILE%
    pause
    exit /b 1
)

endlocal