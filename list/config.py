from pydantic_settings import BaseSettings, SettingsConfigDict

#подгруз настроек из env 
class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    RPC_URL: str = "https://eth.llamarpc.com"
    HSM_LIB_PATH: str = "/usr/lib/hsm_lib.so"

    @property
    def DATABASE_URL_psycopg2(self):
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file="sas.env")

settings = Settings()