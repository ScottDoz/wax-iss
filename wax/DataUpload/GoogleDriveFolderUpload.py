# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 14:49:32 2026

@author: scott
"""

import os
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

import tkinter as tk
from tkinter import filedialog

SCOPES = [
    "https://www.googleapis.com/auth/drive.file"
]

def get_drive_service():

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as f:
            f.write(creds.to_json())

    return build(
        "drive",
        "v3",
        credentials=creds
    )

def create_drive_folder(service, folder_name, parent_id=None):
    """Create a folder on Google Drive and return its ID."""

    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder"
    }

    if parent_id:
        metadata["parents"] = [parent_id]

    folder = service.files().create(
        body=metadata,
        fields="id"
    ).execute()

    return folder["id"]


def upload_file(service, filepath, parent_id):
    """Upload a single file into a Drive folder."""

    metadata = {
        "name": os.path.basename(filepath),
        "parents": [parent_id]
    }

    media = MediaFileUpload(
        filepath,
        resumable=True
    )

    file = service.files().create(
        body=metadata,
        media_body=media,
        fields="id"
    ).execute()

    print(f"Uploaded: {filepath}")


def upload_folder(service, local_folder, drive_parent_id):
    """
    Recursively upload a folder and preserve structure.
    """

    folder_name = os.path.basename(local_folder)

    # Create matching folder in Drive
    drive_folder_id = create_drive_folder(
        service,
        folder_name,
        drive_parent_id
    )

    for item in os.listdir(local_folder):

        local_path = os.path.join(
            local_folder,
            item
        )

        if os.path.isdir(local_path):
            upload_folder(
                service,
                local_path,
                drive_folder_id
            )

        else:
            upload_file(
                service,
                local_path,
                drive_folder_id
            )

if __name__ == "__main__":
    
    # Hide the main Tk window
    root = tk.Tk()
    root.withdraw()
    
    # Example usage
    #LOCAL_FOLDER = r"C:\Users\scott\Documents\Repos\WaxPropulsion\ISS\TestDataFolder"
    
    LOCAL_FOLDER = filedialog.askdirectory(
        title="Select a folder to upload"
    )
    
    if LOCAL_FOLDER:
        print("Selected:", LOCAL_FOLDER)
        
        # Optional: existing Drive folder ID where you want this uploaded
        DRIVE_PARENT_ID = "1jTAhYvGxmjKYETKUjFiCbowm5QZTbeFO"
        
        # This creates the authenticated Google Drive connection
        service = get_drive_service()
        
        upload_folder(
            service,
            LOCAL_FOLDER,
            DRIVE_PARENT_ID
        )
        
    else:
        print("No folder selected.")
    
    