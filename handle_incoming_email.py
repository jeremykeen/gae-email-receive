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
import cloudstorage as gcs
import webapp2

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api import app_identity

# [START retries]
my_default_retry_params = gcs.RetryParams(initial_delay=0.2,
                                          max_delay=5.0,
                                          backoff_factor=2,
                                          max_retry_period=15)
gcs.set_default_retry_params(my_default_retry_params)


# [END retries]

# [START write_to_default_bucket]
def write_file(filename, content):
    bucket_name = os.environ.get('BUCKET_NAME',
                                 app_identity.get_default_gcs_bucket_name())
    bucket = '/' + bucket_name + '/'
    file_location = bucket + filename
    logging.info("File location: ", file_location)
    write_retry_params = gcs.RetryParams(backoff_factor=1.1)
    gcs_file = gcs.open(file_location,
                        'w',
                        options={'x-goog-meta-location': 'driveway',
                                 'x-goog-meta-bar': 'bar'},
                        retry_params=write_retry_params)
    gcs_file.write(content.decode())
    gcs_file.close()
    logging.info("image uploaded to cloud storage")


# [END write_to_default_bucket]


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
                    write_file(filename, content)
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
