@echo off
echo ========================================
echo ContestTrade 自动安装脚本
echo ========================================
echo.

echo 正在检查 Python 安装...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python 未安装，请先安装 Python 3.10 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo Python 已安装，版本信息：
python --version
echo.

echo 正在检查 pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip 未安装，正在安装...
    python -m ensurepip --upgrade
)

echo 正在升级 pip...
python -m pip install --upgrade pip
echo.

echo 正在安装项目依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 依赖安装失败，请检查网络连接或手动安装
    pause
    exit /b 1
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 下一步：
echo 1. 编辑 config.yaml 文件，配置您的 API 密钥
echo 2. 运行命令启动程序：python -m cli.main run
echo.
echo 详细说明请查看 安装指南.md 文件
echo.
pause
