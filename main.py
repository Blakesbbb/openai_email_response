import os.path
from email.utils import parseaddr

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email
import base64
import openai
from quickstart import credsandtokens
openai.api_key = '___'

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com'
                                                                                        '/auth/gmail.send']


def get_message(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()

        # byte string
        msg_raw = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

        # string
        msg_str = email.message_from_bytes(msg_raw)

        content_types = msg_str.get_content_maintype()
        # One is plain text the other is html
        if content_types == 'multipart':

            parts = msg_str.get_payload()
            # part1 is plain, part2 is html
            part1 = parts[0]
            # print("this is the message body: ")
            # print(part1.get_payload())
            # the message body
            return part1.get_payload(decode=True).decode('UTF-8'), message['threadId']
        else:
            return msg_str.get_payload(decode=True).decode('UTF-8'), message['threadId']

    except HttpError as error:
        print(f'An error occurred: {error}')


def get_sender(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()

        # byte string
        msg_raw = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

        # string
        msg_str = email.message_from_bytes(msg_raw)

        sender_name, sender_email = parseaddr(msg_str['From'])
        return sender_email

    except HttpError as error:
        print(f'An error occurred: {error}')


def search_messages(service, user_id, search_string):
    try:
        search_id = service.users().messages().list(userId=user_id, q=search_string).execute()

        number_results = search_id['resultSizeEstimate']

        final_list = []
        if number_results > 0:
            message_ids = search_id['messages']

            for ids in message_ids:
                final_list.append(ids['id'])

            return final_list
        else:
            print('there were 0 results for that search string, returning an empty search string')
            return ""

    except HttpError as error:
        print(f'An error occurred: {error}')


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


def get_first_msg_id(search_id):
    msg_ids = search_id['messages']
    if msg_ids:
        first_msg_id = msg_ids[0]['id']
        return first_msg_id
    else:
        print("No messages found.")

def get_subject(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='metadata', metadataHeaders=['Subject']).execute()
        subject = message['payload']['headers'][0]['value']
        return subject
    except HttpError as error:
        print(f'An error occurred: {error}')

def generate_chatbot_response(prompt, message_body):

    message_prompt = "Please write me a response to this email that I have received, This is how I would like to respond to it " + prompt + " " + message_body
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message_prompt}
        ]
    )

    model_reply = response.choices[0].message["content"]
    return model_reply # Return the generated response

def main():
    credsandtokens()
    service = get_service()

    user_id = 'me'
    message_id = ""
    while message_id == "":
        search_string = input("Enter the search string: ")
        message_id = search_messages(service, user_id, search_string)

    # print(message_id)

    for i in range(len(message_id)):
        message_body, thread_id = get_message(service, user_id, message_id[i])
        print(f"THIS IS EMAIL {i + 1}")
        print(message_body)

    email_choice = input("Enter which email you would like to respond to: ")
    email_choice = int(email_choice)

    # Call the get_message() function to retrieve the message body
    message_body, thread_id = get_message(service, user_id, message_id[email_choice - 1])

    # Print or manipulate the message body as needed
    print("Message body:")
    print(message_body)
    Prompt = input('How would you like to respond to this email?: ')
    message_prompt = "Please write me a response to this email that I have received, This is how I would like to respond to it " + Prompt + " " + message_body
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message_prompt}
        ]
    )

    model_reply = response.choices[0].message["content"]
    print("Model's reply: ", model_reply)

    Respond_Or_Not = input('Do you wish to use this responses? Type YES or NO:')

    decision_made = False
    while decision_made is False:
        if Respond_Or_Not == "YES":
            decision_made = True
        elif Respond_Or_Not == "NO":
            while True:
                Prompt = input('How would you like to change this response?: ')
                message_prompt = model_reply + " " + Prompt
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": message_prompt}
                    ]
                )
                model_reply = response.choices[0].message["content"]
                print("Model's reply: ", model_reply)
                Respond_Or_Not = input('Do you wish to use this responses? Type YES or NO:')
                if Respond_Or_Not == "YES":
                    break
        else:
            break

    sender = get_sender(service, user_id, message_id[email_choice - 1])
    print(sender)
    subject = input('Enter the Subject of your email: ')
    emailMsg = model_reply
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = sender
    mimeMessage['subject'] = subject
    mimeMessage['In-Reply-To'] = message_id[email_choice - 1]
    mimeMessage['References'] = message_id[email_choice - 1]
    mimeMessage.attach(MIMEText(emailMsg, 'plain'))
    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

    message = service.users().messages().send(userId='me', body={'raw': raw_string, 'threadId': thread_id}).execute()
    print(message)


if __name__ == "__main__":
    main()
# potentially add who email is from
