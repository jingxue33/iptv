# PowerShell脚本 - 设置Windows计划任务
# 用于配置IPTV频道自动更新任务

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "IPTV频道自动更新计划任务配置工具" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Join-Path -Path $ScriptDir -ChildPath ".."
$UpdateScriptPath = Join-Path -Path $ScriptDir -ChildPath "update_iptv.bat"
$TaskName = "IPTV_Channel_Update"
$TaskDescription = "每两天自动更新IPTV频道列表"

# 检查更新脚本是否存在
if (-not (Test-Path -Path $UpdateScriptPath)) {
    Write-Host "错误: 未找到更新脚本: $UpdateScriptPath" -ForegroundColor Red
    exit 1
}

# 提示用户确认
Write-Host ""
Write-Host "计划任务信息:"
Write-Host "- 任务名称: $TaskName"
Write-Host "- 描述: $TaskDescription"
Write-Host "- 更新脚本: $UpdateScriptPath"
Write-Host "- 执行频率: 每两天"
Write-Host "- 执行时间: 每天早上8:00"
Write-Host ""
Write-Host "按Enter键继续，或按Ctrl+C取消..."
Read-Host

# 创建计划任务动作
$Action = New-ScheduledTaskAction -Execute "$UpdateScriptPath"

# 创建计划任务触发器（每两天一次）
$Trigger = New-ScheduledTaskTrigger -Once -At 8:00AM -RepetitionInterval (New-TimeSpan -Days 2)

# 设置计划任务主体（使用当前用户，并在用户未登录时运行）
$Principal = New-ScheduledTaskPrincipal -UserId (Get-CimInstance -ClassName Win32_ComputerSystem).UserName -LogonType S4U -RunLevel Highest

# 设置计划任务设置
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable -UseUnifiedSchedulingEngine 1

# 创建计划任务
$Task = New-ScheduledTask -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Description $TaskDescription

try {
    # 注册计划任务
    Register-ScheduledTask -TaskName $TaskName -InputObject $Task -Force
    
    Write-Host "" -ForegroundColor Green
    Write-Host "✅ 计划任务创建成功！" -ForegroundColor Green
    Write-Host "- 任务名称: $TaskName" -ForegroundColor Green
    Write-Host "- 下次执行时间: $(Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo).NextRunTime" -ForegroundColor Green
    Write-Host ""
    Write-Host "您可以通过以下方式管理此任务:"
    Write-Host "1. 打开 '任务计划程序' -> '任务计划程序库'"
    Write-Host "2. 查找并右键点击 '$TaskName' 进行管理"
    Write-Host ""
} catch {
    Write-Host "❌ 计划任务创建失败: $_" -ForegroundColor Red
    Write-Host "请确保以管理员权限运行此脚本。" -ForegroundColor Yellow
    exit 1
}

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "配置完成！" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 提示用户可以手动测试
Write-Host ""
Write-Host "您现在可以手动运行更新脚本进行测试:"
Write-Host "- 双击运行: $UpdateScriptPath"
Write-Host ""
Write-Host "按Enter键退出..."
Read-Host