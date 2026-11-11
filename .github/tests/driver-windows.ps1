$ErrorActionPreference = 'Stop'
# Baixar o driver correspondente ao runtime WebView2 efetivamente instalado.
$roots = @(
  "${env:ProgramFiles(x86)}\Microsoft\EdgeWebView\Application",
  "$env:ProgramFiles\Microsoft\EdgeWebView\Application",
  "$env:LOCALAPPDATA\Microsoft\EdgeWebView\Application"
)
$runtime = $roots | Where-Object { Test-Path $_ } | ForEach-Object {
  Get-ChildItem $_ -Directory | ForEach-Object {
    $exe = Join-Path $_.FullName 'msedgewebview2.exe'
    if (Test-Path $exe) { Get-Item $exe }
  }
} | Sort-Object { [version]$_.VersionInfo.FileVersion } -Descending | Select-Object -First 1
if (-not $runtime) { throw 'WebView2 Runtime não encontrado após instalar o app' }
$version = $runtime.VersionInfo.FileVersion
Write-Output "WebView2 Runtime: $version"
$pasta = Join-Path $env:RUNNER_TEMP 'df-webdriver'
New-Item -ItemType Directory -Force $pasta | Out-Null
$zip = Join-Path $pasta 'driver.zip'
Invoke-WebRequest "https://msedgedriver.microsoft.com/$version/edgedriver_win64.zip" -OutFile $zip
Expand-Archive $zip -DestinationPath $pasta -Force
$driver = Join-Path $pasta 'msedgedriver.exe'
if (-not (Test-Path $driver)) { throw 'Driver não encontrado no download' }
"DF_WEBDRIVER=$driver" >> $env:GITHUB_ENV
& $driver --version
if ($LASTEXITCODE -ne 0) { throw 'Não foi possível executar o driver' }
