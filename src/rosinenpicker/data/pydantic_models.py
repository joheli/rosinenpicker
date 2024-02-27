from pydantic import BaseModel, DirectoryPath, field_validator, model_validator, NewPath
from rosinenpicker.processing.patterns import Pattern
from typing import Optional

class ConfigError(Exception):
    def __init__(self, msg):
        message_primer = "There appears to be a problem with the values entered:\n"
        self.message = message_primer + msg
        super().__init__(self.message)

class ConfigStrategy(BaseModel):
    processed_directory: DirectoryPath
    move_to_directory: Optional[DirectoryPath] = None
    file_name_pattern: str
    file_content_pattern: Optional[str] = None
    file_format: str
    terms: dict[str, str]
    export_format: str
    export_path: NewPath
    export_csv_divider: Optional[str] = ';'
    # terms_patterns_group is created from 'terms', see @model_validator
    terms_patterns_group: dict[str, Pattern] = None

    @field_validator('file_name_pattern', 'export_format')
    @classmethod
    def non_empty_string(cls, v: str):
        assert v != '', 'Must be a non-empty string'
        return v.strip()

    @field_validator('file_name_pattern', 'file_content_pattern')
    @classmethod
    def selection_must_be_regex(cls, v: str):
        v = v.strip()
        if not Pattern.check_regex(v): 
            raise ConfigError(f"Pattern '{v}' cannot be used as a regex pattern; also, regex groups are not allowed!")
        return v
    
    @field_validator('export_format')
    @classmethod
    def validate_export_format(cls, ef: str):
        valid_formats = {"csv", "html", "json", "xlsx"}
        if ef not in valid_formats:
            raise ConfigError(msg=f"Concerning '{ef}': Export format must conform to one of these options: {valid_formats}!")
        return ef
    
    @field_validator('file_format')
    @classmethod
    def validate_file_format(cls, ff: str):
        valid_formats = {"txt", "pdf", "docx"}
        if ff not in valid_formats:
            raise ConfigError(msg=f"Concerning '{ff}': File format must conform to one of these options: {valid_formats}!")
        return ff
    
    @model_validator(mode='after')
    def check_terms_and_patterns(self):
        # process terms_and_patterns 
        processed_tp = {term:Pattern(patterns_and_options_string=pos) for term, pos in self.terms.items()}
        self.terms_patterns_group = processed_tp
        return self

class Config(BaseModel):
    title: str
    strategies: dict[str, ConfigStrategy]
    