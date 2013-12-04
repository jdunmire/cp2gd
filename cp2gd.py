#!/usr/bin/env python
#
# Copyright 2013 Jerry E Dunmire
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
#

"""Copy to Google Drive
Usage:
    $ python cp2gd.py [OPTIONS] source [dest]

For additional help:
    $ python cp2gd.py --help

"""

import argparse
import httplib2
import os
import sys
from mimetypes import MimeTypes

# Google Drive libraries
try:
    from apiclient import discovery
    from apiclient import errors as apierrors
    from apiclient.http import MediaFileUpload
    from oauth2client import file as oa2file
    from oauth2client import client as oa2client
    from oauth2client import tools as oa2tools
except ImportError as err:
    sys.stderr.write("ERROR: You need to install " +
            "google-api-python-client.\n")
    sys.exit(1)


def getGoogleDriveService(cmdLineFlags):
    # Store credentials in ~/.cache/<thisProgram>/... because
    #   - credentials are assocated with a user account, not a system
    #   - ~/.cache is mode 700 (at least on Ubuntu), though that should be
    #     verified.
    # 
    CREDENTIALS = os.path.join(os.path.expanduser("~"), '.cache',
            os.path.basename(__file__), "credentials")
    _CLIENTS_SECRETS_MESSAGE = "Missing secrets %s"
    CLIENT_SECRETS = os.path.join(os.path.expanduser("~"), '.cache',
            os.path.basename(__file__), "client_secrets.json")

    # See https://developers.google.com/drive/scopes for a description of
    # the available scopes. Un-needed scopes have been commented out.
    FLOW = oa2client.flow_from_clientsecrets(CLIENT_SECRETS,
            scope=[
              'https://www.googleapis.com/auth/drive.file',
              'https://www.googleapis.com/auth/drive',
        #      'https://www.googleapis.com/auth/drive.apps.readonly',
        #      'https://www.googleapis.com/auth/drive.readonly',
        #      'https://www.googleapis.com/auth/drive.metadata.readonly',
        #      'https://www.googleapis.com/auth/drive.install',
              'https://www.googleapis.com/auth/drive.appdata',
        #      'https://www.googleapis.com/auth/drive.scripts',
              ],
            message= "Missing secrets %s" % CLIENT_SECRETS)

    # Get credentials and save them in a secure location
    if not os.path.isdir(os.path.dirname(CREDENTIALS)):
        os.makedirs(os.path.dirname(CREDENTIALS), 0700)
    storage = oa2file.Storage(CREDENTIALS)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = oa2tools.run_flow(FLOW, storage, cmdLineFlags)

    # Now authorize the credentials and setup the service
    http = httplib2.Http()
    http = credentials.authorize(http)
    return discovery.build('drive', 'v2', http=http)


# Setup command line processing
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[oa2tools.argparser])
parser.add_argument('--file-description',
    dest='desc',
    help='Short description to be displayed by Google Drive',
    default="Uploaded by %s" % os.path.basename(__file__))
parser.add_argument('--folder', default= '/')
parser.add_argument('--mime-type',
    dest='mime_type',
    help='''If not specified then a mime-type will be
    guessed using the source filename. Defaults to 
    application/octet-stream if the guess fails''',
    default=None)
parser.add_argument("source", nargs='?', default=None)
parser.add_argument("dest", nargs='?',default=None)


def main(argv):
    flags = parser.parse_args(argv[1:])
    service = getGoogleDriveService(flags)

    if flags.source is None:
        print "No file specified."
        sys.exit(1)

    source = flags.source
    if flags.dest is None:
        dest = source
    else:
        dest = flags.dest

    if flags.mime_type is None:
        mime = MimeTypes()
        mime_type = mime.guess_type(os.path.basename(flags.source))[0]
        if mime_type == None :
            mime_type = "application/octet-stream"  # use this for the default
    else:
        mime_type = flags.mime_type

    try:
        parent_id = None
        if flags.folder != '/':
            # find parent IDs, create if they don't exist
            try:
                param = {
                   'maxResults': 1,
                   'q': 'title = "' + flags.folder + 
                        '" and mimeType = "application/vnd.google-apps.folder"' +
                        'and trashed = false'
                   }
                parent = service.files().list(**param).execute()
                if len(parent['items']) > 0:
                    parent_id = parent['items'][0]['id']
                    #print 'parent id = %s' % parent_id
                else:
                    print 'ERROR: folder "%s" not found.' % flags.folder
                    sys.exit(1)
            
            except apierrors.HttpError, error:
                print 'An error occured: %s' % error




        media_body = MediaFileUpload(flags.source, mimetype=mime_type, resumable=True)
        body = {
        'title': dest,
        'description': flags.desc,
        'mimeType': mime_type,
        }

        # Set the parent folder.
        if parent_id is not None:
            body['parents'] = [{'id': parent_id}]

        try:
            file = service.files().insert(
                body=body,
                media_body=media_body).execute()

            # Uncomment the following line to print the File ID
            # print 'File ID: %s' % file['id']

        except apierrors.HttpError, error:
            print 'An error occured: %s' % error

    except oa2client.AccessTokenRefreshError:
        sys.stderr.write("ERRRO: The credentials have been revoked or " +
                "expired please re-run the application to re-authorize.")
        sys.exit(1);


if __name__ == '__main__':
    main(sys.argv)
