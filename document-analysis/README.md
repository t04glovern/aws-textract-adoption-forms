# Document Analysis

## Deploy Dummy DynamoDB

```bash
aws cloudformation create-stack \
    --stack-name "devopstar-adoption-dynamodb" \
    --template-body file://cloudformation/dynamodb.yaml \
    --parameters file://cloudformation/dynamodb-params.json
```

Update the three fields in table-parser.py

```python
table = "<table_name>"
bucket = "devopstar"
document = "resources/aws-textract-adoption-forms/demo-docs/adoption-agreement.png"
```

## Setup

```bash
python3 -m venv ./venv
source venv/bin/activate
python table-parser.py
```
