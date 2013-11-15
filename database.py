from sqlalchemy import create_engine

engine=create_engine('sqlite:///bib.db',convert_unicode=True)
metadata=Metadata(bind=engine)
collections=Table('bibfiles',metadata,autoload=True)
con=engine.connect()

