import xml.etree.ElementTree as ET
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
        
        smtp_obj.login(SMTP_user, SMTP_password)  
        smtp_obj.sendmail(sender, recipients, message.as_string())  # Send email to all recipients
         
        smtp_obj.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("Usage: python script_name.py path_to_xml_file email_recipients")
        return
    
    xml_file_path = sys.argv[1]
    email_recipients = sys.argv[2]    
    try:
        with open(xml_file_path, 'r', encoding='utf-8') as file:
            xml_content = file.read()
    except FileNotFoundError:
        print(f"File '{xml_file_path}' not found.")
        return

    # Specify the attribute you want to extract (e.g., "DeepLink")
    desired_attribute = "DeepLink"

    # Extract the value of the specified attribute from the XML content
    attribute_value = extract_attribute_from_xml(xml_content, desired_attribute)

       # Set email variables
    email_from = Email_from
    email_subject = Email_subject
    email_body = Email_body + "\n" + attribute_value
    # Send email
    send_email(email_from, email_recipients, email_subject, email_body)


if __name__ == "__main__":
    main()
