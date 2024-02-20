import re
from typing import Any
from pydantic_core import CoreSchema, core_schema
from pydantic import GetCoreSchemaHandler

class PatternOptionsError(Exception):
    def __init__(self, msg):
        message_primer = "There appears to be a problem with the pattern options specified:"
        self.message = message_primer + msg
        super().__init__(self.message)
        
class PatternStringError(Exception):
    def __init__(self, msg):
        message_primer = "There appears to be a problem with the patterstring:\n"
        self.message = message_primer + msg
        super().__init__(self.message)

class PatternOptions:
    multiLine: bool = False
    cropToLength: int = None
    lineBreakToSpace: bool = False
    required: bool = True
    
    def __init__(self, optionstring: str):
        self.process_optionstring(optionstring)
    
    def process_optionstring(self, ops: str):
        # cropToLength specified?
        cropToLengthFinds = re.findall("c\(\d+\)", ops)
        if len(cropToLengthFinds) > 0:
            # extract number, only take first, no matter what
            numberString = re.findall("\d+", cropToLengthFinds[0])
            if len(numberString) > 0:
                try:
                    self.cropToLength = int(numberString[0])
                except:
                    pass
        # multiline specified?
        multilineFinds = re.findall("m", ops)
        if len(multilineFinds) > 0:
            self.multiLine = True
        # lineBreakToSpace specified?
        lineBreakToSpaceFinds = re.findall("l", ops)
        if len(lineBreakToSpaceFinds) > 0:
            self.lineBreakToSpace = True
        # not required specified?
        notRequiredFinds = re.findall("\?", ops)
        if len(notRequiredFinds) > 0:
            self.required = False
            
    def __repr__(self):
        return f"PatternOptions(cropToLength:{self.cropToLength}, multiLine:{self.multiLine}, lineBreakToSpace:{self.lineBreakToSpace}, required:{self.required})"

class Pattern:
    compiled_regex_pattern: re.Pattern = None
    pattern_options: PatternOptions = None
    patterns_and_options_string: str = None
    pattern_string: str = None
    options_string: str =  None
    pattern_divider: str = "@@@"
    options_divider: str = "==="
    group_of_interest: int = None
    
    def __repr__(self):
        return f"Pattern(compiled_regex_pattern:{self.compiled_regex_pattern},\
                pattern_options:{self.pattern_options},\
                patterns_and_options_string:{self.patterns_and_options_string},\
                options_string:{self.options_string},\
                group_of_interest:{self.group_of_interest})"
    
    # the following class method is necessary for pydantic to use this class as a type.
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))
    
    def __init__(self, patterns_and_options_string: str):
        self.patterns_and_options_string = patterns_and_options_string
        self.process_options()
        self.process_terms()
    
    # basic validation
    @classmethod
    def check_regex(cls, ps: str) -> bool:
        try: 
            rgx = re.compile(ps)
            # Also, do not allow regex groups
            if rgx.groups > 0:
                return False
        except:
            return False
        return True
    
    # helper to check if pattern only consists of a matchall pattern
    def matchall_only(self, s) -> bool:
        return re.search("\.\*", s) and len(s) == 2
    
    # extract options
    def process_options(self):
        # check number of dividers
        divider_hits = len(re.findall(self.options_divider, self.patterns_and_options_string))
        # check the number of occurrences of divider
        if divider_hits > 1:
            # as this is not implemented, throw an error
            raise PatternStringError(msg=f"Multiple option groups detected in '{self.patterns_and_options_string}'! Only one allowed!")
        # if no options present, set default options!
        if divider_hits == 0:
            self.pattern_options = PatternOptions("")
            self.pattern_string = self.patterns_and_options_string
            return
        # if options present, create new PatternOptions object
        options_split = re.split(self.options_divider, self.patterns_and_options_string)
        self.pattern_string = options_split[0]
        self.pattern_options = PatternOptions(options_split[1])
        
    # process_terms
    def process_terms(self):
        # extract rflag
        rflag = re.DOTALL if self.pattern_options.multiLine else re.NOFLAG
        # if patternstrings contains groups, reject
        if not self.check_regex(self.pattern_string):
            raise PatternStringError(f"Concerning '{self.pattern_string}': cannot be used as regex pattern; also, regex groups are not allowed!")
        # check if matchall pattern is present (as this is not allowed)
        if self.matchall_only(self.pattern_string):
            raise PatternStringError(msg=f"The string '{self.pattern_string}' only contains the matchall-pattern '.*' and can therefore not be processed.")
        # divider_hits counts the number of divider in the string; only one is allowed (see below)
        divider_hits = len(re.findall(self.pattern_divider, self.pattern_string))
        # check the number of occurrences of divider
        if divider_hits > 1:
            # as this is not implemented, throw an error
            raise PatternStringError(msg=f"Each term must correspond to either *one regex pattern* or *two regex patterns divided by '{divider}'*!")
        if divider_hits == 0:
            # return without capture groups
            self.compiled_regex_pattern = re.compile(self.pattern_string, rflag)
            return
            # return (re.compile(patternstring, rflag), -1, -1)
        # process the patternstrings divided by divider
        multiple_patternstrings = re.split(self.pattern_divider, self.pattern_string)
        
        # check if patternstring and multiple_patternstrings are valid regex patterns without groups
        all_strings = multiple_patternstrings.copy()
        all_strings.append(self.pattern_string)
        all_check = [self.check_regex(s) for s in all_strings]
        if not all(all_check):
            raise PatternStringError(f"Concerning one of '{all_strings!r}': cannot be used as regex pattern; also regex groups are not allowed!")
        
        # do any of the patternstrings only contain a matchall pattern?
        if any([self.matchall_only(p) for p in multiple_patternstrings]):
            raise PatternStringError(msg=f"At least one of '{multiple_patternstrings!r}' only consists of a matchall-pattern '.*' and can therefore not be processed.")
        # is any of the patternstrings of length 0? (This occurs if the matchall-pattern not surrounded by two patterns)
        lenx = [len(i) for i in multiple_patternstrings]
        lenx0 = [l == 0 for l in lenx]
        #print(f"multiple patternstrings: {multiple_patternstrings}, lenx: {lenx}, lenx0: {lenx0}\n")
        # if yes, create two groups
        if any(lenx0):
            # the first group is of interest
            if lenx0[0]:
                ps = multiple_patternstrings[1]
                self.compiled_regex_pattern = re.compile(f"(.*)({ps})", rflag)
                #print(f"ps: {ps}, rgx: {self.compiled_regex_pattern}\n")
                self.group_of_interest = 1
                # return (re.compile(f"(.*)({multiple_patternstrings[1]})", rflag), 1, 2)
            else:
            # the second group is of interest
                ps = multiple_patternstrings[0]
                self.compiled_regex_pattern = re.compile(f"({ps})(.*)", rflag)
                #print(f"ps: {ps}, rgx: {self.compiled_regex_pattern}\n")
                self.group_of_interest = 2
                # return (re.compile(f"({multiple_patternstrings[0]})(.*)", rflag), 2, 2)
        else:
            # none of the patternstrings empty? return three groups
            self.compiled_regex_pattern = re.compile(f"({multiple_patternstrings[0]})(.*)({multiple_patternstrings[1]})", rflag)
            self.group_of_interest = 2
            #return (re.compile(f"({multiple_patternstrings[0]})(.*)({multiple_patternstrings[1]})", rflag), 2, 3)
        
    