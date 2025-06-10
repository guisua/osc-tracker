import logging
import os
from fastapi import FastAPI

from app.reaper import reaper as reap
from app.reaper.handlers.track import (
    VolumeHandler,
    MuteHandler,
    NameHandler,
    SoloHandler,
    RecArmHandler,
)
from app.reaper.models.track import Track


# Configure logging to use uvicorn.error logger
uvicorn_logger = logging.getLogger("uvicorn.error")
logging.basicConfig(handlers=uvicorn_logger.handlers, level=logging.INFO)
logging.root.handlers = uvicorn_logger.handlers
logging.root.setLevel(logging.INFO)

# Initialize ReaperOSC with configuration and handlers
reaper_config = reap.ReaperConfig(
    listen_ip=os.getenv("REAPER_LISTEN_IP", "0.0.0.0"),
    listen_port=int(os.getenv("REAPER_LISTEN_PORT", 9000)),
    send_ip=os.getenv("REAPER_SEND_HOST", "localhost"),
    send_port=int(os.getenv("REAPER_SEND_PORT", 9001)),
    log_unhandled_level=logging.DEBUG,
)

reaper = reap.ReaperOSC(
    config=reaper_config,
    handlers=[
        VolumeHandler(),
        MuteHandler(),
        NameHandler(),
        SoloHandler(),
        RecArmHandler(),
    ],
    logger=logging.getLogger("reaper"),
)

# Create FastAPI app and define endpoints
app = FastAPI()


@app.get("/refresh")
async def refresh():
    """Endpoint to refresh the track list."""
    reaper.refresh_tracks()
    return {"message": "Track list refreshed"}


@app.get("/tracks", response_model=list[Track])
def get_tracks():
    """Endpoint to get the list of tracks."""
    return list(reaper.state.tracks.values())
