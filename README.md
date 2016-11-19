# PythonApiGmail
Send email using gmail api.

## Usage
```
python send_email.py
```

## Configuration
Follow this link (https://developers.google.com/gmail/api/quickstart/python) to set Google to allow request to Gmail API.
 
You will need to set the file config.py. Below is a short description of the parameters.

'USER_ID': user's email or the word 'me'.<br>
'SENDER': sender's email.<br>

'EMAIL_SUBJECT': Subject of the email. It can have placeholders.<br>

'URL_SCOPES': For this application, the scope is https://www.googleapis.com/auth/gmail.send<br>
'CLIENT_SECRET_FILE': secret json file generated in https://console.cloud.google.com/apis/credentials<br>
'APPLICATION_NAME': The name of the application.<br>
'CREDENTIAL_JSON_FILE': File which will be used to save oath credentials.<br>

'TEMPLATE_FILE': File with the body template. It can have the extensions .txt or .html.<br>
'RECIPIENTS_FILE': File with the placeholders values. It must have the email column.<br>
'RECIPIENTS_FILE_SEPARATOR': Separator used in Recipient File.<br>
'ATTACHMENT_DIR': Folder with all files which will be attached.<br>

## Placeholders
Placeholders can be used in Subject and Template File. It must start with $ symbol.

If the value does not exists in Recipient File, it will show the placeholder name (no exception will raise).

## Recipient list file
The recipient file must have the email column and any other used in template or subject.

The column name is without the $ symbol.

## Example
### Subject
```
Happy christmas $friend!
```

### Template
```
Dear $friend,

I am sending you $thing.

$missing_placeholder

Regards,
Me
```

### Recipient list
```
email, friend, thing
Tim <tim@email.com>, Tim, a laptop
ben@email.com, Ben, a cake
tal@email.com, Tal, a t-shirt
```

## result
The send_email.py will send one email for each line in the Recipient File.

For the first line, this will be the result.
```
From: <from config>
To: Tim <tim@email.com>
Subject: Happy christmas Tim!
Body:
Dear Tim,

I am sending you a laptop.

$missing_placeholder

Regards,
Me
```