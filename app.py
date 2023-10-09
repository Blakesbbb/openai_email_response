from flask import Flask, request, render_template_string, render_template
from MAIN import *
app = Flask(__name__)

# Define the main route
@app.route('/')
def home():
    return render_template_string("""
        <form action="/search" method="post">
            Enter the search string: <input type="text" name="search_string">
            <input type="submit" value="Search">
        </form>
    """)

@app.route('/search', methods=['POST'])
def search():
    search_string = request.form['search_string']
    service = get_service()
    user_id = 'me'
    message_ids = search_messages(service, user_id, search_string)
    emails = []
    for message_id in message_ids:
        subject = get_subject(service, user_id, message_id) # You'll define this function
        sender = get_sender(service, user_id, message_id)
        emails.append({'id': message_id, 'subject': subject, 'sender': sender})
    return render_template('search_results.html', emails=emails)

@app.route('/email/<message_id>')
def email_details(message_id):
    service = get_service()
    user_id = 'me'
    sender = get_sender(service, user_id, message_id)
    subject = get_subject(service, user_id, message_id)
    body, _ = get_message(service, user_id, message_id)
    return render_template('email_details.html', sender=sender, subject=subject, body=body, message_id=message_id)

@app.route('/respond_to_email/<message_id>', methods=['POST'])
def respond_to_email(message_id):
    service = get_service()
    user_id = 'me'
    sender = get_sender(service, user_id, message_id)
    subject = get_subject(service, user_id, message_id)
    body, _ = get_message(service, user_id, message_id)
    response_prompt = request.form['response_prompt']

    chatbot_response = generate_chatbot_response(response_prompt, body)

    return render_template('response_preview.html', sender=sender, subject=subject, body=body, chatbot_response=chatbot_response)

@app.route('/confirm_or_edit_response/<message_id>', methods=['POST'])
def confirm_or_edit_response(message_id):
    service = get_service()
    user_id = 'me'
    action = request.form['action']
    edited_response = request.form['edited_response']

    if action == 'Use Response':
        sender = get_sender(service, user_id, message_id)
        subject = "Re: Your Email Subject"  # You can customize the subject as needed
        emailMsg = edited_response
        mimeMessage = MIMEMultipart()
        mimeMessage['to'] = sender
        mimeMessage['subject'] = subject
        mimeMessage['In-Reply-To'] = message_id
        mimeMessage['References'] = message_id
        mimeMessage.attach(MIMEText(emailMsg, 'plain'))
        raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

        message = service.users().messages().send(userId=user_id,
                                                  body={'raw': raw_string, 'threadId': message_id}).execute()

        return "Response sent!"
    elif action == 'Edit Response':
        return render_template('response_preview.html', chatbot_response=edited_response, message_id=message_id)


@app.route('/edit_response/<message_id>', methods=['POST'])
def edit_response(message_id):
    current_response = request.form['current_response']
    edit_prompt = request.form['edit_prompt']
    message_prompt = current_response + " " + edit_prompt

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message_prompt}
        ]
    )
    new_response = response.choices[0].message["content"]


    return render_template('response_preview.html', chatbot_response=new_response, message_id=message_id)

if __name__ == "__main__":
    app.run(debug=True)