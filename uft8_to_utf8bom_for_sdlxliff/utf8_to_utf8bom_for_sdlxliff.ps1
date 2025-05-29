# Run this in the folder containing .sdlxliff files
Get-ChildItem -Filter *.sdlxliff | ForEach-Object {
    $filePath = $_.FullName
    
    # Read first 3 bytes to check for existing BOM
    $header = [System.IO.File]::ReadAllBytes($filePath) | Select-Object -First 3
    $hasBOM = ($header[0] -eq 0xEF -and $header[1] -eq 0xBB -and $header[2] -eq 0xBF)
    
    if (-not $hasBOM) {
        # Read the ENTIRE file as bytes
        $content = [System.IO.File]::ReadAllBytes($filePath)
        
        # Prepend BOM (EF BB BF)
        $newContent = [byte[]](0xEF, 0xBB, 0xBF) + $content
        
        # Write back (binary mode, no encoding changes)
        [System.IO.File]::WriteAllBytes($filePath, $newContent)
        Write-Host "Added BOM to: $($_.Name)"
    }
    else {
        Write-Host "Already has BOM: $($_.Name)"
    }
}
Write-Host "Done!"
pause
