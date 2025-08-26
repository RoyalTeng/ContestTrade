@echo off
echo ContestTrade 启动脚本
echo ===================

:: 检查 conda 是否可用
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误：找不到 conda 命令
    echo 请先运行 install.bat 安装环境
    pause
    exit /b 1
)

:: 激活环境
echo 激活 ContestTrade 环境...
call conda activate contesttrade
if %errorlevel% neq 0 (
    echo 激活环境失败，请先运行 install.bat
    pause
    exit /b 1
)

:: 检查配置文件
if not exist "config.yaml" (
    echo 错误：找不到 config.yaml 配置文件
    echo 请复制 config_template.yaml 为 config.yaml 并配置 API 密钥
    pause
    exit /b 1
)

:: 启动项目
echo 启动 ContestTrade...
echo.
"D:\Users\Administrator\miniconda3\envs\contesttrade\python.exe" -m cli.main run

:: 如果上面的命令失败，尝试直接运行
if %errorlevel% neq 0 (
    echo 尝试直接运行...
    "D:\Users\Administrator\miniconda3\envs\contesttrade\python.exe" cli\main.py run
)

pause