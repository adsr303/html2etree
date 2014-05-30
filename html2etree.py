from html.entities import entitydefs
from html.parser import HTMLParser
from io import StringIO
import xml.etree.ElementTree as ET


class HTML2ETree(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self._tree = None
        self._stack = []
        self._text = None

    def handle_starttag(self, tag, attrs):
        self.handle_startendtag(tag, attrs)

    def handle_endtag(self, tag):
        assert self._tree.pop().tag == tag

    def handle_startendtag(self, tag, attrs):
        if self._text:
            self._stack[-1].text = self._text.getvalue()
            self._text = None
        attrs = dict(attrs)
        if self._stack:
            ET.SubElement(self._stack[-1], tag, attrs)
        else:
            self._stack.append(ET.Element(tag, attrs))
            self._tree = ET.ElementTree(self._stack[-1])
        self._text = StringIO()

    def handle_data(self, data):
        if self._text == None:
            self._text = StringIO()
        self._text.write(data)

    def handle_entityref(self, name):
        self.handle_data(entitydefs[name])

    def handle_charref(self, name):
        if name.startswith('x'):
            codepoint = int(name[1:], 16)
        else:
            codepoint = int(name)
        self.handle_data(chr(codepoint))

    def handle_comment(self, data):
        self._stack[-1].append(ET.Comment(data))

    def handle_decl(self, decl):
        pass

    def handle_pi(self, data):
        self._stack[-1].append(ET.ProcessingInstruction(data))

    def close(self):
        super().close()
        return self._tree
