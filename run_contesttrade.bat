@echo off
echo ========================================
echo ContestTrade 启动脚本
echo ========================================
echo.

echo 正在创建conda环境...
call conda create -n contesttrade python=3.10 -y
if %errorlevel% neq 0 (
    echo 创建环境失败，可能环境已存在，继续...
)

echo.
echo 正在激活conda环境...
call conda activate contesttrade
if %errorlevel% neq 0 (
    echo 激活环境失败，请检查conda安装
    pause
    exit /b 1
)

echo.
echo 正在切换到项目目录...
cd /d "F:\contsttrade"

echo.
echo 正在安装项目依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)

echo.
echo ========================================
echo 正在启动ContestTrade系统...
echo ========================================
echo.

python -m cli.main run

echo.
echo 程序已结束
pause