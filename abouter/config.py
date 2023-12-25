import yaml

from pydantic import BaseSettings, Field, SecretStr


class OpenAI(BaseSettings):
    api_key: SecretStr = Field(env="OPENAI_API_KEY")
    model: str = Field("gpt-3.5-turbo-1106")
    temperature: float = Field(0)
    prompt: str

class LoggingSettings(BaseSettings):
    level: str = Field("WARNING", env="LOGGING_LEVEL")

class ServerSettings(BaseSettings):
    location: str|list[str]
    port: int = Field(8080, env="SERVER_PORT")

class MongoDB(BaseSettings):
    address: str = Field("", env="MONGODB_ADDRESS")
    collection: str = Field("prerendered_abouts", env="MONGODB_COLLECTION")

class Config(BaseSettings):
    openai: OpenAI
    logging: LoggingSettings
    server: ServerSettings
    db: MongoDB
    abouts_cap: int = Field(300)
    simulation_chunk_delay: float = Field(0.1)

    def __init__(self, filename:str="config/config.yaml"):
        # Load a YAML configuration file
        with open(filename, 'r') as f:
            conf = yaml.safe_load(f)
        
        super().__init__(**conf)
