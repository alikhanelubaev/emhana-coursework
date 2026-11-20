param([string]$ToolsRoot = '../android-tools', [string]$ApkOutput = '../../outputs/Emhana-Android.apk')
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$toolsPath = [IO.Path]::GetFullPath((Join-Path $projectRoot $ToolsRoot))
$outputPath = [IO.Path]::GetFullPath((Join-Path $projectRoot $ApkOutput))
$jdkPath = (Get-ChildItem -LiteralPath (Join-Path $toolsPath 'jdk') -Directory | Select-Object -First 1).FullName
$btPath = (Get-ChildItem -LiteralPath (Join-Path $toolsPath 'build-tools') -Directory | Select-Object -First 1).FullName
$platformPath = (Get-ChildItem -LiteralPath (Join-Path $toolsPath 'platform') -Directory | Select-Object -First 1).FullName
$env:JAVA_HOME = $jdkPath
$env:PATH = (Join-Path $jdkPath 'bin') + ';' + $env:PATH
$androidJar = Join-Path $platformPath 'android.jar'
$buildPath = Join-Path $projectRoot 'build'
New-Item -ItemType Directory -Path $buildPath,(Join-Path $buildPath 'classes'),(Join-Path $buildPath 'generated'),(Join-Path $buildPath 'dex') -Force | Out-Null

function Run-Checked([string]$Exe, [string[]]$Arguments) {
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Build step failed: $Exe ($LASTEXITCODE)" }
}
Run-Checked (Join-Path $btPath 'aapt2.exe') @('compile','--dir',(Join-Path $projectRoot 'res'),'-o',(Join-Path $buildPath 'resources.zip'))
Run-Checked (Join-Path $btPath 'aapt2.exe') @('link','-o',(Join-Path $buildPath 'unsigned.apk'),'--manifest',(Join-Path $projectRoot 'AndroidManifest.xml'),'-I',$androidJar,'--java',(Join-Path $buildPath 'generated'),'-A',(Join-Path $projectRoot 'assets'),(Join-Path $buildPath 'resources.zip'))
$javaFiles = @(Get-ChildItem -LiteralPath (Join-Path $projectRoot 'src'),(Join-Path $buildPath 'generated') -Filter '*.java' -Recurse | ForEach-Object { $_.FullName })
Run-Checked (Join-Path $jdkPath 'bin/javac.exe') (@('-encoding','UTF-8','-source','8','-target','8','-classpath',$androidJar,'-d',(Join-Path $buildPath 'classes')) + $javaFiles)
Run-Checked (Join-Path $jdkPath 'bin/jar.exe') @('--create','--file',(Join-Path $buildPath 'classes.jar'),'-C',(Join-Path $buildPath 'classes'),'.')
Run-Checked (Join-Path $jdkPath 'bin/java.exe') @('-cp',(Join-Path $btPath 'lib/d8.jar'),'com.android.tools.r8.D8','--release','--min-api','26','--lib',$androidJar,'--output',(Join-Path $buildPath 'dex'),(Join-Path $buildPath 'classes.jar'))
Run-Checked (Join-Path $jdkPath 'bin/jar.exe') @('--update','--file',(Join-Path $buildPath 'unsigned.apk'),'-C',(Join-Path $buildPath 'dex'),'classes.dex')
Run-Checked (Join-Path $btPath 'zipalign.exe') @('-f','-p','4',(Join-Path $buildPath 'unsigned.apk'),(Join-Path $buildPath 'aligned.apk'))
$keyPath = Join-Path $projectRoot 'emhana-demo.jks'
# This is a reusable local demo signing identity, not a store publishing credential.
if (!(Test-Path -LiteralPath $keyPath)) {
    Run-Checked (Join-Path $jdkPath 'bin/keytool.exe') @('-genkeypair','-keystore',$keyPath,'-storepass','android','-keypass','android','-alias','emhana','-keyalg','RSA','-keysize','2048','-validity','10000','-dname','CN=Emhana Course Project, OU=Demo, O=Emhana, C=KZ','-noprompt')
}
Run-Checked (Join-Path $jdkPath 'bin/java.exe') @('-jar',(Join-Path $btPath 'lib/apksigner.jar'),'sign','--ks',$keyPath,'--ks-key-alias','emhana','--ks-pass','pass:android','--key-pass','pass:android','--v4-signing-enabled','false','--out',$outputPath,(Join-Path $buildPath 'aligned.apk'))
Run-Checked (Join-Path $jdkPath 'bin/java.exe') @('-jar',(Join-Path $btPath 'lib/apksigner.jar'),'verify','--verbose','--print-certs',$outputPath)
Run-Checked (Join-Path $btPath 'aapt2.exe') @('dump','badging',$outputPath)
Write-Output "APK: $outputPath"
