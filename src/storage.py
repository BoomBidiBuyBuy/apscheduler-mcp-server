import envs

def get_database_url() -> str:
    if envs.STORAGE_DB.startswith("sqlite"):
        if envs.STORAGE_DB == "sqlite-memory":
            return "sqlite:///:memory:"
        else:
            return "sqlite:///./dev.db"
    elif envs.STORAGE_DB == "postgres":
        return f"postgresql+psycopg2://{envs.PG_USER}:{envs.PG_PASSWORD}@{envs.PG_HOST}:{envs.PG_PORT}/telegram_bot"
    else:
        raise ValueError("The `STORAGE_DB` env variable is not correct")

def get_scheduler_jobstore():
    database_url = get_database_url()
    
    return {
        'default': {
            'type': 'sqlalchemy',
            'url': database_url,
            'tablename': 'apscheduler_jobs'
        }
    }