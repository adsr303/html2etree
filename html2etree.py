from html.entities import entitydefs
from html.parser import HTMLParser
import xml.etree.ElementTree as ET


class HTML2ETree(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self._tree = ET.ElementTree()
        self._stack = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

    def handle_endtag(self, tag):
        pass

    def handle_startendtag(self, tag, attrs):
        attrs = dict(attrs)

    def handle_data(self, data):
        pass

    def handle_entityref(self, name):
        pass

    def handle_charref(self, name):
        pass

    def handle_comment(self, data):
        pass

    def handle_decl(self, decl):
        pass

    def handle_pi(self, data):
        pass

    def close(self):
        super().close()
        return self._tree
