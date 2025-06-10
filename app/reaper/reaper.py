from pydantic import BaseModel
from threading import Thread
import logging
import socket
from pythonosc import dispatcher, osc_server
from pythonosc.udp_client import SimpleUDPClient

from app.reaper.handlers.message import OSCMessageHandler
from .models.track import Track


class ReaperConfig(BaseModel):
    listen_ip: str = "0.0.0.0"
    listen_port: int = 9000
    send_ip: str = "127.0.0.1"
    send_port: int = 9001
    log_unhandled: bool = True
    log_unhandled_level: int = logging.WARNING


class ReaperState(BaseModel):
    tracks: dict[int, Track] = {}

    def track(self, track_id: int, name: str = "", **kwargs) -> Track:
        if track_id not in self.tracks:
            self.tracks[track_id] = Track(id=track_id, name=name, **kwargs)
        return self.tracks[track_id]

    def track_by_name(self, name: str) -> Track | None:
        for track in self.tracks.values():
            if track.name == name:
                return track
        raise ValueError(f"Track with name '{name}' not found")


class ReaperOSC:
    def __init__(
        self,
        config: ReaperConfig,
        handlers: list[OSCMessageHandler],
        logger: logging.Logger = logging.getLogger(__name__),
    ):
        self.config = config
        self._logger = logger
        self.state = ReaperState()
        self.osc_client = SimpleUDPClient(
            config.send_ip,
            config.send_port,
            family=socket.AF_INET,
        )
        self.handlers = handlers

        for handler in self.handlers:
            handler._logger = self._logger
            self._logger.debug(f"Registered handler: {handler.__class__.__name__}")
        self.server_thread = None
        self._start_server()

    def _start_server(self):
        disp = dispatcher.Dispatcher()
        disp.set_default_handler(self._eval_message)
        server = osc_server.ThreadingOSCUDPServer(
            server_address=(self.config.listen_ip, self.config.listen_port),
            dispatcher=disp,
        )
        self.server_thread = Thread(target=server.serve_forever, daemon=True)
        self.server_thread.start()
        self._logger.info(
            f"Serving OSC on {self.config.listen_ip}:{self.config.listen_port}"
        )

    def _eval_message(self, address, *args):
        for handler in self.handlers:
            if handler.matches(address):
                handler.handle(self, address, *args)
                return
        if self.config.log_unhandled:
            self._logger.log(
                self.config.log_unhandled_level,
                f"Unhandled OSC message at {address}: {args}",
            )

    def refresh_tracks(self):
        self._logger.info(
            f"Refreshing track list on {self.config.send_ip}:{self.config.send_port}"
        )
        self.osc_client.send_message("/action/41743", [])
