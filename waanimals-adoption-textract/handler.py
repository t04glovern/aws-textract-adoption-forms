import boto3
from textract.tableparser import TableParser

def dict_to_item(raw):
    if isinstance(raw, dict):
        return {
            k: dict_to_item(v)
            for k, v in raw.items()
        }
    elif isinstance(raw, list):
        return {
            'L': [dict_to_item(v) for v in raw]
        }
    elif isinstance(raw, str):
        return {'S': raw}
    elif isinstance(raw, int):
        return {'N': str(raw)}


def dynamodb_put(item):
    client = boto3.client(service_name='dynamodb')
    client.put_item(TableName=process.env.ADOPTION_TABLE, Item=item)

def textract(event, context):
    bucketName = event['Records'][0]['s3']['bucket']['name']
    bucketKey = event['Records'][0]['s3']['object']['key']
    table_parser = TableParser(
        bucketName,
        bucketKey
    )
    table_dict = table_parser.get_table_dict_results()

    # Put dictionary into DynamoDB
    dynamodb_put(dict_to_item(table_dict))

    return {
        "item": table_dict,
        "event": event
    }
