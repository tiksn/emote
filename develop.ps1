$ErrorActionPreference = 'Stop'

virtualenv .env

if ($IsWindows) {
    .\.env\Scripts\activate.ps1
}
elseif ($IsLinux) {
    .\.env\bin\activate.ps1
}

python -m pip install --upgrade pip
pip install -r requirements.txt
