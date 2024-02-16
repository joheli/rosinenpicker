import pandas as pd

class BaseExporter:
    dataframe: pd.DataFrame
    export_path: str = None
    
    def __init__(self, dataframe: pd.DataFrame) -> None:
        self.dataframe = dataframe
        
    def export(self, export_path: str) -> None:
        raise NotImplementedError("This method should be implemented by subclasses.")
    
class CSVExporter(BaseExporter):
    _separator: str = ";"
    
    @property
    def separator(self) -> str:
        return self._separator
    
    @separator.setter
    def separator(self, newsep = str) -> None:
        self._separator = newsep
    
    def export(self, export_path: str) -> None:
        self.export_path = export_path
        self.dataframe.to_csv(export_path, sep = self.separator)
        
class XLSXExporter(BaseExporter):
    def export(self, export_path: str) -> None:
        self.export_path = export_path
        self.dataframe.to_excel(export_path)
        
class HTMLExporter(BaseExporter):
    def export(self, export_path: str) -> None:
        self.export_path = export_path
        self.dataframe.to_html(export_path, )
        
class JSONExporter(BaseExporter):
    def export(self, export_path: str) -> None:
        self.export_path = export_path
        self.dataframe.to_json(export_path, orient = 'table')
