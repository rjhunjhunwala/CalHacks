import cv2
import io
from imageio import imread
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from apiclient import errors
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

def get_service():
    """
    Set up to get API call
    :return: a service to use
    """
    store = file.Storage('token.json')
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    return service
def upload_file(file_name):
    """
    upload a file
    :param file_name: local filename
    :return: None
    """
    file_metadata = {'name': file_name}
    media = MediaFileUpload(file_name)
    fil = get_service().files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
def get_string_from_file(title):
    """
    get's a string from the file
    :param title: the given title
    :return: the string
    """
    results = get_service().files().list(
        pageSize=30, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    for item in items:
        if item['name'] == title:
            file_id = item['id']
            request = get_service().files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            return fh.getvalue()
    return None #bad title...

def getCV2_from_file(title):
    """
    get's a CV2 image from file
    :param title:
    :return: a valid cv2 image
    """
    results = get_service().files().list(
        pageSize=30, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    for item in items:
        if item['name'] == title:
            file_id = item['id']
            request = get_service().files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            overwritten = open("overwriteme.jpg","wb")
            overwritten.write(fh.getvalue())
            overwritten.close()
            return cv2.imread("overwriteme.jpg")

    return None #bad title..
