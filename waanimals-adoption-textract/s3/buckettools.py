import boto3
import os


class S3Utils:

    def __init__(self, tmp_dir):
        self.tmp_dir = tmp_dir
        self.s3 = boto3.client('s3')
        self.s3r = boto3.resource('s3')

    def upload_to_s3(self):
        for fileName in os.listdir(self.tmp_dir):
            if fileName.endswith((".png", ".pdf", ".jpg")):
                print("Uploading: " + fileName)  # File name to upload
                self.s3r.meta.client.upload_file(self.tmp_dir + '/' + fileName, os.environ['ADOPTION_FORM_BUCKET'],
                                                 fileName)

    def delete_file(self, key, bucket):
        self.s3.delete_object(Bucket=bucket, Key=key)
        print("{0} deleted fom {1}".format(key, bucket))
