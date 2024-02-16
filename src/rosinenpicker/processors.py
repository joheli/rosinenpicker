import fitz
import re

class DocumentProcessor:
    text: str
    matchall_maxlength: int
    result: dict[str, str]
    
    def __init__(self, file_path, matchall_maxlength):
        self.extract_text(file_path = file_path)
        self.matchall_maxlength = matchall_maxlength
    
    def extract_text(self, file_path):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    # function to process the "terms and pattern group" from ConfigStrategy
    def terms_patterns(self, tap: dict[str, tuple[re.Pattern, int, int]]):
        result = {}
        for term, pattern_tpl in tap.items():
            p = pattern_tpl[0]
            mo = re.search(p, self.text)
            content = None
            has_groups = pattern_tpl[1] > 0
            # have patterns been found at all?
            if mo:
                # are groups present?
                if has_groups:
                    matchall_index = pattern_tpl[1]
                    number_of_groups = pattern_tpl[2] # also p.groups
                    content = mo.group(matchall_index)
                    # in case only two groups present: limit length of matched text
                    if len(content) > self.matchall_maxlength and number_of_groups == 2:
                        if matchall_index == 1:
                            content = content[-self.matchall_maxlength:]
                        else:
                            content = content[:self.matchall_maxlength]
                # no groups
                else:
                    # mos: indices of matched text
                    mos = mo.span()
                    content = self.text[mos[0]:mos[1]]
            
            # strip surrounding whitespace and document result
            result[term] = content.strip() if content else content
        # put into class attribute
        self.result = result
        
    def all_found(self) -> bool:
        return not any([n is None for n in self.result])
        
    def terms_content(self, tap) -> dict[str, str]:
        self.terms_patterns(tap)
        return self.result
                
    def contains(self, patternstring: str) -> bool:
        pattern = re.compile(patternstring)
        if pattern.search(self.text):
            return True
        else:
            return False
        
class PDFProcessor(DocumentProcessor):
    def extract_text(self, file_path):
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        self.text = text
        
class TXTProcessor(DocumentProcessor):
    def extract_text(self, file_path):
        with open(file_path, "r") as doc:
            self.text = doc.read()
            

# Placeholder for future extensions
# class MarkdownProcessor(DocumentProcessor):
#     ...
