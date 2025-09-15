
$maxRetries = 10
$retryDelay = 5 
$retryCount = 0


while ($retryCount -lt $maxRetries) {
    Write-Host "Trying git push, attempt $($retryCount + 1)..."
    git push
    if ($LASTEXITCODE -eq 0) {
        Write-Host "git push succeeded!"
        break
    } else {
        Write-Host "git push failed, retrying in $retryDelay seconds..."
        Start-Sleep -Seconds $retryDelay
        $retryCount++
    }
}

if ($retryCount -eq $maxRetries) {
    Write-Host "Max retries reached, git push did not succeed."
}
