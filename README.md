# Textract Adoption Form

Consuming and processing WA Animals adoption forms using AWS Textract and placing that data in DynamoDB

## Setup

Copy over the demo documents we'll be using throughout this tutorial

```bash
aws s3 sync docs/ s3://devopstar/resources/aws-textract-adoption-forms/demo-docs
```

## Serverless Setup

```bash
## Project Setup
mkdir waanimals-adoption-textract
cd waanimals-adoption-textract
serverless create --template aws-python3 --name waanimals-adoption-textract
```

### Update serverless.yml

```yaml
service: waanimals-adoption-textract

custom:
  PRIMARY_KEY: "Microchip Number"
  ADOPTION_BUCKET: "waanimals-adoption-forms"

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
        - arn:aws:dynamodb:${opt:region, self:provider.region}:*:table/${self:provider.environment.ADOPTION_TABLE}
    - Effect: Allow
      Action:
        - textract:AnalyzeDocument
      Resource: "*"
  environment:
    ADOPTION_TABLE: "waanimals-adoption-forms"

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
      Type: "AWS::DynamoDB::Table"
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
```
