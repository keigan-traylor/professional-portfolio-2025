Import-Module -Force ./AdvancedAutomation.psm1 -Verbose
$credPath = '.\secrets.cred'
if (-Not (Test-Path $credPath)) {
    Write-Host 'Creating test credential (will be saved protected locally)'
    $username = Read-Host 'Enter username for lab (testuser)'
    $pwd = Read-Host 'Enter password (will be saved securely)' -AsSecureString
    $creds = New-SecureCredential -UserName $username -Password $pwd
    Save-EncryptedCredential -Path $credPath -Credential $creds -Verbose
}
$creds = Get-EncryptedCredential -Path $credPath
Write-Host 'Loaded credential for user:' $creds.UserName
$report = [PSCustomObject]@{ Generated = (Get-Date).ToString('o'); Host = $env:COMPUTERNAME; User = $creds.UserName }
$report | ConvertTo-Json | Out-File -FilePath '.\report.json' -Encoding utf8
Write-Host 'Report written to report.json'
