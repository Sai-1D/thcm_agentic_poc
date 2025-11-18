# src/utils/cache.py

from typing import Optional, List, Dict
from pydantic import BaseModel

class CacheData(BaseModel):
    target: Optional[str] = None
    expected_fields: List[dict] = []
    current_field_index: int = 0
    resume_data: dict = {}

class Cache:
    def __init__(self):
        self.cache: Dict[str, CacheData] = {}
    
    def __getitem__(self, thread_id: str) -> CacheData:
        return self.cache[thread_id]

    def add(self, thread_id: str, interrupt_value: dict):
        fields = interrupt_value.get("fields") or []
        self.cache[thread_id] = CacheData(
            target=interrupt_value.get("target"),
            expected_fields=fields,
            current_field_index=-len(fields) if fields else 0,
            resume_data={},
        )

    def exist(self, thread_id: str) -> bool:
        return thread_id in self.cache

    def get_field(self, thread_id: str):
        cd = self.cache[thread_id]
        return cd.expected_fields[cd.current_field_index]

    def remove(self, thread_id):
        self.cache.pop(thread_id, None)

    def update(self, thread_id, data):
        cd = self.cache[thread_id]
        cur_index = cd.current_field_index
        field_name = cd.expected_fields[cur_index]["name"]
        cd.resume_data[field_name] = data
        cd.current_field_index += 1
