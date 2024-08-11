"""
AR, 2018-11
Class GoogleMediaItem - stores information about media item from Google Photos
"""

# general imports
import os
import requests
from datetime import datetime
from enum import Enum


class MediaType(Enum):
    IMAGE = "image"
    VIDEO = "video"

    @staticmethod
    def from_mime_type(mime_type: str):
        if mime_type.startswith("image/"):
            return MediaType.IMAGE
        elif mime_type.startswith("video/"):
            return MediaType.VIDEO
        else:
            raise ValueError(f"Unsupported MIME type: {mime_type}")

    def get_download_parameter(self):
        if self == MediaType.IMAGE:
            return "d"
        elif self == MediaType.VIDEO:
            return "dv"
        else:
            raise ValueError(f"Download parameter not know for {self}")


class GoogleMediaItem:
    def __init__(self, name=None, item_id=None, base_url=None, creation_date=None, media_type=None):
        self.name = name
        self.id = item_id
        self.base_url = base_url
        self.creation_date = creation_date
        self.media_type = media_type


    def __str__(self):
        return 'Media item {}: {}'.format(self.name, self.base_url)

    def from_dict(self, dictionary):
        """
        Sets GoogleMediaItem object attributes to values given in dictionary

        :param dictionary: with info about one of media items from list returned
        by Google APIs request:
        service.mediaItems().search(body).execute()['mediaItems']
        :return: None
        """

        required_keys = ['filename', 'id', 'baseUrl', 'mediaMetadata', 'mimeType']
        assert all(key in list(dictionary.keys()) for key in required_keys), \
            'Dictionary missing required key. GoogleMediaItem.from_dict() ' \
            'requires keys: {}'.format(required_keys)

        assert 'creationTime' in dictionary['mediaMetadata']

        self.name = dictionary['filename']
        self.id = dictionary['id']
        self.base_url = dictionary['baseUrl']
        # The [:-1] is to drop the trailing Z, which datetime doesn't like
        self.creation_date = datetime.fromisoformat(dictionary['mediaMetadata']['creationTime'][:-1])
        self.media_type = MediaType.from_mime_type(dictionary['mimeType'])

    def download(self):
        """
        Downloads media item to given directory (with metadata, except GPS).
        Info about download URL:
        https://developers.google.com/photos/library/guides/access-media-items#image-base-urls

        :param directory: destination directory for downloaded item
        :return: filename, full path to saved media item
        """

        # Setting filename (full path) and URL of file to download
        download_url = f'{self.base_url}={self.media_type.get_download_parameter()}'


        with requests.get(download_url, stream=True) as response:
            # Raise an exception for HTTP errors
            response.raise_for_status()

            # Iterate over the response in chunks
            for chunk in response.iter_content(chunk_size=(10*1024*1024)):
                # Filter out keep-alive new chunks
                if chunk:
                    yield chunk

