Write-Host "[*] Executing Automated Security Audit Suite"
Write-Host "[*] Target Environment: Localhost API"
Write-Host ""
Write-Host "[*] Press any key to initiate sequence..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""

Write-Host "[*] Module 1/6: Authentication Policy"
python attack1_weak_password.py
Start-Sleep -Seconds 1

Write-Host "`n[*] Module 2/6: Cryptographic Storage"
python attack2_weak_hashing.py
Start-Sleep -Seconds 1

Write-Host "`n[*] Module 3/6: Rate Limiting & Brute Force"
python attack3_brute_force.py
Start-Sleep -Seconds 1

Write-Host "`n[*] Module 4/6: Identity Enumeration"
python attack4_user_enumeration.py
Start-Sleep -Seconds 1

Write-Host "`n[*] Module 5/6: Session State Management"
python attack5_session_management.py
Start-Sleep -Seconds 1

Write-Host "`n[*] Module 6/6: Recovery Mechanisms"
python attack6_password_reset.py

Write-Host "`n[*] Audit sequence completed."