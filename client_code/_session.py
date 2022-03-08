from time import sleep

import anvil

from . import model
from ._anvil_extras.injection import HTMLInjector
from ._anvil_extras.messaging import Publisher
from ._anvil_extras.non_blocking import call_async
from ._logging import Logger

CDN_URL = "https://cdn.jsdelivr.net/gh/tableau/extensions-api/lib/tableau.extensions.1.latest.js"  # noqa


def _inject_tableau():
    injector = HTMLInjector()
    injector.cdn(CDN_URL)

    from anvil.js.window import tableau

    return tableau


class TableauSession:
    def __init__(self):
        self.logger = Logger()
        self.logger.log("Starting new session")
        self._initializing = True
        self.timeout = 2
        self.publisher = Publisher()
        self.event_type_mapper = model.EventTypeMapper()
        self.dashboard = model.Dashboard()
        self._tableau = _inject_tableau()
        async_call = call_async(self._tableau.extensions.initializeAsync)
        async_call.on_result(self._on_init)
        async_call.on_error(self.handle_error)

    def _on_init(self, result):
        self.dashboard.proxy = self._tableau.extensions.dashboardContent.dashboard
        self.event_type_mapper.tableau = self._tableau
        self._initializing = False

    def handle_error(self, err):
        self.logger.log(err)
        anvil.Notification("Failed to initialize tableau", style="danger").show()

    @property
    def available(self):
        waited = 0
        step = 0.1
        if self._initializing:
            self.logger.log(
                "Dashboard is still initialising. "
                f"Waiting for a max of {self.timeout} seconds..."
            )
        while self._initializing and waited <= self.timeout:
            sleep(step)
            waited += step
        self.logger.log(f"Waited for {waited} seconds")
        return self.dashboard.proxy is not None
