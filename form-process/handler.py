import boto3
import os
import email
import uuid
from textract.tableparser import TableParser
from dynamodb.dbtools import DbUtils
from s3.buckettools import S3Utils

tmpDir = "/tmp/output/"


def textract(event, context):
    bucketName = event['Records'][0]['s3']['bucket']['name']
    bucketKey = event['Records'][0]['s3']['object']['key']

    # Textract process to dictionary of items
    table_parser = TableParser(
        bucketName,
        bucketKey
    )
    table_dict = table_parser.get_table_dict_results()

    if len(table_dict) > 0:
        # Put dictionary into DynamoDB
        db_utils = DbUtils()
        db_utils.put(raw=table_dict)

    return {
        "item": table_dict,
        "event": event
    }


def ses(event, context):
    bucketName = event['Records'][0]['s3']['bucket']['name']
    bucketKey = event['Records'][0]['s3']['object']['key']

    s3 = boto3.client('s3')
    s3r = boto3.resource('s3')

    s3_utils = S3Utils(tmpDir)

    try:
        # Use waiter to ensure the file is persisted
        waiter = s3.get_waiter('object_exists')
        waiter.wait(Bucket=bucketName, Key=bucketKey)

        response = s3r.Bucket(bucketName).Object(bucketKey)

        # Read the raw byte file into a Email Object
        msg = email.message_from_bytes(response.get()["Body"].read())

        if len(msg.get_payload()) == 2:

            # Create directory for the files (makes debugging easier)
            if os.path.isdir(tmpDir) == False:
                os.mkdir(tmpDir)

            # The first attachment
            attachment = msg.get_payload()[1]

            # Save the attachment to local fs
            extract_attachment(attachment)

            # Upload the files to S3
            s3_utils.upload_to_s3()

        else:
            print("Could not see file/attachment.")
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist '
              'and your bucket is in the same region as this '
              'function.'.format(bucketKey, bucketName))
        raise e
    s3_utils.delete_file(bucketKey, bucketName)


def extract_attachment(attachment):
    if "png" in attachment.get_content_type():
        open(tmpDir + str(uuid.uuid4()) + '.png', 'wb').write(attachment.get_payload(decode=True))
    elif "jpg" in attachment.get_content_type():
        open(tmpDir + str(uuid.uuid4()) + '.jpg', 'wb').write(attachment.get_payload(decode=True))
    elif "pdf" in attachment.get_content_type():
        fileName = tmpDir + str(uuid.uuid4())
        open(fileName + '.pdf', 'wb').write(attachment.get_payload(decode=True))
        os.system('convert -density 300 -background white -alpha background -alpha off %s %s' % (fileName + '.pdf', fileName + '.png'))
        os.remove(fileName + '.pdf')
    else:
        print('Skipping ' + attachment.get_content_type())
