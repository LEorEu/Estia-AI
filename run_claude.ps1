<#  run_claude.ps1  # 执行方式：双击 run_claude.bat，或 PowerShell -File run_claude.ps1 -- "chat" #>

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

# ---------- 4. 设置本会话环境变量 ----------
# 从配置文件加载环境变量
$envConfigFile = "$Project\config\env_local.ps1"
if (Test-Path $envConfigFile) {
    Write-Host "加载环境配置: $envConfigFile"
    . $envConfigFile
} else {
    Write-Host "环境配置文件不存在: $envConfigFile" -ForegroundColor Yellow
    Write-Host "请复制 config\env_template.ps1 为 config\env_local.ps1 并配置API密钥" -ForegroundColor Yellow
}

# --- 安全地更新 .claude.json ---

# 1. 准备需要用到的变量
$configFile = "C:\Users\zero_\.claude.json"
$keySnippet = $env:ANTHROPIC_API_KEY.Substring($env:ANTHROPIC_API_KEY.Length - 20)

# 2. 安全地读取配置文件内容
$jsonContent = if (Test-Path $configFile) { Get-Content $configFile -Raw -Encoding UTF8 } else { "null" }

# 3. (检查步骤) 使用 jq 检查密钥是否已存在，结果会是 "true" 或 "false" 字符串
$keyExists = $jsonContent | jq --arg key $keySnippet '(.customApiKeyResponses.approved // []) | any(. == $key)'

# 4. (执行步骤) 如果 jq 的检查结果不是 "true"，才执行添加和写入操作
if ($keyExists -ne 'true') {
    # 密钥不存在，执行添加和写入文件的逻辑
    $newJson = $jsonContent | jq --arg key $keySnippet '(. // {}) | .customApiKeyResponses.approved |= ([.[]?, $key] | unique)'
    [System.IO.File]::WriteAllText($configFile, $newJson)
}
# 如果密钥已存在，则什么也不做，直接跳过。

# 代理配置已移至环境配置文件