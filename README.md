# postActionScanURL
- Script to be triggered as a post action by checkmarx SAST to send an email with SAST scan Results URL
    batch script expects to receive 2 arguments from SAST:
    - XML report file PATH
    - optional: Email recipient
    -     supports the following convention lists for example:
    -         "ido.neamani@checkmarx.com,ido.neamani@gmail.com,tazazoo@gmail.com"
    -         "ido.neamani@checkmarx.com"
    
    In case email recipient are not provided, all team members related to project will receive emails
  
  - The batch script will call additional python script for URL extraction and sending via email
    script has variables for further customization if needed
    script output all execution info and errors to errors_log file

Python Installation: Ensure that Python is installed on the Windows server. You can direct your customer to the official Python website (https://www.python.org/) to download and install the latest version of Python. During installation, they should ensure they select the option to add Python to the system PATH to make it easier to run Python scripts from the command line.

In order to create a post scan action in sast APP  and send an email please follow these steps:
Place the enclosed files in the Executable folder under Checkmarx home  - C:\Program Files\Checkmarx\Executables"
Edit config.yaml for property configuratiorn.
Create a post scan action global CONFIGURATION and in the project level as described here : https://checkmarx.com/resource/documents/en/34965-46408-configuring-an-executable-action.html#UUID-903907f7-4b20-ccb0-fc5a-fa2e6b8c5362
