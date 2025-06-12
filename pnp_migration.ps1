Import-Module PnP.PowerShell

# Config
$sourceFolder = "D:\salesforcedownload_code\salesforce_document_folder_downloads\SalesForceProjectsDownload_Melbourne Quarter (Parent Project)_2025-06-12_12-12\Melbourne Quarter (Parent Project)"
$siteUrl = "https://lendlease.sharepoint.com/sites/MelbourneQuarter(ParentProject)"

$libraryName = "Shared documents"
$spRootFolder = "$libraryName/Project Files/17. Historical Compass Document"

$timestampTag = Get-Date -Format "yyyy-MM-dd_HHmm"
$uploadLogPath = "upload_log_$timestampTag.txt"
$errorLogPath  = "error_log_$timestampTag.txt"




# Start timer
$startTime = Get-Date
$totalSize = 0

# Connect to SharePoint
Connect-PnPOnline -Url $siteUrl -Interactive -ClientId "a907eb35-5fdd-41ea-8666-dd45affa1944" 

# Get all files recursively
$Files = Get-ChildItem -Path $sourceFolder -Recurse -File

foreach ($File in $Files) {
    try {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $relativePath = $File.FullName.Substring($sourceFolder.Length).TrimStart('\')
        $relativeFolder = Split-Path $relativePath -Parent

        if ([string]::IsNullOrEmpty($relativeFolder)) {
            $spFolderPath = $spRootFolder
        } else {
            $spFolderPath = "$spRootFolder/$relativeFolder" -replace '\\','/'
        }

        Write-Host "Uploading $($File.Name) to $spFolderPath"
        Add-PnPFile -Path $File.FullName -Folder $spFolderPath



        # Track uploaded file size
        $totalSize += $File.Length

        # Log success with timestamp
        "[$timestamp] File uploaded: $($File.FullName) to $spFolderPath" | Out-File -Append -FilePath $uploadLogPath
    }
    catch {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $errorMessage = "[$timestamp] ERROR: Failed to upload $($File.FullName) - $($_.Exception.Message)"
        Write-Host $errorMessage -ForegroundColor Red
        $errorMessage | Out-File -Append -FilePath $errorLogPath
    }
}

# End timer
$endTime = Get-Date
$duration = $endTime - $startTime

# Size conversions
$sizeMB = [math]::Round($totalSize / 1MB, 2)
$sizeGB = [math]::Round($totalSize / 1GB, 2)

# Output summary
Write-Host "`nUpload completed in $($duration.TotalMinutes.ToString("0.00")) minutes ($duration)." -ForegroundColor Cyan
Write-Host "Total uploaded size: $sizeMB MB ($sizeGB GB)" -ForegroundColor Cyan

# Log summary with timestamp
$summaryTimestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
@"
======== Summary ========
[$summaryTimestamp]
Completed at: $endTime
Duration     : $duration
Total Size   : $sizeMB MB ($sizeGB GB)
"@ | Out-File -Append -FilePath $uploadLogPath

# === VERIFICATION STEP ===

# Count local files and folders
$localFiles = Get-ChildItem -Path $sourceFolder -Recurse -File
$localFolders = Get-ChildItem -Path $sourceFolder -Recurse -Directory

$localFileCount = $localFiles.Count
$localFolderCount = $localFolders.Count

# Get SharePoint files recursively
# Recursive function to collect SP files and folders
function Get-SPItemsRecursive {
    param (
        [string]$folderSiteRelativeUrl
    )

    $allFiles = @()
    $allFolders = @()

    try {
        $items = Get-PnPFolderItem -FolderSiteRelativeUrl $folderSiteRelativeUrl -ErrorAction Stop
    } catch {
        Write-Host "⚠️  Failed to access: $folderSiteRelativeUrl - $($_.Exception.Message)" -ForegroundColor Red
        return [PSCustomObject]@{
            Files   = $allFiles
            Folders = $allFolders
        }
    }

    foreach ($item in $items) {
        if ($item -is [Microsoft.SharePoint.Client.File]) {
            $allFiles += $item
        }
        elseif ($item -is [Microsoft.SharePoint.Client.Folder]) {
            $allFolders += $item
            $subFolderUrl = "$folderSiteRelativeUrl/$($item.Name)"
            $result = Get-SPItemsRecursive -folderSiteRelativeUrl $subFolderUrl
            $allFiles += $result.Files
            $allFolders += $result.Folders
        }
    }

    return [PSCustomObject]@{
        Files   = $allFiles
        Folders = $allFolders
    }
}



Write-Host "`n🔍 Verifying upload..." -ForegroundColor Yellow

# Corrected function call with correct parameter name
$spItems = Get-SPItemsRecursive -folderSiteRelativeUrl $spRootFolder
$spFileCount = $spItems.Files.Count
$spFolderCount = $spItems.Folders.Count

# Output verification summary
Write-Host "`n====== Verification Summary ======" -ForegroundColor Green
Write-Host "Local files        : $localFileCount"
Write-Host "Local folders      : $localFolderCount"
Write-Host "SharePoint files   : $spFileCount"
Write-Host "SharePoint folders : $spFolderCount"

if (($spFileCount -eq $localFileCount) -and ($spFolderCount -eq $localFolderCount)) {
    Write-Host "✅ All files and folders appear to be uploaded correctly!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Mismatch: Some files or folders might be missing in SharePoint!" -ForegroundColor Red
}
