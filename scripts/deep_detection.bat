@echo off
setlocal enabledelayedexpansion

REM Deep Technology Detection Script for Windows
REM Provides multiple command combinations for comprehensive technology detection

if "%1"=="" goto :usage
if "%1"=="help" goto :usage
if "%1"=="-h" goto :usage
if "%1"=="--help" goto :usage

set command=%1
set input=%2
set output_file=%3

REM Generate timestamp for output files
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,8%_%dt:~8,6%"

if "%command%"=="deep" goto :deep_detection
if "%command%"=="batch" goto :batch_detection
if "%command%"=="aggressive" goto :aggressive_detection
if "%command%"=="stealth" goto :stealth_detection
if "%command%"=="high-confidence" goto :high_confidence_detection
goto :usage

:deep_detection
if "%input%"=="" (
    echo [ERROR] URL required for deep detection
    echo Usage: %0 deep ^<URL^> [output_file]
    exit /b 1
)
if "%output_file%"=="" set output_file=deep_detection_%timestamp%.csv
echo [INFO] Starting deep detection for: %input%
echo [INFO] Output file: %output_file%
python main.py "%input%" --use-dataset --use-whatweb --use-wappalyzer --user-agents 15 --preferred-browser random --preferred-os windows --min-confidence 5 --max-results 300 --timeout 60 --follow-redirects --output csv --save-report "%output_file%" --verbose --debug --dump --whatweb-aggression 4 --workers 1 --delay 1.0
if %errorlevel% equ 0 (
    echo [SUCCESS] Deep detection completed successfully
    echo [INFO] Results saved to: %output_file%
) else (
    echo [ERROR] Deep detection failed
    exit /b 1
)
goto :end

:batch_detection
if "%input%"=="" (
    echo [ERROR] URLs file required for batch detection
    echo Usage: %0 batch ^<urls_file^> [output_file]
    exit /b 1
)
if "%output_file%"=="" set output_file=batch_detection_%timestamp%.csv
echo [INFO] Starting batch detection for: %input%
echo [INFO] Output file: %output_file%
python main.py --batch "%input%" --use-dataset --use-whatweb --use-wappalyzer --user-agents 8 --preferred-browser random --min-confidence 10 --max-results 150 --timeout 45 --follow-redirects --output csv --save-report "%output_file%" --verbose --debug --whatweb-aggression 4 --workers 5 --delay 1.0
if %errorlevel% equ 0 (
    echo [SUCCESS] Batch detection completed successfully
    echo [INFO] Results saved to: %output_file%
) else (
    echo [ERROR] Batch detection failed
    exit /b 1
)
goto :end

:aggressive_detection
if "%input%"=="" (
    echo [ERROR] URL required for aggressive detection
    echo Usage: %0 aggressive ^<URL^> [output_file]
    exit /b 1
)
if "%output_file%"=="" set output_file=aggressive_detection_%timestamp%.csv
echo [INFO] Starting aggressive detection for: %input%
echo [INFO] Output file: %output_file%
python main.py "%input%" --use-dataset --use-whatweb --use-wappalyzer --user-agents 20 --preferred-browser random --preferred-os windows --min-confidence 1 --max-results 500 --timeout 90 --follow-redirects --output csv --save-report "%output_file%" --verbose --debug --dump --whatweb-aggression 4 --whatweb-path ./WhatWeb/whatweb --workers 1 --delay 0.2
if %errorlevel% equ 0 (
    echo [SUCCESS] Aggressive detection completed successfully
    echo [INFO] Results saved to: %output_file%
) else (
    echo [ERROR] Aggressive detection failed
    exit /b 1
)
goto :end

:stealth_detection
if "%input%"=="" (
    echo [ERROR] URL required for stealth detection
    echo Usage: %0 stealth ^<URL^> [output_file]
    exit /b 1
)
if "%output_file%"=="" set output_file=stealth_detection_%timestamp%.csv
echo [INFO] Starting stealth detection for: %input%
echo [INFO] Output file: %output_file%
python main.py "%input%" --use-dataset --use-whatweb --use-wappalyzer --user-agents 25 --preferred-browser random --preferred-os windows --min-confidence 10 --max-results 150 --timeout 30 --follow-redirects --output csv --save-report "%output_file%" --verbose --debug --whatweb-aggression 3 --workers 1 --delay 2.0
if %errorlevel% equ 0 (
    echo [SUCCESS] Stealth detection completed successfully
    echo [INFO] Results saved to: %output_file%
) else (
    echo [ERROR] Stealth detection failed
    exit /b 1
)
goto :end

:high_confidence_detection
if "%input%"=="" (
    echo [ERROR] URL required for high-confidence detection
    echo Usage: %0 high-confidence ^<URL^> [output_file]
    exit /b 1
)
if "%output_file%"=="" set output_file=high_confidence_detection_%timestamp%.csv
echo [INFO] Starting high-confidence detection for: %input%
echo [INFO] Output file: %output_file%
python main.py "%input%" --use-dataset --use-whatweb --use-wappalyzer --user-agents 5 --preferred-browser chrome --min-confidence 50 --max-results 50 --timeout 30 --follow-redirects --output csv --save-report "%output_file%" --verbose --whatweb-aggression 3 --workers 1 --delay 0.5
if %errorlevel% equ 0 (
    echo [SUCCESS] High-confidence detection completed successfully
    echo [INFO] Results saved to: %output_file%
) else (
    echo [ERROR] High-confidence detection failed
    exit /b 1
)
goto :end

:usage
echo Deep Technology Detection Script for Windows
echo.
echo Usage: %0 ^<command^> ^<input^> [output_file]
echo.
echo Commands:
echo   deep ^<URL^>              - Deep detection with maximum fallbacks
echo   batch ^<urls_file^>       - Batch processing with multiple URLs
echo   aggressive ^<URL^>        - Aggressive detection with maximum settings
echo   stealth ^<URL^>           - Stealth detection with high user agent count
echo   high-confidence ^<URL^>   - High-confidence detection (50%%+ threshold)
echo.
echo Examples:
echo   %0 deep https://example.com
echo   %0 batch urls.txt
echo   %0 aggressive https://example.com aggressive_results.csv
echo   %0 stealth https://example.com stealth_results.csv
echo   %0 high-confidence https://example.com high_conf_results.csv
exit /b 1

:end
