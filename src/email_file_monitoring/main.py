#%%
import os
import imaplib
import email
import json
import fnmatch
from pathlib import Path
import keyring
import configparser
# pylint: disable=import-error
from utils.password import get_password as pw
# pylint: enable=import-error

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

# set up IMAP connection
# config = configparser.ConfigParser()
# config.read('connection.ini')
# # for local connection settings not to be uploaded to github
# config.read('connection_local.ini')

if os.path.exists('imap_accounts_local.json'):
    with open('imap_accounts_local.json') as f:
        imap_accounts = json.load(f)
else:
    with open('imap_accounts.json') as f:
        imap_accounts = json.load(f)

#%%
for account in imap_accounts['imap_accounts']:
    # if account['account_name'] == 'Sample Account Name - Will Be Ignored':
    #     continue

    # account_name = config.get('IMAP', 'account_name') 
    # imap_server = config.get('IMAP', 'imap_server')
    # imap_port = config.getint('IMAP', 'imap_port')
    # imap_username = config.get('IMAP', 'imap_username')
    # imap_password_key = config.get('IMAP', 'imap_password_key')
    # imap_password = keyring.get_password(account_name, imap_password_key)

    account_name = account['account_name']
    imap_username = account['imap_username']
    imap_server = account['imap_server']
    imap_port = account['imap_port']
    imap_password_key = account['imap_password_key']
    #imap_password = keyring.get_password(account_name, imap_password_key)
    imap_password = pw(account_name, imap_password_key)
    json_filename = f'{account_name}_email_rules.json'

    if os.path.exists(json_filename):
        with open(json_filename) as f:
            config_data = json.load(f)
    else:
        with open("default_email_rules.json") as f:
            config_data = json.load(f)

    with imaplib.IMAP4_SSL(imap_server.lower(), imap_port) as imap_conn:
        # log in to your Gmail account
        imap_conn.login(imap_username.lower(), imap_password.lower())

        # select the mailbox you want to check
        mailbox = 'INBOX'
        imap_conn.select(mailbox)

        # search for all unread emails in the mailbox
        typ, data = imap_conn.search(None, 'UNSEEN')

        if len(data[0]) == 0:
            print('No Unread messages to process')

        for email_id in data[0].split():
            # fetch the email content
            typ, email_data = imap_conn.fetch(email_id, '(RFC822)')

            # mark the email as unread
            # imap_conn.store(email_id, '-FLAGS', '\\Seen')

            # parse the email content
            email_message = email.message_from_bytes(email_data[0][1])

            # extract relevant fields from the email message
            email_subject = email_message['Subject'].lower()
            email_from = email_message['From'].lower()
            email_to = email_message['To'].lower()
            email_date = email_message['Date'].lower()

            # extract the email body
            if email_message.is_multipart():
                for part in email_message.get_payload():
                    content_type = part.get_content_type()
                    if content_type == "multipart/alternative":
                        for subpart in part.get_payload():
                            subpart_content_type = subpart.get_content_type()
                            if subpart_content_type == "text/plain":
                                email_body = subpart.get_payload(decode=True).decode().lower()
                                break
                            elif subpart_content_type == "text/html":
                                email_body = subpart.get_payload(decode=True).decode().lower()
                                break
                        if email_body:
                            break
                    elif "text" in content_type:
                        email_body = part.get_payload(decode=True).decode().lower()
                        break
            else:
                email_body = email_message.get_payload(decode=True).decode().lower()

            # check for attachments
            attachments = []
            for part in email_message.walk():
                if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                    continue
                filename = part.get_filename()
                if filename:
                    attachments.append(filename.lower())

            # check if email meets any of the defined patterns
            for condition in config_data['conditions']:
                condition_name = condition['name']
                if condition_name == 'example_entry_will_be_ignored':
                    continue

                if 'delivery' in condition:
                    delivery_target = condition['delivery']['target']
                    delivery_path = condition['delivery']['path']
                else:
                    target = None
                    path = None

                pattern = condition['pattern']

                meets_criteria = True

                # check sender pattern
                if 'sender' in pattern and pattern['sender'].lower() not in email_from:
                    meets_criteria = False
                    continue

                # check subject patterns
                if 'subject' in pattern:
                    subject_patterns = pattern['subject']
                    subject_matches = [pattern for pattern in subject_patterns if pattern.lower() in email_subject]
                    if not subject_matches:
                        meets_criteria = False
                        continue

                # check body patterns
                if 'body' in pattern:
                    body_patterns = pattern['body']
                    body_matches = [pattern for pattern in body_patterns if pattern.lower() in email_body]
                    if not body_matches:
                        meets_criteria = False
                        continue
                    
                # check attachment pattern
                if meets_criteria and 'attachments' in pattern:
                    any_attachment_matched = False
                    for i, attachment in enumerate(attachments):
                        attachment_matches = [pattern.lower() for pattern in pattern['attachments'][0]['filename']]
                        if attachment.lower() in attachment_matches:
                            print(f'Attachment {i+1} meets the condition: {condition_name}')
                            if not os.path.exists(delivery_path):
                                os.makedirs(delivery_path)
                            filepath = Path(delivery_path) / attachment
                            with open(filepath, 'wb') as f:
                                f.write(part.get_payload(decode=True))
                            any_attachment_matched = True
                    if not any_attachment_matched:
                        meets_criteria = False
                        continue


                    # mark email as read
                    # imap_conn.store(email_id, '+FLAGS', '\\Flagged')

                    # this prevents the email from being compared against other patterns.  If you wish to have the email evaluated against other conditions, such as to extract other attachments, remove these lines
                    if meets_criteria == True:
                        break

        # close the IMAP connection
        imap_conn.close()
        imap_conn.logout()
