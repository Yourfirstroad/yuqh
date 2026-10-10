@echo off
chcp 65001 >nul

echo ============================================================
echo   TrendRadar 静态网页服务 (index.html 预览)
echo ============================================================
echo.

echo [模式] 静态文件服务
echo [地址] http://localhost:8899/index.html
echo [提示] 按 Ctrl+C 停止服务
echo.

uv run --no-project python -m http.server 8899 --bind 127.0.0.1

pause
