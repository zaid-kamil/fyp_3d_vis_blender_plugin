from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Create a base class for our classes to inherit from
Base = declarative_base()

class Dataset(Base):
    __tablename__ = 'Datasets'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(String(250))
    models = relationship("Model", back_populates="dataset")

    def _repr_(self):
        return f"<Dataset(name={self.name}, description={self.description})>"

class Configuration(Base):
    __tablename__ = 'Configurations'

    id = Column(Integer, primary_key=True)
    key = Column(String(50))
    value = Column(String(50))
    model_id = Column(Integer, ForeignKey('models.id'))

    def _repr_(self):
        return f"<Configuration(key={self.key}, value={self.value})>"

class Model(Base):
    __tablename__ = 'Model'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    dataset_id = Column(Integer, ForeignKey('datasets.id'))
    dataset = relationship("Dataset", back_populates="models") 
    configurations = relationship("Configuration", back_populates="model")

    def _repr_(self):
        return f"<Model(name={self.name})>"
    
def get_db():
        engine = create_engine('sqlite:///example.db')
        return sessionmaker(bind=engine)()
    
def save_to_db(object):
    db = get_db()
    db.add(object)
    db.commit()
    db.close()
# Function to create and return the database session
def get_session(database_url="sqlite:///example.db"):
    engine = create_engine(database_url, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()



# Example of using the defined classes
if __name__ == "__main__":
    session = get_session()

    # Create and add new dataset
    new_dataset = Dataset(name="Sample Dataset", description="This is a sample dataset.")
    session.add(new_dataset)
    
    # Create and add new model
    new_model = Model(name="Sample Model", dataset=new_dataset)
    session.add(new_model)
    
    # Create and add new configuration
    new_config = Configuration(key="resolution", value="1080p", model=new_model)
    session.add(new_config)
    
    # Commit the changes
    session.commit()
    
    # Query and print data
    for dataset in session.query(Dataset).all():
        print(dataset)
        for model in dataset.models:
            print(model)
            for config in model.configurations:
                print(config)