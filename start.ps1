$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    throw '请先按 README.md 安装依赖。'
}
& .venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8050 --browser.gatherUsageStats false
