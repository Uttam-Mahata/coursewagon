# repositories/module_repo.py
from models.module import Module
from extensions import db

class ModuleRepository:
    def __init__(self):
        self.db = db
    
    def add_module(self, module):
        self.db.session.add(module)
        self.db.session.commit()
    
    def get_modules_by_subject_id(self, subject_id):
        return self.db.session.query(Module).filter(Module.subject_id == subject_id).all()
    
    def get_module_by_id(self, module_id):
        return self.db.session.query(Module).filter(Module.id == module_id).first()