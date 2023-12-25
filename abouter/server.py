import tornado.web
import tornado.websocket
import tornado.platform.asyncio
from .config import Config
import logging
from urllib.parse import urlparse
from random import randint
import json
import datetime
from asyncio import sleep

logger = logging.getLogger(__name__)

class WS(tornado.websocket.WebSocketHandler):
    def initialize(self, app):
        self.app = app
    
    async def open(self):
        logger.debug("WebSocket opened")

    async def on_message(self, message):
        if message != "get":
            logger.info(f"received unexpected {message}")
            return

        c = self.app.collection
        cursor = c.find({"prompt_hash": {"$eq": self.app.prompt_hash}}).sort("date", -1).limit(self.app.config.abouts_cap)
        pregenerated = []
        async for p in cursor:
            pregenerated.append(p["content"])
        await cursor.close()
        rand = min(len(pregenerated)+1, self.app.config.abouts_cap)
        index = randint(0, rand-1)
        if index >= len(pregenerated):
            return await self.generate_new()
        else:
            return await self.send_pregenerated(pregenerated[index])

    async def generate_new(self):
        logger.info("generating new")
        stream = await self.app.openai.chat.completions.create(
            model=self.app.config.openai.model,
            temperature=self.app.config.openai.temperature,
            messages=[{"role":"user","content":self.app.config.openai.prompt}],
            stream=True,
        )
        content = []
        start = datetime.datetime.now()
        chunk_start = datetime.datetime.now()
        async for chunk in stream:
            chunk_delta = datetime.datetime.now() - chunk_start
            chunk_start = datetime.datetime.now()
            cc = chunk.choices[0].delta.content
            if cc is not None:
                logger.info(f"got next chunk: {cc}")
                content.append({
                    "chunk": cc,
                    "time_delta": chunk_delta.total_seconds(),
                })
                await self.write_message(json.dumps({
                    "chunk": cc
                }))
        delta = (datetime.datetime.now() - start).total_seconds()
        logger.info(f"received full message, time spent: {delta}")

        await self.app.collection.insert_one({
            "content": content,
            "prompt_hash": self.app.prompt_hash,
            "date": datetime.datetime.now(),
            "time_spent": delta,
        })
        logger.info(f"saved to db")

        self.write_message(json.dumps({
            "finished": True,
        }))
        logger.info(f"finished routine")

    async def send_pregenerated(self, message):
        logger.info(f"using pregenerated {message}")

        for rune in message:
            await sleep(rune["time_delta"])
            await self.write_message(json.dumps({
                "chunk": rune["chunk"]
            }))
        self.write_message(json.dumps({
            "finished": True,
        }))
        logger.info(f"finished routine")

    def on_close(self):
        logger.debug("WebSocket closed")
    
    def check_origin(self, origin):
        loc = self.app.config.server.location
        if loc == "":
            return True
        
        if isinstance(loc, list):
            for loc1 in loc:
                parsed_origin = urlparse(origin)
                return parsed_origin.netloc == loc1 or parsed_origin.netloc.endswith(f".{loc1}")
        else:
            parsed_origin = urlparse(origin)
            return parsed_origin.netloc == loc or parsed_origin.netloc.endswith(f".{loc}")

async def create_server(config: Config, base_app):
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    app = tornado.web.Application([
        (r"/ws", WS, {"app": base_app}),
    ])
    app.listen(config.server.port)
    base_app.server = app

    return app
