# run_docking_tests.ps1
Write-Host "Building Docker image for testing..."
docker-compose -f docker-compose.test.yml build bio-analyze-test

if ($?) {
    Write-Host "Running docking tests..."
    .\run_tests_docker.ps1 packages\docking\tests
} else {
    Write-Error "Docker build failed."
}
