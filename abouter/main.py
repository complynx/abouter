import asyncio
import logging
from .config import Config
from .server import create_server
from motor.motor_asyncio import AsyncIOMotorClient
import hashlib
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class App(object):
    config = Config
    server = None
    collection = None
    prompt_hash = ""
    openai = None

async def main(cfg: Config):
    app = App()
    app.config = cfg

    app.openai = AsyncOpenAI(api_key=cfg.openai.api_key.get_secret_value())

    h = hashlib.new('sha256')
    h.update(f'{cfg.openai.prompt}'.encode())
    app.prompt_hash = h.hexdigest()

    logger.info(f"db address {cfg.db.address}")
    mongodb = AsyncIOMotorClient(cfg.db.address).get_database()
    app.collection = mongodb[cfg.db.collection]

    await create_server(cfg, app)
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    cfg = Config()
    logger = logging.getLogger("MAIN")

    logging.basicConfig(level=cfg.logging.level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Get or create a specific logger
    httpx_logger = logging.getLogger('httpx')
    if cfg.logging.level != "DEBUG":
        httpx_logger.setLevel(logging.WARNING)

    asyncio.run(main(cfg))
