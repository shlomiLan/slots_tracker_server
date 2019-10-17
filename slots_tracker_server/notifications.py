import json
import os

from firebase_admin import credentials, firestore, initialize_app
from pyfcm import FCMNotification


class Notifications:
    def __init__(self, name=None):
        api_key = os.environ.get('FIREBASE_API_KEY')
        os.environ['GRPC_DNS_RESOLVER'] = 'native'
        if not api_key:
            raise KeyError('No firebase API key')
        self.push_service = FCMNotification(api_key=api_key)

        credentials_data = os.environ.get('FIREBASE_CREDENTIALS')
        if not credentials_data:
            raise KeyError('No credentials data, missing environment variable')

        credentials_data = json.loads(credentials_data)
        # Fix the 'private_key' escaping
        credentials_data['private_key'] = credentials_data.get('private_key').encode().decode('unicode-escape')

        # Use the application default credentials
        cred = credentials.Certificate(credentials_data)
        if name:
            initialize_app(cred, name=name)
        else:
            initialize_app(cred)

        self.db = firestore.client()

    def send(self, title, message, target_env, collection='devices', dry_run=False):
        errors = []
        docs_ref = self.db.collection(collection)
        docs = docs_ref.get()

        for doc in docs:
            try:
                doc_as_dict = doc.to_dict()
                token = doc_as_dict.get('token')
                env = doc_as_dict.get('env')
                if env == target_env:
                    self.push_service.notify_single_device(registration_id=token, message_title=title,
                                                           message_body=message, dry_run=dry_run)
            except Exception as e:
                errors.append(e)

        return errors
