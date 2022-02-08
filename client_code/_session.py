from time import sleep

from . import model
from ._anvil_extras.injection import HTMLInjector
from ._anvil_extras.messaging import Publisher
from ._anvil_extras.non_blocking import call_async
from ._logging import Logger

cdn_url = "https://cdn.jsdelivr.net/gh/tableau/extensions-api/lib/tableau.extensions.1.latest.js"


def _inject_tableau():
    injector = HTMLInjector()
    injector.cdn(cdn_url)

    from anvil.js.window import tableau

    return tableau


class Session:
    def __init__(self):
        self.logger = Logger()
        self.logger.log("Starting new session")
        self._initializing = True
        self.timeout = 2
        self.event_types = {
            "filter_changed": None,
            "selection_changed": None,
            "parameter_changed": None,
        }
        self.proxies = {}
        self.publisher = Publisher()
        self.dashboard = model.Dashboard()
        self._tableau = _inject_tableau()
        async_call = call_async(self._tableau.extensions.initializeAsync)
        async_call.on_result(self._on_init)

    def _on_init(self, result):
        self.dashboard.proxy = self._tableau.extensions.dashboardContent.dashboard
        self.event_types = {
            "filter_changed": self._tableau.TableauEventType.FilterChanged,
            "selection_changed": self._tableau.TableauEventType.MarkSelectionChanged,
            "parameter_changed": self._tableau.TableauEventType.ParameterChanged,
        }
        self.proxies = {
            self._tableau.TableauEventType.FilterChanged: model.FilterChangedEvent,
            self._tableau.TableauEventType.MarkSelectionChanged: model.MarksSelectedEvent,
            self._tableau.TableauEventType.ParameterChanged: model.ParameterChangedEvent,
        }
        self._initializing = False

    @property
    def available(self):
        waited = 0
        step = 0.1
        if self._initializing:
            self.logger.log(f"Dashboard is still initialising. Waiting for a max of {self.timeout} seconds...")
        while self._initializing and waited <= self.timeout:
            sleep(step)
            waited += step
        self.logger.log(f"Waited for {waited} seconds")
        return self.dashboard.proxy is not None
