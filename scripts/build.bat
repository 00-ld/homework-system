@echo off
chcp 65001 >nul
echo ========================================
echo  班级作业提交系统 - 构建打包脚本
echo ========================================

echo.
echo [1/3] 安装后端依赖...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 ( echo 安装失败! & pause & exit /b 1 )
cd ..

echo.
echo [2/3] 构建前端...
cd frontend
call npm install
if %errorlevel% neq 0 ( echo npm install 失败! & pause & exit /b 1 )
call npm run build
if %errorlevel% neq 0 ( echo 前端构建失败! & pause & exit /b 1 )
cd ..

echo.
echo [3/3] 打包为可执行文件...
pip install pyinstaller
if exist "dist\homework_submission_system" rmdir /s /q "dist\homework_submission_system"
pyinstaller homework_submission_system.spec
if %errorlevel% neq 0 ( echo 打包失败! & pause & exit /b 1 )

echo.
echo ========================================
echo  打包完成！
echo  可执行文件: dist\homework_submission_system\homework_submission_system.exe
echo ========================================
pause
