import xml.etree.ElementTree as ET
import requests
import sys
import smtplib
from email.mime.text import MIMEText
import yaml

# Open the YAML file
with open('config.yaml', 'r') as file:
    # Load the YAML contents
    config = yaml.safe_load(file)

SMTP_server = config['SMTP_server']
SMTP_port = config['SMTP_port']
SMTP_tls = config['SMTP_tls']
SMTP_user = config['SMTP_user']
SMTP_password = config['SMTP_password']
Email_from = config['Email_from']
Email_subject = config['Email_subject']
Email_body = config['Email_body']
SAST_url = config['SAST_url']
SAST_username = config['SAST_username']
SAST_password = config['SAST_password']

# Function to extract attribute from XML

def extract_attribute_from_xml(xml_string, attribute_name):
    try:
        root = ET.fromstring(xml_string)
        attribute_value = root.get(attribute_name)
        return attribute_value
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

# Function to send email
def send_email(sender, email_recipients, subject, body):
    recipients_list = email_recipients.split(',')  # Split the email_recipients string into individual email addresses
    recipients = [recipient.strip() for recipient in recipients_list]  # Remove leading/trailing spaces

    message = MIMEText(body)
    message['From'] = sender
    message['To'] = ", ".join(recipients)  # Join recipients list into a comma-separated string
    message['Subject'] = Email_subject

    try:
        smtp_obj = smtplib.SMTP(SMTP_server, SMTP_port)  
        if(SMTP_tls):
            smtp_obj.starttls()

        if(SMTP_user and SMTP_password):
            smtp_obj.login(SMTP_user, SMTP_password)  
        smtp_obj.sendmail(sender, recipients, message.as_string())  # Send email to all recipients
         
        smtp_obj.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def SAST_get_access_token():
    try:
        payload = 'scope=access_control_api&client_id=resource_owner_client&grant_type=password&client_secret=014DF517-39D1-4453-B7B3-9930C563627C&username=' + SAST_username + '&password=' + SAST_password
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", SAST_url + '/CxRestAPI/auth/identity/connect/token', headers=headers, data=payload)

#        print('get_SAST_access_token - token = ' + response.text)
        response_json = response.json()
        access_token = response_json['access_token']
    except Exception as e:
        print("Exception: get access token failed:", str(e))
        return ""
    else:
        return access_token

def SAST_get_teams(access_token):
    try:
        payload = {}
        headers = {
        'Authorization': 'Bearer ' + access_token
        }

        url = SAST_url + "/CxRestAPI/auth/teams"

        response = requests.request("GET", url, headers=headers, data=payload)
        response_json = response.json()
    except Exception as e:
        print("Exception: SAST_get_projects:", str(e))
        return ""
    else:
        return response_json

def SAST_get_team_members(access_token, teamId):
    try:
        payload = {}
        headers = {
        'Authorization': 'Bearer ' + access_token
        }

        url = SAST_url + "/CxRestAPI/auth/teams/" + str(teamId) + "/Users"

        response = requests.request("GET", url, headers=headers, data=payload)
        response_json = response.json()
    except Exception as e:
        print("Exception: SAST_get_team_members:", str(e))
        return ""
    else:
        return response_json

def get_email_recepients_from_team(xmlteamFullPath):
    try:
        access_token = SAST_get_access_token()
        if(access_token != ""):
            teams_list = SAST_get_teams(access_token)

        TeamID = 0
        print('team list:')

        for team in teams_list:
            print('id: ' + str(team['id']) + ' name: ' + team['fullName'])
            tmpSASTTeam = team['fullName']

            if tmpSASTTeam.startswith('/'):
                SASTTeam = tmpSASTTeam.lstrip('/')
            else:
                SASTTeam = tmpSASTTeam

            xmlteamFullPath = xmlteamFullPath.replace('\\', '/')

            if(SASTTeam == xmlteamFullPath):
                TeamID = team['id']
                print('team match found: ' + SASTTeam)
                break
        if(TeamID > 0):
            teamMembers = SAST_get_team_members(access_token, TeamID)        

            email_recipients = ''
            for member in teamMembers:
                if email_recipients == '':
                    email_recipients = member['email']
                else:
                    email_recipients += ',' + member['email']
    except Exception as e:
        print("Exception: get_email_recepients_from_team:", str(e))
        return ""
    else:
        return email_recipients


def main(): 

    try:
        if len(sys.argv) < 2:
            print("Usage: python script_name.py <path_to_xml_file> <optional:email receipeint>")
            return
        
        xml_file_path = sys.argv[1]

        with open(xml_file_path, 'r', encoding='utf-8') as file:
            xml_content = file.read()

        if len(sys.argv) == 3:
            email_recipients = sys.argv[2]
        else:
            Team_attribute = "TeamFullPathOnReportDate"
            team = extract_attribute_from_xml(xml_content, Team_attribute)
            print('team in scan xml: ' + team)
            email_recipients = get_email_recepients_from_team(team)    
        
        print('email_receipients: ' + email_recipients)

        # Specify the attribute you want to extract (e.g., "DeepLink")
        deeplink_attribute = "DeepLink"
        # Extract the value of the specified attribute from the XML content
        deepLink = extract_attribute_from_xml(xml_content, deeplink_attribute)

        # Set email variables
        email_from = Email_from
        email_subject = Email_subject
        email_body = Email_body + "\n" + deepLink
        # Send email
        send_email(email_from, email_recipients, email_subject, email_body)
    except Exception as e:
        print("Exception: main:", str(e))
        return ""
    else:
        return

if __name__ == "__main__":
    main()
