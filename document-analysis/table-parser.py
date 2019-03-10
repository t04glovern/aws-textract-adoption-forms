import boto3
from textract.tableparser import TableParser

table = "devopstar-adoption-dynamodb-DynamoDBTable-12N6PRXMMZWSL"
bucket = "devopstar"
document = "resources/aws-textract-adoption-forms/demo-docs/adoption-agreement.png"


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
    client.put_item(TableName=table, Item=item)


# Parse document from S3 bucket to Dictionary
table_parser = TableParser(bucket, document)
table_dict = table_parser.get_table_dict_results()

# Put dictionary into DynamoDB
dynamodb_put(dict_to_item(table_dict))
