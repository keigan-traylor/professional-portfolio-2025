function New-SecureCredential {
    param([string]$UserName, [securestring]$Password)
    return New-Object System.Management.Automation.PSCredential ($UserName, $Password)
}

function Save-EncryptedCredential {
    param([string]$Path, [PSCredential]$Credential)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes(($Credential.UserName + '|' + ($Credential.GetNetworkCredential().Password)))
    $protected = [System.Security.Cryptography.ProtectedData]::Protect($bytes, $null, [System.Security.Cryptography.DataProtectionScope]::CurrentUser)
    [IO.File]::WriteAllBytes($Path, $protected)
}

function Get-EncryptedCredential {
    param([string]$Path)
    $bytes = [IO.File]::ReadAllBytes($Path)
    $unprotected = [System.Security.Cryptography.ProtectedData]::Unprotect($bytes, $null, [System.Security.Cryptography.DataProtectionScope]::CurrentUser)
    $str = [System.Text.Encoding]::UTF8.GetString($unprotected)
    $parts = $str -split '\|',2
    $user = $parts[0]; $pwd = $parts[1]
    $sec = ConvertTo-SecureString $pwd -AsPlainText -Force
    return New-Object System.Management.Automation.PSCredential ($user, $sec)
}

Export-ModuleMember -Function * -Alias *
