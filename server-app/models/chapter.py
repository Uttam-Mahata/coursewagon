# models/chapter.py
from extensions import db


class Chapter(db.Model):
    __tablename__ = 'chapters'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    
    def __init__(self, module_id, name):
        self.module_id = module_id
        self.name = name
    
    def to_dict(self):
        return {
            'id': self.id,
            'module_id': self.module_id,
            'name': self.name
        }