#! python
# -*- coding: utf-8 -*-

import os
import argparse
import requests

def upload_file(url, file, password=None):
    try:
        filename = os.path.basename(file)
        if not url.endswith(filename):
            url = f"{url}/{filename}"
        headers = {"Authorization": password} if password else None

        with open(file, 'rb') as f:
            files = {'file': (filename, f)}
            response = requests.put(url, headers=headers, files=files)

            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Upload an RELEASES to the update server")
    parser.add_argument("url", help="Upload URL (e.g., http://host:port/api/v1/publish/vlocation/win32/x64/1.0.0-alpha2/)")
    parser.add_argument("file", help="Path to the file to upload")
    parser.add_argument("--password", default="admin", help="Authorization password (default: admin)")

    args = parser.parse_args()
    upload_file(args.url, args.file, args.password)

if __name__ == "__main__":
    main()