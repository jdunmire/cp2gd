# Copy a file to Google Drive
Copy a single file to Google drive. The file will be copied to your
Google drive root directory ("My Drive") or you can specify a folder.
The folder must exist.

While the script itself is simple to use, two sets of permissions are
required to access Google drive: one set authorizies uses of the Google
API and the second authorizes access to a specific Google Drive account.
So pay close attention to the setup instructions.

## Usage
    python ./cp2gd.py [OPTIONS] source [dest]

The `source` file will be copied to `dest` on Google Drive. If `dest` is
not specified the `source` basename is also used as the `dest`.

To copy to an existing Google Drive folder use the `--folder` option.

A full list of options is avaialbe from from the script itself:

    python ./c2gd.py --help


## Setup
Setup for this script is complicated by the need to both install a
Python library and to get two sets of permissions from Google.


### Install Google API library
Installing the needed library is easy:

    pip install google-api-python-client


### Get application secrets
These _secrets_ authorize the use use of Google APIs by an application.
They are assocated with the _developer_ of the application and used by
Google to track and report the API use.

Google expects that an application developer will provide these secrets
to the application users. However, I am not interested in who uses this
application, nor how they use it, so I am not distributing the secrets.
You will have to obtain your own secrets (they're free):

  1. At https://cloud.google.com/console#/flows/enableapi?apiid=drive
     * Create New Project
  2. A `Register new application` page comes up:
     * Set the name of the project to `cp2gd`
     * Set the plaform to `Native`
  3. Next page:
     * Download JSON and save in `~/.cache/cp2gd.py/client_secrets.json`
     * Press the Update button under the `CONSENT SCREEN` label
  4. On the `Consent Screen`,
     * Change the `PRODUCT NAME` to `cp2gd`
     * Click on the `Save` button at the bottom of the page

Step 4 is optional and you can use any _Project_ and _Product_ name you
like. The important parts are to set the platform to `Native` and save
the JSON file as `~/.cache/cp2gd.py/client_secrets.json`.


### Get Account Credentials
Credentials are assocated with the user of the application. They grant
an application \(`cp2gd.py` in this case\) access to a user's resources
\(such as _files_ and _directories_\). These should be kept in a secure,
private, location.

`cp2gd.py` will request the necessary permissions and write the
authorizing credentials to `~/.cache/cp2gd.py/credentials`. The
authorization process requires a browser. If you do not have browser on
the system where you will be using `cp2gd.py` then you have two choices:

  1. Use the `--noauth_local_webserver` option, open the generated URL
     on any system with a browser, and ollow the instructions to obtain a
     verification code. Then enter the code at the prompt from cp2gd.py

  2. Run `cp2gd.py` on a system with a browser and copy the
     `~/.cache/cp2gd.py/credentials` to the system that does not have a
     browser.

