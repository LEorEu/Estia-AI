<#  run_claude_template.ps1  
# 使用方法：
# 1. 复制此文件为 run_claude.ps1 
# 2. 确保已创建 config/env_local.ps1 配置文件
#>

param(
    [string]$Project = "D:/Estia-AI"
)

# ---------- 0. 报错即停 ----------
$ErrorActionPreference = "Stop"

# ---------- 1. 激活 conda ----------
conda activate estia

# ---------- 2. 切 Node 版本 ----------
# nvm use 20.15.0

# ---------- 3. 进项目目录 ----------
Set-Location $Project

# ---------- 4. 从配置文件加载环境变量 ----------
$envConfigFile = "$Project\config\env_local.ps1"
if (Test-Path $envConfigFile) {
    Write-Host "✅ 加载环境配置: $envConfigFile" -ForegroundColor Green
    . $envConfigFile
} else {
    Write-Host "❌ 环境配置文件不存在: $envConfigFile" -ForegroundColor Red
    Write-Host "请先创建配置文件：" -ForegroundColor Yellow
    Write-Host "  cp config\env_template.ps1 config\env_local.ps1" -ForegroundColor Cyan
    Write-Host "  然后编辑 config\env_local.ps1 配置API密钥" -ForegroundColor Cyan
    exit 1
}

# ---------- 5. 安全地更新 .claude.json ----------
if ($env:ANTHROPIC_API_KEY -and $env:ANTHROPIC_API_KEY -ne "sk-ant-oat01-YOUR-TOKEN-HERE") {
    $configFile = "C:\Users\zero_\.claude.json"  # 根据你的用户名调整
    $keySnippet = $env:ANTHROPIC_API_KEY.Substring($env:ANTHROPIC_API_KEY.Length - 20)
    
    $jsonContent = if (Test-Path $configFile) { Get-Content $configFile -Raw -Encoding UTF8 } else { "null" }
    $keyExists = $jsonContent | jq --arg key $keySnippet '(.customApiKeyResponses.approved // []) | any(. == $key)'
    
    if ($keyExists -ne 'true') {
        $newJson = $jsonContent | jq --arg key $keySnippet '(. // {}) | .customApiKeyResponses.approved |= ([.[]?, $key] | unique)'
        [System.IO.File]::WriteAllText($configFile, $newJson)
        Write-Host "✅ 已更新Claude配置文件" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  API密钥未正确配置" -ForegroundColor Yellow
}

Write-Host "🚀 环境配置完成！" -ForegroundColor Green