# env_template.ps1 - 环境变量配置模板
# 复制此文件为 env_local.ps1 并填入真实的API密钥
# env_local.ps1 会被 .gitignore 忽略，不会被提交到git

# Anthropic API配置
$env:ANTHROPIC_API_KEY = "sk-ant-oat01-YOUR-TOKEN-HERE"
$env:ANTHROPIC_BASE_URL = "https://relay01.gaccode.com/claudecode"

# 代理配置 (如需要)
$env:HTTP_PROXY = "http://192.168.0.106:7890"
$env:HTTPS_PROXY = "http://192.168.0.106:7890"
$env:http_proxy = $env:HTTP_PROXY
$env:https_proxy = $env:HTTPS_PROXY

Write-Host "环境变量已设置 - API Key: $($env:ANTHROPIC_API_KEY.Substring(0,15))..."