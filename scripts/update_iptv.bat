@echo off
:: IPTV频道更新批处理文件
:: 用于立即执行频道更新

setlocal

:: 设置项目根目录
set "PROJECT_ROOT=%~dp0.."
set "SCRIPTS_DIR=%PROJECT_ROOT%\scripts"
set "LOG_FILE=%PROJECT_ROOT%\logs\update_iptv_%date:~0,4%%date:~5,2%%date:~8,2%.log"

:: 创建logs目录
if not exist "%PROJECT_ROOT%\logs" mkdir "%PROJECT_ROOT%\logs"

:: 输出信息
echo =================================================
echo IPTV频道更新工具
set datetime=%date:~0,4%-%date:~5,2%-%date:~8,2% %time:~0,2%:%time:~3,2%:%time:~6,2%
echo 执行时间: %datetime%
echo =================================================

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python。请确保已安装Python并添加到系统路径。
    pause
    exit /b 1
)

:: 进入scripts目录
cd /d "%SCRIPTS_DIR%"

:: 执行更新脚本
echo 开始更新IPTV频道数据...
python main.py > "%LOG_FILE%" 2>&1

:: 检查执行结果
if %errorlevel% equ 0 (
    echo 频道更新成功！
    echo 日志文件: %LOG_FILE%
) else (
    echo 频道更新失败！
    echo 请查看日志文件获取详细信息: %LOG_FILE%
    pause
    exit /b 1
)

echo =================================================
echo 更新完成！
echo =================================================
pause
endlocal