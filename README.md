# Textract Adoption Form

Consuming and processing WA Animals adoption forms using AWS Textract and placing that data in DynamoDB

## Serverless Setup

```bash
## Project Setup
mkdir waanimals-adoption-textract
cd waanimals-adoption-textract
serverless create --template aws-python3 --name waanimals-adoption-textract
```

### Requirements [Workaround]

Currently the boto3 client deployed to Lambda doesn't include textract. We'll need to force an update on the client using python requirements

```bash
serverless plugin install -n serverless-python-requirements
```

Create a `requirements.txt` file and add the following to it

```bash
boto3>=1.9.111
```

Also in the next section take careful note of the lines below

```bash
pythonRequirements:
  dockerizePip: non-linux
  noDeploy: []
```

`noDeploy` tells the `serverless-python-requirements` plugin to include boto3 and not omit it. More information can be found [HERE](https://github.com/UnitedIncome/serverless-python-requirements#omitting-packages)

### Update serverless.yml

```yaml
service: waanimals-adoption-textract

custom:
  pythonRequirements:
    dockerizePip: non-linux
    noDeploy: []
  PRIMARY_KEY: Microchip Number
  ADOPTION_BUCKET: waanimals-adoption-forms

provider:
  name: aws
  runtime: python3.7
  iamRoleStatements:
    - Effect: Allow
      Action:
        - dynamodb:PutItem
      Resource:
        - { "Fn::GetAtt": ["AdoptionDynamoDBTable", "Arn"] }
    - Effect: Allow
      Action:
        - s3:GetObject
      Resource:
        - arn:aws:s3:::${self:custom.ADOPTION_BUCKET}/*
    - Effect: Allow
      Action:
        - textract:AnalyzeDocument
      Resource: "*"
  environment:
    ADOPTION_TABLE: waanimals-adoption-forms

functions:
  textract:
    handler: handler.textract
    events:
      - s3:
          bucket: ${self:custom.ADOPTION_BUCKET}
          event: s3:ObjectCreated:*

resources:
  Resources:
    AdoptionDynamoDBTable:
      Type: AWS::DynamoDB::Table
      Properties:
        AttributeDefinitions:
          - AttributeName: ${self:custom.PRIMARY_KEY}
            AttributeType: S
        KeySchema:
          - AttributeName: ${self:custom.PRIMARY_KEY}
            KeyType: HASH
        ProvisionedThroughput:
          ReadCapacityUnits: 1
          WriteCapacityUnits: 1
        TableName: ${self:provider.environment.ADOPTION_TABLE}

plugins:
  - serverless-python-requirements
```

### Test

Upload an example to the new bucket created by your serverless package

```bash
aws s3 cp docs/adoption-agreement.png s3://waanimals-adoption-forms/adoption-agreement.png
```
