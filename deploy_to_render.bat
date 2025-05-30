@echo off
echo ========================================
echo 🚀 部署到 Render.com
echo ========================================

echo.
echo 📝 提交代碼到 Git...
git add .
git commit -m "Update for Render.com deployment - %date% %time%"

echo.
echo 📤 推送到 GitHub...
git push origin main

echo.
echo ✅ 代碼已推送到 GitHub
echo 現在你需要：
echo.
echo 1. 前往 https://render.com
echo 2. 登錄你的帳號
echo 3. 點擊 "New Web Service"
echo 4. 選擇你的 GitHub 倉庫
echo 5. 按照 RENDER_DEPLOYMENT.md 中的指示設置
echo.
echo 📖 詳細步驟請查看: RENDER_DEPLOYMENT.md
echo.
pause 