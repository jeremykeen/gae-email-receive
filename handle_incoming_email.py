# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START log_sender_handler]
import logging
import os

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.cloud import storage

import webapp2

# [start config]

# Configure this environment variable via app.yaml
CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']
# [end config]

class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: " + mail_message.sender)
# [END log_sender_handler]
# [START bodies]
        plaintext_bodies = mail_message.bodies('text/plain')
        html_bodies = mail_message.bodies('text/html')

        for content_type, body in html_bodies:
            decoded_html = body.decode()

        try:
            if hasattr(mail_message, 'attachments'):
                for filename, content in mail_message.attachments:
                    decoded_file = content.decode()

                    if not uploaded_file:
                        return 'No file uploaded.', 400

                    # Create a Cloud Storage client.
                    gcs = storage.Client()

                    # Get the bucket that the file will be uploaded to.
                    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)

                    # Create a new blob and upload the file's content.
                    blob = bucket.blob(filename)

                    blob.upload_from_string(
                        content,
                        content_type=content_type
                    )
                    logging.info("blob url:", blob.public_url)
        except:
            logging.exception("Exception decoding attachments in email from %s" % mail_message.sender)
            # ...
# [END bodies]
            logging.info("Html body of length %d.", len(decoded_html))
        for content_type, body in plaintext_bodies:
            plaintext = body.decode()
            logging.info("Plain text body of length %d.", len(plaintext))

# [START app]
app = webapp2.WSGIApplication([LogSenderHandler.mapping()], debug=True)
# [END app]
