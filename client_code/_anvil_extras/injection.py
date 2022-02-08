# SPDX-License-Identifier: MIT
#
# Copyright (c) 2021 The Anvil Extras project team members listed at
# https://github.com/anvilistas/anvil-extras/graphs/contributors
#
# This software is published at https://github.com/anvilistas/anvil-extras

import anvil.js
from anvil.js.window import Promise as _Promise
from anvil.js.window import document as _document

__version__ = "1.9.0"


class HTMLInjector:
    _injected_css = set()

    def css(self, css):
        """inject some custom css"""
        hashed = hash(css)
        if hashed in self._injected_css:
            return
        sheet = self._create_tag("style")
        sheet.innerHTML = css
        self._inject(sheet, head=False)
        self._injected_css.add(hashed)

    def cdn(self, cdn_url, **attrs):
        """inject a js/css cdn file"""
        if cdn_url.endswith("js"):
            tag = self._create_tag("script", src=cdn_url, **attrs)
        elif cdn_url.endswith("css"):
            tag = self._create_tag("link", href=cdn_url, rel="stylesheet", **attrs)
        else:
            raise ValueError("Unknown CDN type expected css or js file")
        self._inject(tag)
        self._wait_for_load(tag)

    def script(self, js):
        """inject some javascript code inside a script tag"""
        s = self._create_tag("script")
        s.textContent = js
        self._inject(s)

    def _create_tag(self, tag_name, **attrs):
        tag = _document.createElement(tag_name)
        for attr, value in attrs.items():
            tag.setAttribute(attr, value)
        return tag

    def _inject(self, tag, head=True):
        if head:
            _document.head.appendChild(tag)
        else:
            _document.body.appendChild(tag)

    def _wait_for_load(self, tag):
        if not tag.get("src"):
            return

        def do_wait(res, rej):
            tag.onload = res
            tag.onerror = rej

        p = _Promise(do_wait)
        anvil.js.await_promise(p)