param(
    [Parameter(Mandatory = $true)]
    [string]$Target,
    [ValidateSet("v1", "v2")]
    [string]$Schema = "v1"
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Get-Command py -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python -ErrorAction SilentlyContinue
}
if (-not $python) {
    throw "需要 Python 3。也可以直接复制 ready\v1 里的文件到题目目录。"
}
& $python.Source "$here\install.py" --schema $Schema --target $Target
