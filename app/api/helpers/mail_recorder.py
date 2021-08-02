import json
from datetime import datetime

from envparse import env


class MailRecorder:
    store = []
    inbox = {}

    def __init__(self, save_to_file=False, in_memory=False, use_env=False) -> None:
        if use_env:
            save_to_file = env.bool('MAIL_RECORDER_SAVE_TO_FILE', default=save_to_file)
        self.save_to_file = save_to_file
        self.in_memory = save_to_file or in_memory

    def record(self, message) -> None:
        if self.in_memory:
            message = dict(time=str(datetime.now()), **message)
            self.store.append(message)
            to = message['to']
            self.inbox[to] = self.inbox.get(to, []) + [message]

        if self.save_to_file:
            with open('generated/mails.json', 'w') as fi:
                json.dump(self.store, fi, indent=4)
