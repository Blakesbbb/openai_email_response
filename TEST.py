import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import email
import base64
import MAIN
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    return service

"""
service = get_service()
print(service)
search_id = service.users().messages().list(userId='me', q='CRAZY').execute()
print(search_id)
msg_id = MAIN.get_first_msg_id(search_id)
#msg_id = '18907acf616713d1'
print(msg_id)

message_list = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
#print(message_list)

message = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()

msg_raw = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
#print(msg_raw)
# string
msg_str = email.message_from_bytes(msg_raw)
#print(msg_str)
content_types = msg_str.get_content_maintype()

part1, part2 = msg_str.get_payload()
# the message body
print(part1.get_payload())
"""
import openai

openai.api_key = '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'

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "PLEASE TYPE 123 BACK TO ME"}
    ]
)

model_reply = response.choices[0].message["content"]
print("Model's reply: ", model_reply)


# Get the Gmail service
"""service = get_service()

user_id = 'me'
search_string = input("Enter the search string: ")
message_id = MAIN.search_messages(service, user_id, search_string)
print(message_id)

for i in range(len(message_id)):
    message_body = MAIN.get_message(service, user_id, message_id[i])
    print(f"THIS IS EMAIL {i+1}")
    print(message_body)

email_choice = input("Enter which email you would like to respond to: ")
email_choice = int(email_choice)

# Call the get_message() function to retrieve the message body
message_body = MAIN.get_message(service, user_id, message_id[email_choice-1])

# Print or manipulate the message body as needed
print("Message body:")
print(message_body)"""

"""Respond_Or_Not = input('Do you wish to use one of these responses? Type YES or NO:')
 if Respond_Or_Not == "YES":
     Response_Choice = input('Which response do you choose?: ')
     Final_Response_Prompt = Response_Choice + model_reply + "Please respond with Just the response choice nothing else."
     Final_Response = openai.ChatCompletion.create(
         model="gpt-3.5-turbo",
         messages=[
             {"role": "system", "content": "You are a helpful assistant."},
             {"role": "user", "content": Final_Response_Prompt}
         ]
     )
     Final_Response = response.choices[0].message["content"]
     print(Final_Response)"""