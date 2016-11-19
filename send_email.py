from __future__ import print_function, unicode_literals
import os
import base64
import httplib2
import glob

from string import Template
from collections import namedtuple
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from apiclient import discovery
from apiclient import errors

import mimetypes
import argparse

import config

flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()


def info(message):
    print (message)


class Credentials(object):
    def __init__(self, url_scopes, client_secret_file, application_name, credential_json_file):
        self.url_scopes = url_scopes
        self.client_secret_file = client_secret_file
        self.application_name = application_name
        self.credential_json_file = credential_json_file

        self.home_dir = os.path.expanduser('~')
        self.credential_dir = os.path.join(self.home_dir, '.credentials')

    @classmethod
    def new_from_json(cls, data):
        return cls(
            url_scopes=data.get('URL_SCOPES'),
            client_secret_file=data.get('CLIENT_SECRET_FILE'),
            application_name=data.get('APPLICATION_NAME'),
            credential_json_file=data.get('CREDENTIAL_JSON_FILE')
        )

    def get_credential(self):
        if not os.path.exists(self.credential_dir):
            os.makedirs(self.credential_dir)

        credential_path = os.path.join(self.credential_dir, self.credential_json_file)
        store = Storage(credential_path)
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.client_secret_file, self.url_scopes)
            flow.user_agent = self.application_name
            credentials = tools.run_flow(flow, store, flags)
            info('Storing credentials to ' + credential_path)

        return credentials


class Message(object):
    def __init__(self, service, user_id, sender):
        self.service = service
        self.user_id = user_id
        self.sender = sender

    @classmethod
    def new_from_json(cls, data):
        http = (Credentials.new_from_json(data)
                .get_credential()
                .authorize(httplib2.Http()))
        serv = discovery.build('gmail', 'v1', http=http)

        return cls(
            service=serv,
            user_id=data.get('USER_ID'),
            sender=data.get('SENDER')
        )

    def _create_message(self, to, subject, message_text, message_sub_type='plain'):
        message = MIMEText(message_text, message_sub_type)
        message['to'] = to
        message['from'] = self.sender
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_string())}

    def _create_message_with_attachment(self,
                                        to, subject, message_text,
                                        attachments, message_sub_type='plain'):
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = self.sender
        message['subject'] = subject
        message.attach(MIMEText(message_text, message_sub_type))

        for path in attachments:
            if not os.path.isfile(path):
                raise Exception('File {} does not exists.'.format(path))

            _, filename = os.path.split(path)
            content_type, encoding = mimetypes.guess_type(path)

            if content_type is None or encoding is not None:
                content_type = 'application/octet-stream'

            main_type, sub_type = content_type.split('/', 1)
            if main_type == 'text':
                fp = open(path, 'rb')
                msg = MIMEText(fp.read(), _subtype=sub_type)
                fp.close()
            elif main_type == 'image':
                fp = open(path, 'rb')
                msg = MIMEImage(fp.read(), _subtype=sub_type)
                fp.close()
            elif main_type == 'audio':
                fp = open(path, 'rb')
                msg = MIMEAudio(fp.read(), _subtype=sub_type)
                fp.close()
            else:
                fp = open(path, 'rb')
                msg = MIMEBase(main_type, sub_type)
                msg.set_payload(fp.read())
                fp.close()

            msg.add_header('Content-Disposition', 'attachment', filename=filename)
            message.attach(msg)

        return {'raw': base64.urlsafe_b64encode(message.as_string())}

    def _send_message(self, message):
        try:
            message = (self.service
                       .users().messages()
                       .send(userId=self.user_id, body=message)
                       .execute())

            print('  Message Id: {}'.format(message['id']))
            return message

        except errors.HttpError, error:
            print('An error occurred: %s'.format(error))

    def send_message(self, to, subject, message_text, attachments, message_sub_type='plain'):
        if len(attachments) == 0:
            message = self._create_message(to, subject, message_text, message_sub_type)
        else:
            message = self._create_message_with_attachment(to, subject, message_text, attachments, message_sub_type)

        self._send_message(message)


class EmailSender(object):
    def __init__(self, config):
        self.config = config
        self.template_file = config.get('TEMPLATE_FILE')
        self.email_subject = config.get('EMAIL_SUBJECT')
        self.recipients_file = config.get('RECIPIENTS_FILE')
        self.recipients_file_separator = config.get('RECIPIENTS_FILE_SEPARATOR')
        self.attachment_dir = config.get('ATTACHMENT_DIR')

        self.template_is_html = os.path.splitext(self.template_file)[1].upper() == '.HTML'

    def _get_body_template(self):
        with open(self.template_file) as f:
            template = f.read()
        f.close()

        return Template(template)

    def _get_subject_template(self):
        return Template(self.email_subject)

    def _get_recipients(self):
        recipients = []
        with open(self.recipients_file) as f:
            for line in f:
                if line.strip() == '':
                    continue

                line = map(lambda x: x.strip(), line.split(self.recipients_file_separator))
                recipients.append(line)
        f.close()

        fields = recipients[0]
        Recipient = namedtuple('Recipient', ' '.join(fields))
        return [Recipient(*r) for r in recipients[1:]]

    def _get_attachments(self):
        return [x for x in glob.glob(os.path.join(self.attachment_dir, '*.*'))]

    def run(self):
        info('>>> Start sending emails')
        body_template = self._get_body_template()
        subject_template = self._get_subject_template()
        recipients = self._get_recipients()
        attachments = self._get_attachments()
        sub_type = 'html' if self.template_is_html else 'plain'

        info('Connecting to Gmail')
        message = Message.new_from_json(self.config)

        for r in recipients:
            info('Send to: {}'.format(r.email))
            args = r._asdict()
            body = body_template.safe_substitute(**args)
            subject = subject_template.safe_substitute(**args)

            message.send_message(r.email, subject, body, attachments, sub_type)

        info('<<<< Finished')


def main():
    sender = EmailSender(config.CONFIG)
    sender.run()


if __name__ == '__main__':
    main()
