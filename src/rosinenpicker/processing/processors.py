from pdfminer.high_level import extract_text
from docx import Document
import re
from rosinenpicker.processing.patterns import Pattern

class DocumentProcessor:
    text: str
    result: dict[str, str]
    result_required: dict[str, str]
    
    def __init__(self, file_path):
        self.extract_text(file_path = file_path)
    
    def extract_text(self, file_path):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    # function to process the "terms and pattern group" from ConfigStrategy
    def terms_patterns(self, tap: dict[str, Pattern]):
        result = {}
        result_required = {}
        for term, p in tap.items():
            mo = re.search(p.compiled_regex_pattern, self.text)
            content = None
            has_groups = p.compiled_regex_pattern.groups > 0
            # have patterns been found at all?
            if mo:
                # are groups present?
                if has_groups:
                    #goi = p.group_of_interest
                    #number_of_groups = p.compiled_regex_pattern.groups 
                    content = mo.group(p.group_of_interest)
                    # # in case only two groups present: limit length of matched text
                    # if p.pattern_options.cropToLength:
                    #     if len(content) > p.pattern_options.cropToLength and number_of_groups == 2:
                    #         if goi == 1:
                    #             content = content[-p.pattern_options.cropToLength:]
                    #         else:
                    #             content = content[:p.pattern_options.cropToLength]
                # no groups
                else:
                    # mos: indices of matched text
                    mos = mo.span()
                    content = self.text[mos[0]:mos[1]]
            
            # further process content
            # linebreak to space
            if content and p.pattern_options.lineBreakToSpace:
                content = re.sub("\n", " ", content)
                
            # cropToLength
            if content and p.pattern_options.cropToLength:
                ctl = p.pattern_options.cropToLength + 1 # adding 1 makes sure the length of cropped string equals cropToLength
                #print(f"pattern: {p.compiled_regex_pattern}, content: {content}, ctl: {ctl}, groups: {p.compiled_regex_pattern.groups}, goi: {p.group_of_interest}\n")
                if len(content) > ctl:
                    if p.compiled_regex_pattern.groups == 2 and p.group_of_interest == 1:
                        content = content[-ctl:]
                    else:
                        content = content[:ctl]
            
            # strip
            if content:
                content = content.strip()
                
            # result required
            if p.pattern_options.required:
                # print(f"\nGoing into required - Pattern: {p}\n")
                # print(f"content: {content!r}\n")
                result_required[term] = content
            
            # document result
            #print(f"\nGoing into all: {p}\n")
            result[term] = content
        # put into class attribute
        self.result = result
        self.result_required = result_required
        
        # # Finally 
        # print(f"all results: {self.result!r}\n")
        # print(f"required: {self.result_required!r}\n")
        # na_required = any([n is None for n in self.result_required.values()])
        # na_all = any([n is None for n in self.result.values()])
        # print(f"none in required: {na_required}, none in all: {na_all}\n")
        
    def all_found(self) -> bool:
        return not any([n is None for n in self.result_required.values()])
        
    def terms_content(self, tap) -> dict[str, str]:
        self.terms_patterns(tap)
        return self.result
                
    def contains(self, text_: str) -> bool:
        pattern = re.compile(text_)
        if pattern.search(self.text):
            return True
        else:
            return False
        
class PDFProcessor(DocumentProcessor):
    def extract_text(self, file_path):
        self.text = extract_text(file_path)
        
class TXTProcessor(DocumentProcessor):
    def extract_text(self, file_path):
        with open(file_path, "r") as doc:
            self.text = doc.read()

class DOCXProcessor(DocumentProcessor):
    def extract_text(self, file_path):
        d = Document(file_path)
        txt = ''
        for p in d.paragraphs:
            txt = txt + '\n' + p.text
        self.text = txt
        

# Placeholder for future extensions
# class MarkdownProcessor(DocumentProcessor):
#     ...
