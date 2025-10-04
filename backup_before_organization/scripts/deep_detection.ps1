# Deep Technology Detection Script for PowerShell
# Provides multiple command combinations for comprehensive technology detection

param(
    [Parameter(Mandatory=$true)]
    [string]$Command,
    
    [Parameter(Mandatory=$true)]
    [string]$Input,
    
    [string]$OutputFile
)

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to run deep detection
function Invoke-DeepDetection {
    param(
        [string]$Url,
        [string]$OutputFile,
        [int]$UserAgents = 15,
        [int]$MinConfidence = 5,
        [int]$MaxResults = 300
    )
    
    Write-Status "Starting deep detection for: $Url"
    Write-Status "Output file: $OutputFile"
    Write-Status "User agents: $UserAgents"
    Write-Status "Min confidence: $MinConfidence"
    Write-Status "Max results: $MaxResults"
    
    $arguments = @(
        $Url,
        "--use-dataset", "--use-whatweb", "--use-wappalyzer",
        "--user-agents", $UserAgents,
        "--preferred-browser", "random",
        "--preferred-os", "windows",
        "--min-confidence", $MinConfidence,
        "--max-results", $MaxResults,
        "--timeout", "60",
        "--follow-redirects",
        "--output", "csv",
        "--save-report", $OutputFile,
        "--verbose", "--debug", "--dump",
        "--whatweb-aggression", "4",
        "--workers", "1",
        "--delay", "1.0"
    )
    
    try {
        & python main.py @arguments
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Deep detection completed successfully"
            Write-Status "Results saved to: $OutputFile"
        } else {
            Write-Error "Deep detection failed"
            exit 1
        }
    } catch {
        Write-Error "Deep detection failed: $_"
        exit 1
    }
}

# Function to run batch detection
function Invoke-BatchDetection {
    param(
        [string]$UrlsFile,
        [string]$OutputFile,
        [int]$Workers = 5
    )
    
    Write-Status "Starting batch detection for: $UrlsFile"
    Write-Status "Output file: $OutputFile"
    Write-Status "Workers: $Workers"
    
    $arguments = @(
        "--batch", $UrlsFile,
        "--use-dataset", "--use-whatweb", "--use-wappalyzer",
        "--user-agents", "8",
        "--preferred-browser", "random",
        "--min-confidence", "10",
        "--max-results", "150",
        "--timeout", "45",
        "--follow-redirects",
        "--output", "csv",
        "--save-report", $OutputFile,
        "--verbose", "--debug",
        "--whatweb-aggression", "4",
        "--workers", $Workers,
        "--delay", "1.0"
    )
    
    try {
        & python main.py @arguments
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Batch detection completed successfully"
            Write-Status "Results saved to: $OutputFile"
        } else {
            Write-Error "Batch detection failed"
            exit 1
        }
    } catch {
        Write-Error "Batch detection failed: $_"
        exit 1
    }
}

# Function to run aggressive detection
function Invoke-AggressiveDetection {
    param(
        [string]$Url,
        [string]$OutputFile
    )
    
    Write-Status "Starting aggressive detection for: $Url"
    Write-Status "Output file: $OutputFile"
    
    $arguments = @(
        $Url,
        "--use-dataset", "--use-whatweb", "--use-wappalyzer",
        "--user-agents", "20",
        "--preferred-browser", "random",
        "--preferred-os", "windows",
        "--min-confidence", "1",
        "--max-results", "500",
        "--timeout", "90",
        "--follow-redirects",
        "--output", "csv",
        "--save-report", $OutputFile,
        "--verbose", "--debug", "--dump",
        "--whatweb-aggression", "4",
        "--whatweb-path", "./WhatWeb/whatweb",
        "--workers", "1",
        "--delay", "0.2"
    )
    
    try {
        & python main.py @arguments
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Aggressive detection completed successfully"
            Write-Status "Results saved to: $OutputFile"
        } else {
            Write-Error "Aggressive detection failed"
            exit 1
        }
    } catch {
        Write-Error "Aggressive detection failed: $_"
        exit 1
    }
}

# Function to run stealth detection
function Invoke-StealthDetection {
    param(
        [string]$Url,
        [string]$OutputFile
    )
    
    Write-Status "Starting stealth detection for: $Url"
    Write-Status "Output file: $OutputFile"
    
    $arguments = @(
        $Url,
        "--use-dataset", "--use-whatweb", "--use-wappalyzer",
        "--user-agents", "25",
        "--preferred-browser", "random",
        "--preferred-os", "windows",
        "--min-confidence", "10",
        "--max-results", "150",
        "--timeout", "30",
        "--follow-redirects",
        "--output", "csv",
        "--save-report", $OutputFile,
        "--verbose", "--debug",
        "--whatweb-aggression", "3",
        "--workers", "1",
        "--delay", "2.0"
    )
    
    try {
        & python main.py @arguments
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Stealth detection completed successfully"
            Write-Status "Results saved to: $OutputFile"
        } else {
            Write-Error "Stealth detection failed"
            exit 1
        }
    } catch {
        Write-Error "Stealth detection failed: $_"
        exit 1
    }
}

# Function to run high-confidence detection
function Invoke-HighConfidenceDetection {
    param(
        [string]$Url,
        [string]$OutputFile
    )
    
    Write-Status "Starting high-confidence detection for: $Url"
    Write-Status "Output file: $OutputFile"
    
    $arguments = @(
        $Url,
        "--use-dataset", "--use-whatweb", "--use-wappalyzer",
        "--user-agents", "5",
        "--preferred-browser", "chrome",
        "--min-confidence", "50",
        "--max-results", "50",
        "--timeout", "30",
        "--follow-redirects",
        "--output", "csv",
        "--save-report", $OutputFile,
        "--verbose",
        "--whatweb-aggression", "3",
        "--workers", "1",
        "--delay", "0.5"
    )
    
    try {
        & python main.py @arguments
        if ($LASTEXITCODE -eq 0) {
            Write-Success "High-confidence detection completed successfully"
            Write-Status "Results saved to: $OutputFile"
        } else {
            Write-Error "High-confidence detection failed"
            exit 1
        }
    } catch {
        Write-Error "High-confidence detection failed: $_"
        exit 1
    }
}

# Generate timestamp for output files
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Set default output file if not provided
if (-not $OutputFile) {
    $OutputFile = "${Command}_detection_${timestamp}.csv"
}

# Main execution
switch ($Command.ToLower()) {
    "deep" {
        if (-not $Input) {
            Write-Error "URL required for deep detection"
            Write-Host "Usage: .\deep_detection.ps1 -Command deep -Input <URL> [-OutputFile <file>]"
            exit 1
        }
        Invoke-DeepDetection -Url $Input -OutputFile $OutputFile
    }
    "batch" {
        if (-not $Input) {
            Write-Error "URLs file required for batch detection"
            Write-Host "Usage: .\deep_detection.ps1 -Command batch -Input <urls_file> [-OutputFile <file>]"
            exit 1
        }
        Invoke-BatchDetection -UrlsFile $Input -OutputFile $OutputFile
    }
    "aggressive" {
        if (-not $Input) {
            Write-Error "URL required for aggressive detection"
            Write-Host "Usage: .\deep_detection.ps1 -Command aggressive -Input <URL> [-OutputFile <file>]"
            exit 1
        }
        Invoke-AggressiveDetection -Url $Input -OutputFile $OutputFile
    }
    "stealth" {
        if (-not $Input) {
            Write-Error "URL required for stealth detection"
            Write-Host "Usage: .\deep_detection.ps1 -Command stealth -Input <URL> [-OutputFile <file>]"
            exit 1
        }
        Invoke-StealthDetection -Url $Input -OutputFile $OutputFile
    }
    "high-confidence" {
        if (-not $Input) {
            Write-Error "URL required for high-confidence detection"
            Write-Host "Usage: .\deep_detection.ps1 -Command high-confidence -Input <URL> [-OutputFile <file>]"
            exit 1
        }
        Invoke-HighConfidenceDetection -Url $Input -OutputFile $OutputFile
    }
    default {
        Write-Host "Deep Technology Detection Script for PowerShell"
        Write-Host ""
        Write-Host "Usage: .\deep_detection.ps1 -Command <command> -Input <input> [-OutputFile <file>]"
        Write-Host ""
        Write-Host "Commands:"
        Write-Host "  deep <URL>              - Deep detection with maximum fallbacks"
        Write-Host "  batch <urls_file>       - Batch processing with multiple URLs"
        Write-Host "  aggressive <URL>        - Aggressive detection with maximum settings"
        Write-Host "  stealth <URL>           - Stealth detection with high user agent count"
        Write-Host "  high-confidence <URL>   - High-confidence detection (50%+ threshold)"
        Write-Host ""
        Write-Host "Examples:"
        Write-Host "  .\deep_detection.ps1 -Command deep -Input https://example.com"
        Write-Host "  .\deep_detection.ps1 -Command batch -Input urls.txt"
        Write-Host "  .\deep_detection.ps1 -Command aggressive -Input https://example.com -OutputFile aggressive_results.csv"
        Write-Host "  .\deep_detection.ps1 -Command stealth -Input https://example.com -OutputFile stealth_results.csv"
        Write-Host "  .\deep_detection.ps1 -Command high-confidence -Input https://example.com -OutputFile high_conf_results.csv"
        exit 1
    }
}
