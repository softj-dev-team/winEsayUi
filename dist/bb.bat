@echo off
PowerShell -Command "& {$file_id = '122Ya89tAWddpWNi4XnitrIVjhBZ3cUGv'; $file_name = 'aa.zip'; Invoke-WebRequest -Uri ('https://drive.google.com/uc?export=download&id=' + $file_id) -SessionVariable session; $code = $session.Cookies.GetCookies('https://drive.google.com') | Where-Object { $_.Name -eq 'download_warning' } | Select-Object -ExpandProperty Value; $download_link = 'https://drive.google.com/uc?export=download&confirm=' + $code + '&id=' + $file_id; Invoke-WebRequest -Uri $download_link -OutFile $file_name -WebSession $session}"

:: 파일 압축 해제
PowerShell -Command "& {Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory('$file_name', '.', $true)}"
