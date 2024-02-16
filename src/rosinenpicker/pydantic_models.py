from pydantic import BaseModel, DirectoryPath, field_validator, model_validator, NewPath
from typing import Optional
import re

class ConfigError(Exception):
    def __init__(self, msg):
        message_primer = "There appears to be a problem with the values entered:\n"
        self.message = message_primer + msg
        super().__init__(self.message)

class ConfigStrategy(BaseModel):
    processed_directory: DirectoryPath
    file_name_pattern: str
    file_content_pattern: Optional[str] = None
    file_format: str
    terms: dict[str, str]
    export_format: str
    export_path: NewPath
    export_csv_divider: Optional[str] = ';'
    # terms_patterns_group is created from 'terms', see @model_validator
    terms_patterns_group: dict[str, tuple[re.Pattern, int, int]] = None
    matchall_maxlength: int = 100

    @field_validator('file_name_pattern', 'export_format')
    @classmethod
    def non_empty_string(cls, v: str):
        assert v != '', 'Must be a non-empty string'
        return v.strip()
    
    @classmethod
    def compile_regex(cls, p: str) -> re.Pattern:
        try:
            rgx = re.compile(p)
            return rgx
        except:
            raise ConfigError(f"Concerning pattern {p}: this string cannot be used as a regex pattern!")

    @field_validator('file_name_pattern', 'file_content_pattern')
    @classmethod
    def selection_must_be_regex(cls, v: str):
        v = v.strip()
        cls.compile_regex(v) # if unsuccessful an error is thrown
        return v

    @model_validator(mode='after')
    def check_terms_and_patterns(self):
        # process terms_and_patterns 
        processed_tp = {term:self.process_terms(pattern) for term, pattern in self.terms.items()}
        self.terms_patterns_group = processed_tp
        return self
    
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
        valid_formats = {"txt", "pdf"}
        if ff not in valid_formats:
            raise ConfigError(msg=f"Concerning '{ff}': File format must conform to one of these options: {valid_formats}!")
        return ff
    
    @classmethod
    def is_regex(cls, patternstring: str) -> bool:
        #breakpoint()
        try: 
            re.compile(patternstring)
        except:
            return False
        return True
    
    # process_terms
    # This function has the following jobs:
    #   - check if patternstrings can be converted to regex patterns (type re.Pattern)
    #   - check if patternstrings already contain a "matchall pattern" (.*), as these are not allowed 
    #   - create capture groups if divider is present; if present:
    #       - check if divider occurs more than once, as this is not allowed
    #       - replace the divider by a capture group matching all ("matchall pattern")
    #       - return the index of the (one and only) capture group representing the matchall pattern
    #       - return the total number of capture groups
    # Return value:
    #   The function returns a tuple of (re.Pattern, int, int) containing the compiled pattern,
    #   the index of the group containing the (one and only) matchall pattern, and
    #   the number of capture groups present.
    #   In case no capture groups have been formed, the second and third integers are set to -1.
    def process_terms(cls, patternstring: str, divider: str = "@@@") -> tuple[re.Pattern, int, int]:
        # helper to check if pattern only consists of a matchall pattern
        def matchall_only(s) -> bool:
            return re.search("\.\*", s) and len(s) == 2
        # check if matchall pattern is present (as this is not allowed)
        if matchall_only(patternstring):
            raise ConfigError(msg=f"The string '{patternstring}' only contains the matchall-pattern '.*' and can therefore not be processed.")
        # divider_hits counts the number of divider in the string; only one is allowed (see below)
        divider_hits = len(re.findall(divider, patternstring))
        # check the number of occurrences of divider
        if divider_hits > 1:
            # as this is not implemented, throw an error
            raise ConfigError(msg=f"Each term must correspond to either *one regex pattern* or *two regex patterns divided by '{divider}'*!")
        if divider_hits == 0:
            # return without capture groups
            return (cls.compile_regex(patternstring), -1, -1)
        # process the patternstrings divided by divider
        multiple_patternstrings = re.split(divider, patternstring)
        # do any of the patternstrings only contain a matchall pattern?
        if any([matchall_only(p) for p in multiple_patternstrings]):
            raise ConfigError(msg=f"At least one of {multiple_patternstrings!r} only consists of a matchall-pattern '.*' and can therefore not be processed.")
        # is any of the patternstrings of length 0?
        lenx = [len(i) for i in multiple_patternstrings]
        lenx0 = [l == 0 for l in lenx]
        # if yes
        if any(lenx0):
            # the first?
            if lenx0[0]:
                return (cls.compile_regex(f"(.*)({multiple_patternstrings[1]})"), 1, 2)
            # the second?
            return (cls.compile_regex(f"({multiple_patternstrings[0]})(.*)"), 2, 2)
        # none of the patternstrings empty? return three groups
        return (cls.compile_regex(f"({multiple_patternstrings[0]})(.*)({multiple_patternstrings[1]})"), 2, 3)

class Config(BaseModel):
    title: str
    strategies: dict[str, ConfigStrategy]
    