# Helper to run manage.py from any subdirectory
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File "<path>\runproject.ps1"

$path = (Get-Location).Path
while (-not (Test-Path (Join-Path $path 'manage.py'))) {
    $parent = Split-Path $path -Parent
    if ($parent -eq $path) {
        Write-Error "manage.py not found in any parent directories."
        exit 1
    }
    $path = $parent
}

Write-Host "Found manage.py in: $path"
Set-Location $path

# Run the Django development server
python manage.py runserver
