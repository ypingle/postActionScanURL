@echo off

REM Please modify the CD command to your relevant SAST installation location
cd /d "C:\Program Files\Checkmarx\Executables"

REM Initialize the log file with a timestamp
set LogFile="errors_log.txt"
echo %date% %time% - Batch Script Execution started >> %LogFile%

REM Retrieving the location of the created SAST scan XML report. Note that in general XML report files are saved in C:\Program Files\Checkmarx\Checkmarx Jobs Manager\Results
set "XMLReportFileName=%~1"
REM Retrieving the email recipients argument
set "EmailRecipients=%~2"

echo %date% %time% - Email Recipients: %EmailRecipients% >> %LogFile%

REM Error handling for retrieving the XML report location and the email recipients argument
IF "%XMLReportFileName%"=="" (
    echo %date% %time% - Error: No XML file provided. >> %LogFile%
    exit /b
) ELSE IF NOT EXIST "%XMLReportFileName%" (
    echo %date% %time% - Error: XML file "%XMLReportFileName%" not found. >> %LogFile%
    exit /b
) ELSE IF "%EmailRecipients%"=="" (
    py "%~dp0extract_attribute_value.py" "%XMLReportFileName%" >> %LogFile%
) ELSE (
    REM Call the Python script passing XML report location and Email Recipients as arguments
    py "%~dp0extract_attribute_value.py" "%XMLReportFileName%" "%EmailRecipients%" >> %LogFile%
    
    REM Check if an error occurred during Python script execution
    if errorlevel 1 (
        echo %date% %time% - Error occurred during execution of Python Script >> %LogFile%
    ) else (
        echo %date% %time% - Execution of Python script completed successfully. >> %LogFile%
    )
)
