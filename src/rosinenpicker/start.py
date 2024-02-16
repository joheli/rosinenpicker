__version__ = '0.1.4'
import yaml
import re
import os
import shutil as sh
import pathlib as pl
import pandas as pd
from .pydantic_models import Config, ConfigStrategy, ConfigError
from .database import Base, DbRun, DbStrategy, DbProcessedFile, DbMatch
from .utils import file_sha256
from .exporter import BaseExporter, CSVExporter, XLSXExporter, HTMLExporter, JSONExporter
from .processors import DocumentProcessor, PDFProcessor, TXTProcessor
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
import argparse

# File format
# processor and exporter options according to file_format and export_format
file_format_options = {"pdf": PDFProcessor, "txt": TXTProcessor}
export_format_options = {"csv": CSVExporter, "xlsx": XLSXExporter, "html": HTMLExporter, "json": JSONExporter}

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

def process_strategy(strategy_name: str, cs: ConfigStrategy, db: Session, run_id: int, 
                     processor: DocumentProcessor, exporter: BaseExporter):
    # save strategy info
    d_strategy = DbStrategy(run_id = run_id,
                            name = strategy_name,
                            processed_directory = str(cs.processed_directory),
                            file_name_pattern = cs.file_name_pattern,
                            file_content_pattern = cs.file_content_pattern,
                            export_format = cs.export_format,
                            export_path = str(cs.export_path),
                            export_csv_divider = cs.export_csv_divider)
    db.add(d_strategy)
    db.commit()
    
    # locate files (documents)
    documents = find_documents(cs.processed_directory, cs.file_name_pattern)
    if len(documents) < 1:
        raise ConfigError(f"No matching documents found with pattern {cs.file_name_pattern} in directory {cs.processed_directory}!")
    
    # loop thru documents
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
        db.add(d_file)
        db.commit()
        
        # get content from file
        terms_content = pr.terms_content(cs.terms_patterns_group)
        
        # save content into database
        for term, content in terms_content.items():
            dm = DbMatch(file_id = d_file.id, term = term, content = content)
            db.add(dm)
            db.commit()
            
        # move document if all found and 'move_to_directory' was specified
        if pr.all_found() and cs.move_to_directory:
            sh.move(doc, cs.move_to_directory)
    
    # export
    # formulate sql query filtering for the current strategy
    sql = select(DbStrategy.id, DbProcessedFile.id, DbProcessedFile.filename, DbMatch.term, DbMatch.content)\
    .join(DbStrategy.processed_files).join(DbProcessedFile.matches)\
    .filter(DbStrategy.id == d_strategy.id)
    
    # translate into pandas dataframe
    df = pd.read_sql_query(sql=sql, con=db.connection())
    
    # pivot to wide
    df_wide = df.pivot(index=['filename'], columns='term', values='content')
    
    # pass wide dataframe to exporter
    exp = exporter(df_wide)
    
    # set separator for csv only
    if cs.export_format == "csv":
        exporter.separator = cs.export_csv_divider
    
    # write to file
    exp.export(cs.export_path)
    
def main(config_file: str, db_file: str):
    config = read_config_file(config_file)
    engine = create_engine(f'sqlite:///{db_file}')
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # save run info
    run = DbRun(title = config.title,
              yml_filename = config_file,
              yml_sha256 = file_sha256(config_file))
    db.add(run)
    db.commit()
    
    for strategy_name, strategy in config.strategies.items():
        # processor is chosen according to strategy.file_format
        processor = file_format_options[strategy.file_format]
        # exporter is chosen according to strategy.export_format
        exporter = export_format_options[strategy.export_format]
        # process using correct processor
        process_strategy(strategy_name, strategy, db, run.id, processor, exporter)

    db.close()
    
def cli():
    parser = argparse.ArgumentParser(description="A package for picking the juciest text morsels out of a pile of documents.")
    parser.add_argument('-c', '--config', default='config.yml', help='Path to configuration YAML file.')
    parser.add_argument('-d', '--database', default='matches.db', help='Path to SQLite database file.')
    parser.add_argument('-v', '--version', help = "Print version and exit.", action="store_true")
    parser.add_argument('-r', '--readout', help = "Only read contents of file and exit.")
    args = parser.parse_args()
    
    # version?
    if args.version:
        print(f"{__version__}")
        exit(0)
        
    # read out only?
    if args.readout:
        if os.path.isfile(args.readout):
            # determine file ending
            fe = pl.Path(args.readout).suffix[1:]
            # file format implemented?
            if fe not in file_format_options.keys():
                print(f"File '{args.readout}' appears to be of a type that cannot be read out!")
                exit(1)
            # determine processor
            processor = file_format_options[fe]
            # print out
            pr = processor(args.readout, 100) # second argument inconsequential, to be removed at a later point
            print(pr.text)
            # exit
            exit(0)
        else:
            print("No file to read out provided!")
            parser.print_help()
            exit(1)
    
    # check if config exists!
    if not os.path.isfile(args.config):
        print("No configuration file provided! Please add one using -c! Apply -h for help.\n")
        parser.print_help()
        exit(1)

    main(args.config, args.database)
    
if __name__ == "__main__":
    cli()
    
    