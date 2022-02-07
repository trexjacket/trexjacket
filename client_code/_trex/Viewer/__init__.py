import anvil
import anvil.media
import anvil.server

from ._anvil_designer import ViewerTemplate


class Viewer(ViewerTemplate):
    def __init__(self, publisher=None, **properties):
        self.original_image = None
        self.changes_saved = True
        try:
            publisher.subscribe(
                subscriber=self, channel="tableau.trex", handler=self.handle_message
            )
        except AttributeError:
            pass
        trex = anvil.server.call("tableau.private.get_trex", anvil.app.id)
        trex.publisher = publisher
        self.item = trex
        self.init_components(**properties)

    @property
    def file_available(self):
        return self.changes_saved and self.item.file is not None

    def handle_message(self, message):
        print(f"message content: {message.content}")
        self.changes_saved = message.content
        self.refresh_data_bindings()

    def button_save_click(self, **event_args):
        self.item.save()
        self.refresh_data_bindings()

    def button_download_click(self, **event_args):
        anvil.media.download(self.item.file)

    def file_loader_logo_change(self, file, **event_args):
        self.original_image = file
        self.item.logo = anvil.image.generate_thumbnail(file, 70)
        self.refresh_data_bindings()
