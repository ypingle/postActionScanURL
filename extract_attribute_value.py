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
SAST_proxy = config['SAST_proxy']
proxy_servers = {
   'https': SAST_proxy
}

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
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def SAST_get_access_token():
    try:
        payload = {
            'scope': 'access_control_api',
            'client_id': 'resource_owner_client',
            'grant_type': 'password',
            'client_secret': '014DF517-39D1-4453-B7B3-9930C563627C',
            'username': SAST_username,
            'password': SAST_password
        }

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(
            f"{SAST_url}/CxRestAPI/auth/identity/connect/token",
            headers=headers,
            data=payload,
            verify=False, 
            proxies=proxy_servers
        )

        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        access_token = response.json().get('access_token', '')

    except requests.exceptions.RequestException as e:
        print(f"Exception: SAST_get_access_token - {e}")
        return ""
    except Exception as e:
        print(f"Exception: SAST_get_access_token - {e}")
        return ""
    else:
        return access_token

def SAST_get_teams(access_token):
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        url = f"{SAST_url}/CxRestAPI/auth/teams"

        response = requests.get(url, headers=headers, verify=False, proxies=proxy_servers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        teams_json = response.json()

    except requests.exceptions.RequestException as e:
        print(f"Exception: SAST_get_teams - {e}")
        return []
    except Exception as e:
        print(f"Exception: SAST_get_teams - {e}")
        return []
    else:
        return teams_json

def SAST_get_team_members(access_token, team_id):
    try:
        headers = {'Authorization': 'Bearer ' + access_token}
        url = f"{SAST_url}/CxRestAPI/auth/teams/{team_id}/Users"

        response = requests.get(url, headers=headers, verify=False, proxies=proxy_servers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        response_json = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Exception: SAST_get_team_members - {e}")
        return []
    except Exception as e:
        print(f"Exception: SAST_get_team_members - {e}")
        return []
    else:
        return response_json

def get_team_email_recipients(xml_team_full_path):
    try:
        access_token = SAST_get_access_token()

        if not access_token:
            return ""

        teams_list = SAST_get_teams(access_token)
        team_id = 0

        print('Team list:')
        for team in teams_list:
            team_name = team['fullName'].lstrip('/')
            print(f'id: {team["id"]} name: {team_name}')

            if team_name == xml_team_full_path.replace('\\','/'):
                team_id = team['id']
                print('Team match found:', team_name)
                break

        if team_id > 0:
            team_members = SAST_get_team_members(access_token, team_id)
            email_recipients = ','.join(member['email'] for member in team_members)
            return email_recipients

    except Exception as e:
        print("Exception: get_email_recipients_from_team:", str(e))
        return ""

def main():
    try:
        if len(sys.argv) < 2:
            print("Usage: python script_name.py <path_to_xml_file> <optional:email_recipient>")
            return

        xml_file_path = sys.argv[1]

        with open(xml_file_path, 'r', encoding='utf-8') as file:
            xml_content = file.read()

        team_attribute = "TeamFullPathOnReportDate"
        email_recipients = sys.argv[2] if len(sys.argv) == 3 else get_team_email_recipients(extract_attribute_from_xml(xml_content, team_attribute))

        print('email_recipients:', email_recipients)

        # Specify the attribute you want to extract (e.g., "DeepLink")
        deeplink_attribute = "DeepLink"
        # Extract the value of the specified attribute from the XML content
        deep_link = extract_attribute_from_xml(xml_content, deeplink_attribute)

        # Set email variables
        email_from = Email_from
        email_subject = Email_subject
        email_body = f"{Email_body}\n{deep_link}"

        # Send email
        send_email(email_from, email_recipients, email_subject, email_body)
        
    except Exception as e:
        print("Exception: main:", str(e))
    else:
        print("Email sent successfully.")

if __name__ == "__main__":
    main()
