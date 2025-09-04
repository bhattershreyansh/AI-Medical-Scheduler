from pydantic import BaseModel, Field, field_validator
from typing import Optional

class InsuranceInfo(BaseModel):
    """Insurance information with validation"""
    
    primary_carrier: str = Field(..., min_length=2, max_length=100)
    member_id: str = Field(..., min_length=5, max_length=20)
    group_number: str = Field(..., min_length=3, max_length=15)
    
    secondary_carrier: Optional[str] = Field(None, max_length=100)
    secondary_member_id: Optional[str] = None
    secondary_group_number: Optional[str] = None
    
    @field_validator('member_id', 'secondary_member_id')
    def validate_member_id(cls, v):
        if v is None:
            return v
        clean_id = v.replace(' ', '').replace('-', '')
        if not clean_id.isalnum():
            raise ValueError('Member ID must contain only letters and numbers')
        return clean_id
    
    @field_validator('group_number', 'secondary_group_number')
    def validate_group_number(cls, v):
        if v is None:
            return v
        clean_group = v.replace(' ', '').replace('-', '')
        if not clean_group.isalnum():
            raise ValueError('Group number must contain only letters and numbers')
        return clean_group
    
    class Config:
        str_strip_whitespace = True
