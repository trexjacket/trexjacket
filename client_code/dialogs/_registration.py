_forms = {}


class dialog_form:
    def __init__(self, form_name):
        _forms[form_name] = self.__class__
        self.name = form_name

    def __call__(self, cls):
        _forms[self.name] = cls

        class WrappedForm(cls):
            def __init__(self, *args, **kwargs):
                cls.__init__(self, *args, **kwargs)

        return WrappedForm
