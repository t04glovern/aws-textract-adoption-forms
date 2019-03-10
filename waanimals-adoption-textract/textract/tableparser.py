import boto3


class TableParser:

    def __init__(self, bucket, document):
        self.bucket = bucket
        self.document = document

    def get_rows_columns_map(self, table_result, blocks_map):
        rows = {}
        for relationship in table_result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    cell = blocks_map[child_id]
                    if cell['BlockType'] == 'CELL':
                        row_index = cell['RowIndex']
                        col_index = cell['ColumnIndex']
                        if row_index not in rows:
                            # create new row
                            rows[row_index] = {}

                        # get the text value
                        rows[row_index][col_index] = self.get_text(cell, blocks_map)
        return rows

    def get_text(self, result, blocks_map):
        text = ''
        if 'Relationships' in result:
            for relationship in result['Relationships']:
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        word = blocks_map[child_id]
                        if word['BlockType'] == 'WORD':
                            text += word['Text'] + ' '
        return text

    def get_table_dict_results(self):
        # Analyze the document from S3
        client = boto3.client(service_name='textract')
        response = client.analyze_document(Document={'S3Object': {'Bucket': self.bucket, 'Name': self.document}},
                                           FeatureTypes=["TABLES"])

        # Get the text blocks
        blocks = response['Blocks']

        blocks_map = {}
        table_blocks = []
        for block in blocks:
            blocks_map[block['Id']] = block
            if block['BlockType'] == "TABLE":
                table_blocks.append(block)

        if len(table_blocks) <= 0:
            return {}

        cells = {}
        for index, table in enumerate(table_blocks):
            cells = self.generate_table_dict(table, blocks_map, cells)

        return cells

    def generate_table_dict(self, table_result, blocks_map, cells):
        rows = self.get_rows_columns_map(table_result, blocks_map)

        for row_index, cols in rows.items():
            cells[cols[1].rstrip()] = cols[2].rstrip()

        return cells
