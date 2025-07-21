<#  run_claude.ps1  # 执行方式：双击 run_claude.bat，或 PowerShell -File run_claude.ps1 -- "chat" #>

param(
    [string]$Project = "D:\Estia-AI"
)

# ---------- 0. 报错即停 ----------
$ErrorActionPreference = "Stop"

# ---------- 1. 激活 conda ----------
conda activate estia

# ---------- 2. 切 Node 版本 ----------
nvm use 20.15.0            # ← 这一步改 PATH，下面会手动刷新缓存

# ---------- 3. 进项目目录 ----------
Set-Location $Project

# ---------- 4. 设置本会话环境变量 ----------
$Env:ANTHROPIC_BASE_URL   = "https://relay01.gaccode.com/claudecode"
# $Env:ANTHROPIC_AUTH_TOKEN = "sk-ant-oat01-e108b9b0d69a97f63b10b1fd8e1e12720dae21eabb360a9625de34fa5b724f88"
$env:ANTHROPIC_API_KEY = "sk-ant-oat01-e108b9b0d69a97f63b10b1fd8e1e12720dae21eabb360a9625de34fa5b724f88"

$newJson = $(if (Test-Path "C:\Users\asus\.claude.json") { Get-Content "C:\Users\asus\.claude.json" -Raw } else { "null" }) | jq --arg key "$($env:ANTHROPIC_API_KEY.Substring($env:ANTHROPIC_API_KEY.Length - 20))" '(. // {}) | .customApiKeyResponses.approved |= ([.[]?, $key] | unique)'; [System.IO.File]::WriteAllText("C:\Users\asus\.claude.json", $newJson)

$Env:HTTP_PROXY  = "http://127.0.0.1:7890"
$Env:HTTPS_PROXY = "http://127.0.0.1:7890"

$Env:http_proxy  = $Env:HTTP_PROXY
$Env:https_proxy = $Env:HTTPS_PROXY