import boto3
import os


class DbUtils:

    def put(self, raw):
        item = self.dict_to_item(raw)
        client = boto3.client(service_name='dynamodb')
        client.put_item(TableName=os.environ['ADOPTION_FORM_TABLE'], Item=item)

    def dict_to_item(self, raw):
        if isinstance(raw, dict):
            return {
                k: self.dict_to_item(v)
                for k, v in raw.items()
            }
        elif isinstance(raw, list):
            return {
                'L': [self.dict_to_item(v) for v in raw]
            }
        elif isinstance(raw, str):
            return {'S': raw}
        elif isinstance(raw, int):
            return {'N': str(raw)}
