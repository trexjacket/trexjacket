import anvil
import anvil.server


class Cache:
    def __init__(self):
        self.items = {"publisher": None}

    def __getitem__(self, name):
        return self.items[name]

    def __setitem__(self, name, value):
        self.items[name] = value


cache = Cache()


@anvil.server.portable_class
class Trex:
    defaults = {
        "publisher": None,
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

    def __serialize__(self, global_data):
        _dict = self.__dict__.copy()
        del _dict["publisher"]
        return _dict

    def __deserialize__(self, data, global_data):
        self.__dict__.update(data)
        self._publisher = cache["publisher"]
        self.capability.set_update_handler(self._handle_cache_update)

    def __setattr__(self, name, value):
        if name == "publisher":
            cache["publisher"] = value
        else:
            try:
                self.publisher.publish(
                    channel="tableau.trex", title="changes_saved", content=False
                )
            except AttributeError:
                pass
        self.__dict__[name] = value

    def _handle_cache_update(self, update):
        self.file = update["file"]
        try:
            self.publisher.publish(
                channel="tableau.trex", title="changes_saved", content=True
            )
        except AttributeError:
            pass

    @property
    def details(self):
        result = self.__dict__.copy()
        for attr in ["uid", "capability", "file", "logo"]:
            del result[attr]
        return result

    def save(self):
        anvil.server.call("tableau.private.save_trex", self)
