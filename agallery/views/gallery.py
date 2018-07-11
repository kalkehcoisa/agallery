import uuid
import urllib
import re

import boto3
from pyramid.view import view_config
from sqlalchemy.sql.expression import false, true

from agallery.models.gallery import Photo

ACCEPT_FILE_TYPES = re.compile('image/(gif|p?jpeg|(x-)?png)')


class GalleryViews:
    def __init__(self, request):
        self.request = request

    @staticmethod
    def get_file_size(file):
        file.seek(0, 2)  # Seek to the end of the file
        size = file.tell()  # Get the position of EOF
        file.seek(0)  # Reset the file position to the beginning
        return size

    @staticmethod
    def validate(file):
        if file['size'] < 1:
            file['error'] = 'File is too small'
        elif file['size'] > 1048576 * 2:  # megabytes
            file['error'] = 'File is too big'
        elif not ACCEPT_FILE_TYPES.match(file['type']):
            file['error'] = 'Filetype not allowed'
        else:
            return True
        return False

    def save_in_database(self, url):
        p = Photo(
            url=url,
            user_id=self.request.login
        )
        self.request.dbsession.add(p)

    def save_in_s3(self, file_name, fieldStorage):
        # Load required data from the request
        file_type = fieldStorage.type

        # Initialise the S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=self.request.config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.request.config.AWS_SECRET_ACCESS_KEY
        )

        s3.put_object(
            Bucket=self.request.config.S3_BUCKET,
            Key=file_name,
            Body=fieldStorage.value,
            ACL='public-read',
            ContentType=file_type,
            Expires=3600 * 30
        )

        # Return the data to the client
        return 'https://{bucket}.s3.amazonaws.com/{fname}'.format(
            bucket=self.request.config.S3_BUCKET,
            fname=file_name
        )

    @view_config(
        permissions=('login',),
        renderer='agallery:templates/gallery/photos.html',
        request_method='GET',
        route_name='gallery')
    def list_active_photos(self):
        photos = self.request.dbsession.query(Photo) \
            .order_by(Photo.likes_count.desc())
        return {'photos': photos}

    @view_config(
        permissions=('image_send'),
        renderer='json',
        request_method='POST',
        route_name='gallery')
    def post_s3(self):
        results = []
        for name, fieldStorage in self.request.POST.items():
            if type(fieldStorage) is str:
                continue

            result = {}
            result['name'] = '{pre}-{fname}'.format(
                pre=uuid.uuid4(),
                fname=urllib.parse.unquote(fieldStorage.filename)
            )
            result['type'] = fieldStorage.type
            result['size'] = self.get_file_size(fieldStorage.file)
            if self.validate(result):
                key = '{tpe}/{hsh}/{name}'.format(
                    tpe=urllib.parse.quote(result['type'].encode('utf-8'), ''),
                    hsh=str(hash(fieldStorage.value)),
                    name=urllib.parse.quote(result['name'].encode('utf-8'), '')
                )
                if key is not None:
                    result['url'] = self.save_in_s3(result['name'], fieldStorage)
                    self.save_in_database(result['url'])
                    result['deleteUrl'] = result['url']
                    result['deleteType'] = 'DELETE'
                else:
                    result['error'] = 'Failed to store uploaded file.'
            results.append(result)
        return {'files': results}


class GalleryApproveViews:
    def __init__(self, request):
        self.request = request

    @view_config(
        permissions=('image_approve',),
        renderer='agallery:templates/gallery/approve.html',
        request_method='GET',
        route_name='gallery_approve')
    def list_active_photos(self):
        photos = self.request.dbsession.query(Photo).filter(
            Photo.approved == false()
        ).order_by(Photo.likes_count.desc())
        return {'photos': photos}
