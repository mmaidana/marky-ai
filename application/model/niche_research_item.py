class NicheResearchItem:
    def __init__(self, niche_id, niche_name, niche_description, niche_rank, processed, status, cost_id, created_date, updated_date, updated_by, comments):
        self.niche_id = niche_id
        self.niche_name = niche_name
        self.niche_description = niche_description
        self.niche_rank = niche_rank
        self.processed = processed
        self.status = status
        self.cost_id = cost_id
        self.created_date = created_date
        self.updated_date = updated_date
        self.updated_by = updated_by
        self.comments = comments

    def to_dynamodb_item(self):
        return {
            'niche-id': self.niche_id,
            'niche-name': self.niche_name,
            'niche-description': self.niche_description,
            'niche-rank': str(self.niche_rank),  # DynamoDB uses strings for numbers
            'processed': 'true' if self.processed else 'false',  # DynamoDB does not have a native boolean type; store as string or number
            'status': self.status,
            'cost-id': self.cost_id,
            'created-date': self.created_date,
            'updated-date': self.updated_date,
            'updated-by': self.updated_by,
            'comments': self.comments,
        }