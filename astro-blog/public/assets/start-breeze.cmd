@echo off
setlocal
cd /d "%~dp0"
title Breeze local voice - close this window to stop
set "PATH=%~dp0;%SystemRoot%\System32;%SystemRoot%\System32\WindowsPowerShell\v1.0;%SystemRoot%"
set "PSModulePath=%SystemRoot%\System32\WindowsPowerShell\v1.0\Modules"
set "PYTHONHOME="
set "PYTHONPATH="
set "CONDA_PREFIX="
set "VIRTUAL_ENV="
set "HTTP_PROXY="
set "HTTPS_PROXY="
set "ALL_PROXY="
if not exist "breeze-server.exe" (
  echo Put this launcher beside breeze-server.exe.
  pause
  exit /b 1
)
if not exist "breeze-tts-2-q8_0.gguf" (
  echo Download breeze-tts-2-q8_0.gguf into this folder first.
  pause
  exit /b 1
)
if not exist "%SystemRoot%\System32\vulkan-1.dll" (
  echo Vulkan runtime is missing. Install or update your official graphics driver first.
  echo Python and CUDA Toolkit are not required.
  pause
  exit /b 1
)
echo Checking the model download. This may take a few seconds.
powershell.exe -NoProfile -Command "$f=[IO.FileInfo]::new('breeze-tts-2-q8_0.gguf');if($f.Length -ne 3568844480){[Console]::WriteLine('Model download is incomplete or is the wrong file.');exit 1};$s=[IO.File]::OpenRead($f.FullName);$sha=[Security.Cryptography.SHA256]::Create();try{$h=[BitConverter]::ToString($sha.ComputeHash($s)).Replace('-','')}finally{$s.Dispose();$sha.Dispose()};if($h -ne 'a02bcc4b69b0601032727f8040c4942149b1b73aa0f69022fe5aaa6a8f0ef879'){[Console]::WriteLine('Model checksum failed. Download the Q8_0 file linked in the guide again.');exit 1}"
if errorlevel 1 (
  pause
  exit /b 1
)
powershell.exe -NoProfile -Command "foreach($p in 8088,8089){$l=[Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,$p);try{$l.Start()}catch{Write-Host ('Port '+$p+' is in use. Close the other Breeze window or follow the manual-port instructions in the guide.');exit 1}finally{$l.Stop()}}"
if errorlevel 1 (
  pause
  exit /b 1
)
echo Loading Breeze TTS 2. Keep this window open.
echo The browser will open when the service is ready.
start "" /min powershell.exe -NoProfile -WindowStyle Hidden -Command "$u='http://127.0.0.1:8088/'; for($i=0;$i -lt 180;$i++){try{$r=Invoke-WebRequest -UseBasicParsing -Uri $u -TimeoutSec 2;if($r.StatusCode -eq 200 -and $r.Content -match 'Breeze'){Start-Process $u;exit}}catch{};Start-Sleep -Seconds 1}"
breeze-server.exe breeze-tts-2-q8_0.gguf --host 127.0.0.1 --port 8088 --webui
pause
