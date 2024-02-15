__version__ = '0.0.4'
import yaml
import re
import os
from .pydantic_models import Config, ConfigStrategy, ConfigError
from .database import Base, DbRun, DbStrategy, DbProcessedFile, DbMatch
from .utils import file_sha256
from .processors import DocumentProcessor, PDFProcessor, TXTProcessor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import argparse

def read_config_file(config_file: str) -> Config:
    try:
        with open(config_file, "r") as f:
            cfg_raw = yaml.safe_load(f)
        cfg = Config(**cfg_raw)
        return cfg
    except Exception as e:
        print(f"{e}")
        
def find_documents(directory, file_name_pattern) -> list[str]:
    pattern = re.compile(file_name_pattern)
    return [os.path.join(directory, f) for f in os.listdir(directory) if pattern.match(f)]

def process_strategy(strategy_name: str, cs: ConfigStrategy, session: Session, run_id: int, 
                     processor: DocumentProcessor):
    # save strategy info
    d_strategy = DbStrategy(run_id = run_id,
                            name = strategy_name,
                            processed_directory = str(cs.processed_directory),
                            file_name_pattern = cs.file_name_pattern,
                            file_content_pattern = cs.file_content_pattern,
                            export_format = cs.export_format,
                            export_path = str(cs.export_path),
                            export_csv_divider = cs.export_csv_divider)
    session.add(d_strategy)
    session.commit()
    
    # loop thru files
    documents = find_documents(cs.processed_directory, cs.file_name_pattern)
    if len(documents) < 1:
        raise ConfigError(f"No matching documents found with pattern {cs.file_name_pattern} in directory {cs.processed_directory}!")
    
    for doc in documents:
        pr = processor(doc, cs.matchall_maxlength)
        # if file_content_pattern is given and if that pattern is not found in the document, skip the document
        if cs.file_content_pattern:
            if not pr.contains(cs.file_content_pattern):
                # skip to next document without any further ado
                continue
        # save file info
        d_file = DbProcessedFile(strategy_id = d_strategy.id,
                                 filename = os.path.basename(doc),
                                 sha256 = file_sha256(doc))
        session.add(d_file)
        session.commit()
        
        # get content from file
        terms_content = pr.terms_content(cs.terms_patterns_group)
        
        # save content into database
        for term, content in terms_content.items():
            dm = DbMatch(file_id = d_file.id, term = term, content = content)
            session.add(dm)
            session.commit()
    
def main(config_file: str, db_file: str):
    config = read_config_file(config_file)
    engine = create_engine(f'sqlite:///{db_file}')
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # processor options according to file_format
    file_format_options = {"pdf": PDFProcessor, "txt": TXTProcessor}
    
    # save run info
    run = DbRun(title = config.title,
              yml_filename = config_file,
              yml_sha256 = file_sha256(config_file))
    session.add(run)
    session.commit()
    
    for strategy_name, strategy in config.strategies.items():
        # processor is chosen according to strategy.file_format
        processor = file_format_options[strategy.file_format]
        # process using correct processor
        process_strategy(strategy_name, strategy, session, run.id, processor)

    session.close()
    
def cli():
    parser = argparse.ArgumentParser(description="A package for picking the juciest text morsels out of a pile of documents.")
    parser.add_argument('-c', '--config', default='config.yml', help='Path to configuration YAML file.')
    parser.add_argument('-d', '--database', default='matches.db', help='Path to SQLite database file.')
    parser.add_argument('-v', '--version', help = "Print version and exit.", action="store_true")
    args = parser.parse_args()
    
    # version?
    if args.version:
        print(f"{__version__}")
        exit(0)
    
    # check if config exists!
    if not os.path.isfile(args.config):
        print("No configuration file provided! Please add one using -c! Apply -h for help.\n")
        parser.print_help()
        exit(1)

    main(args.config, args.database)
    
if __name__ == "__main__":
    cli()
    
    