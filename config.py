CONFIG = {
    'USER_ID': 'me',
    'SENDER': 'your@gmail.com',

    'EMAIL_SUBJECT': 'Subject with $placeholders',

    'URL_SCOPES': 'https://www.googleapis.com/auth/gmail.send',
    'CLIENT_SECRET_FILE': 'client_secret.json',
    'APPLICATION_NAME': 'Gmail API Python - Automatic sender',
    'CREDENTIAL_JSON_FILE': 'gmail-python-auto-sender.json',

    'TEMPLATE_FILE': 'template.html',
    'RECIPIENTS_FILE': 'recipient_list.txt',
    'RECIPIENTS_FILE_SEPARATOR': ',',
    'ATTACHMENT_DIR': 'attachment',
}
