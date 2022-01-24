from .Viewer import Viewer
import anvil


def show_trex(publisher=None):
    anvil.alert(
        content=Viewer(publisher), buttons=None, large=True, title="Trex Details"
    )
