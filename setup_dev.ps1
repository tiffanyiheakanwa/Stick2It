# setup_dev.ps1

# setup_dev.ps1 (Optimized for Cursor)

Write-Host "Starting RemindAI in Cursor Integrated Terminals..."

# 1. Check for Redis/Memurai
$redisCheck = Get-Service -Name "Memurai" -ErrorAction SilentlyContinue
if ($redisCheck -and $redisCheck.Status -eq "Running") {
    Write-Host "Redis/Memurai is already running."
} else {
    Write-Host "Warning: Redis/Memurai not found. Ensure Docker or Memurai is active."
}

# 2. Start Celery Worker (In-IDE Tab)
Write-Host "Opening Celery Worker tab..."
cursor --terminal --command "python -m celery -A backend.app.tasks worker --loglevel=info -P solo"

# 3. Start FastAPI Server (In-IDE Tab)
Write-Host "Opening FastAPI Backend tab..."
cursor --terminal --command "python -m uvicorn backend.app.main:app --reload"

# 4. Start React Frontend (In-IDE Tab)
if (Test-Path "RemindAI-frontend") {
    Write-Host "Opening React Frontend tab..."
    cursor --terminal --command "cd RemindAI-frontend; npm run dev"
}

Write-Host "Check the terminal dropdown in Cursor for your new tabs!"

# Write-Host "Starting RemindAI in VS Code Integrated Terminals..."

# # 1. Check for Redis/Memurai
# $redisCheck = Get-Service -Name "Memurai" -ErrorAction SilentlyContinue
# if ($redisCheck -and $redisCheck.Status -eq "Running") {
#     Write-Host "Redis/Memurai is already running."
# } else {
#     Write-Host "Warning: Redis/Memurai not found. Ensure Docker or Memurai is active."
# }

# # 2. Start Celery Worker
# Write-Host "Dispatching Celery Worker..."
# code --terminal --command "python -m celery -A backend.app.tasks worker --loglevel=info -P solo"

# # 3. Start FastAPI Server
# Write-Host "Dispatching FastAPI Backend..."
# code --terminal --command "python -m uvicorn backend.app.main:app --reload"

# # 4. Start React Frontend
# if (Test-Path "RemindAI-frontend") {
#     Write-Host "Dispatching React Frontend..."
#     code --terminal --command "cd RemindAI-frontend; npm run dev"
# }

# Write-Host "Success! Check your Terminal panel for the new tabs."


