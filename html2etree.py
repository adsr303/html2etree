from html.entities import entitydefs
from html.parser import HTMLParser
from io import StringIO
import xml.etree.ElementTree as ET


class HTML2ETree(HTMLParser):
    """HTML parser that attempts to build an ElementTree."""

    def __init__(self):
        HTMLParser.__init__(self)
        self._tree = None
        self._stack = []
        self._text = None
        self._tail = None  # Last-ended element in scope, if any

    @classmethod
    def parse(cls, source):
        """Parse an external HTML document into an ElementTree.

        source - a filename or a file-like object.
        """
        try:
            f = open(source)
        except TypeError:
            return cls.fromstringlist(source)
        with f:
            return cls.fromstringlist(f)

    @classmethod
    def fromstring(cls, text):
        """Parse HTML into an ElementTree from string constant."""
        return cls.fromstringlist([text])

    @classmethod
    def fromstringlist(cls, sequence):
        """Parse HTML into an ElementTree from a sequence of strings."""
        parser = cls()
        for text in sequence:
            if isinstance(text, bytes):
                text = str(text, 'utf-8')  # TODO encoding?
            parser.feed(text)
        parser.close()
        return parser._tree

    def tree(self):
        """Return the parsed ElementTree."""
        return self._tree

    def handle_starttag(self, tag, attrs):
        self._stack.append(self._handle_start_sub(tag, attrs))
        self._tail = None

    def handle_endtag(self, tag):
        self._tail = self._stack.pop()
        # TODO May need some heuristics to track back up (c.f. <br> or <hr>).
        assert self._tail.tag == tag

    def handle_startendtag(self, tag, attrs):
        self._tail = self._handle_start_sub(tag, attrs)

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
        self._handle_special_sub(ET.Comment(data))

    #def handle_decl(self, decl):
    #    pass

    def handle_pi(self, data):
        self._handle_special_sub(ET.ProcessingInstruction(data))

    def _top(self):
        """Return top element on stack."""
        return self._stack[-1]

    def _settext(self):
        """Append text in the right place depending on context.

        When an element was just started, set its text. When there were
        children elements, set last child's tail.
        """
        if self._text:
            if self._tail:
                self._tail.tail = self._text.getvalue()
            else:
                self._top().text = self._text.getvalue()
            self._text = None

    def _handle_start_sub(self, tag, attrs):
        """Append new Element from tag and return it."""
        elem = ET.Element(tag, dict(attrs))
        self._settext()
        if self._stack:
            self._top().append(elem)
        else:
            self._tree = ET.ElementTree(elem)
        return elem

    def _handle_special_sub(self, elem):
        """Append new special element."""
        self._settext()
        self._tail = elem
        self._top().append(elem)
