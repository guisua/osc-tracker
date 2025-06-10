import abc
import logging
import re

from app.reaper.handlers.message import OSCMessageHandler


class InvalidTrackIdError(Exception):
    """Custom exception for errors in extracting track ID from address."""

    pass


class TrackHandler(OSCMessageHandler, abc.ABC):
    suffix: str
    attribute: str
    cast: type

    def __init__(self, logger: logging.Logger = logging.getLogger(__name__)):
        super().__init__(logger)
        self.pattern = rf"^/track/(\d+)/{self.suffix}"
        self.regex = re.compile(self.pattern)

    def matches(self, address: str) -> bool:
        return bool(self.regex.match(address))

    def extract_track_id(self, address: str) -> int:
        match = self.regex.match(address)
        if match:
            return int(match.group(1))
        raise InvalidTrackIdError(f"Could not extract track id from {address}")

    def handle(self, reaper, address, *args) -> bool:
        try:
            track_id = self.extract_track_id(address)
            if args:
                value = self.cast(args[0])
                setattr(reaper.state.track(track_id), self.attribute, value)
                self._logger.info(f"Track {track_id} {self.attribute} set to {value}")
        except InvalidTrackIdError as e:
            self._logger.error(f"Error handling {self.attribute} for {address}: {e}")
            return False
        return True


class VolumeHandler(TrackHandler):
    suffix = "vu$"
    attribute = "volume"
    cast = float


class MuteHandler(TrackHandler):
    suffix = "mute$"
    attribute = "muted"
    cast = bool


class NameHandler(TrackHandler):
    suffix = "name$"
    attribute = "name"
    cast = str


class SoloHandler(TrackHandler):
    suffix = "solo$"
    attribute = "solo"
    cast = bool


class RecArmHandler(TrackHandler):
    suffix = "recarm$"
    attribute = "rec_armed"
    cast = bool
