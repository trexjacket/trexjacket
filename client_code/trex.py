import anvil.server


@anvil.server.portable_class
class Trex:
    defaults = {
        "uid": None,
        "name": "",
        "description": "",
        "url": "",
        "author_name": "",
        "author_email": "",
        "author_website": "",
        "author_org": "",
        "full_permission": False,
        "logo": None,
        "file": None,
    }

    def __init__(self):
        self.__dict__.update(self.defaults)

    def __str__(self):
        return str(self.__dict__)

    def _handle_cache_update(self, update):
        self.file = update["file"]

    @property
    def details(self):
        result = self.__dict__.copy()
        for attr in ["uid", "capability", "file", "logo"]:
            del result[attr]
        return result

    def save(self):
        anvil.server.call("tableau.private.save_trex", self)
