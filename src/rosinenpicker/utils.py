import hashlib
import re

class PatternStringError(Exception):
    def __init__(self, msg):
        message_primer = "There appears to be a problem with the patterstring:\n"
        self.message = message_primer + msg
        super().__init__(self.message)

def file_sha256(file_name: str) -> str:
    with open(file_name, "rb") as f:
        bytes = f.read()
        hex_hash = hashlib.sha256(bytes).hexdigest()
        return hex_hash
    
def check_regex(patternstring: str) -> bool:
    try: 
        rgx = re.compile(patternstring)
        # Also, do not allow regex groups
        if rgx.groups > 0:
            return False
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
def process_terms(patternstring: str, divider: str = "@@@", rflag: re.RegexFlag = re.NOFLAG) -> tuple[re.Pattern, int, int]:
    # if patternstrings contains groups, reject
    if not check_regex(patternstring):
        raise PatternStringError(f"Concerning '{patternstring}': cannot be used as regex pattern; also, regex groups are not allowed!")
    # helper to check if pattern only consists of a matchall pattern
    def matchall_only(s) -> bool:
        return re.search("\.\*", s) and len(s) == 2
    # check if matchall pattern is present (as this is not allowed)
    if matchall_only(patternstring):
        raise PatternStringError(msg=f"The string '{patternstring}' only contains the matchall-pattern '.*' and can therefore not be processed.")
    # divider_hits counts the number of divider in the string; only one is allowed (see below)
    divider_hits = len(re.findall(divider, patternstring))
    # check the number of occurrences of divider
    if divider_hits > 1:
        # as this is not implemented, throw an error
        raise PatternStringError(msg=f"Each term must correspond to either *one regex pattern* or *two regex patterns divided by '{divider}'*!")
    if divider_hits == 0:
        # return without capture groups
        return (re.compile(patternstring, rflag), -1, -1)
    # process the patternstrings divided by divider
    multiple_patternstrings = re.split(divider, patternstring)
    
    # check if patternstring and multiple_patternstrings are valid regex patterns without groups
    all_strings = multiple_patternstrings.copy()
    all_strings.append(patternstring)
    all_check = [check_regex(s) for s in all_strings]
    if not all(all_check):
        raise PatternStringError(f"Concerning one of '{all_strings!r}': cannot be used as regex pattern; also regex groups are not allowed!")
    
    # do any of the patternstrings only contain a matchall pattern?
    if any([matchall_only(p) for p in multiple_patternstrings]):
        raise PatternStringError(msg=f"At least one of '{multiple_patternstrings!r}' only consists of a matchall-pattern '.*' and can therefore not be processed.")
    # is any of the patternstrings of length 0?
    lenx = [len(i) for i in multiple_patternstrings]
    lenx0 = [l == 0 for l in lenx]
    # if yes
    if any(lenx0):
        # the first?
        if lenx0[0]:
            return (re.compile(f"(.*)({multiple_patternstrings[1]})", rflag), 1, 2)
        # the second?
        return (re.compile(f"({multiple_patternstrings[0]})(.*)", rflag), 2, 2)
    # none of the patternstrings empty? return three groups
    return (re.compile(f"({multiple_patternstrings[0]})(.*)({multiple_patternstrings[1]})", rflag), 2, 3)