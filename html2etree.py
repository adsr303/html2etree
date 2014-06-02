#!/usr/bin/env python3


"""A parser for HTML that builds ElementTrees.

Read HTML and use ElementTree API to navigate and analyze it.

>>> tree = HTML2ETree.fromstring('''<html><body>
...         <a href="https://github.com/adsr303/html2etree">
...         </body></html>''')
>>> tree.find('.//a[1]').get('href')
'https://github.com/adsr303/html2etree'
"""


from html.entities import entitydefs
from html.parser import HTMLParser
from io import StringIO
import xml.etree.ElementTree as ET


class HTML2ETree(HTMLParser):
    """Parse HTML documents to ElementTrees."""

    def __init__(self, backtrack=False, strict=True):
        """Create an HTML2ETree instance.

        backtrack - if True, try to recover from missing closing tags.
        strict - set to False to be tolerant about invalid HTML.
        """
        HTMLParser.__init__(self, strict)
        self._backtrack = backtrack
        self._tree = None
        self._stack = []
        self._text = None
        self._tail = None  # Last-ended element in scope, if any

    @classmethod
    def parse(cls, source, backtrack=False, strict=True):
        """Parse an external HTML document to an ElementTree.

        source - a filename or a file-like object.
        backtrack - if True, try to recover from missing closing tags.
        strict - set to False to be tolerant about invalid HTML.
        """
        try:
            f = open(source)
        except TypeError:
            return cls.fromstringlist(source, backtrack, strict)
        with f:
            return cls.fromstringlist(f, backtrack, strict)

    @classmethod
    def fromstring(cls, text, backtrack=False, strict=True):
        """Parse HTML in a string constant to an ElementTree.

        text - a string with HTML to be parsed.
        backtrack - if True, try to recover from missing closing tags.
        strict - set to False to be tolerant about invalid HTML.
        """
        return cls.fromstringlist([text], backtrack, strict)

    @classmethod
    def fromstringlist(cls, sequence, backtrack=False, strict=True):
        """Parse HTML in a sequence of strings to an ElementTree.

        sequence - a sequence of strings that contain the HTML to be parsed.
        backtrack - if True, try to recover from missing closing tags.
        strict - set to False to be tolerant about invalid HTML.
        """
        parser = cls(backtrack, strict)
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
        self._settext()
        self._tail = self._stack.pop()
        if self._backtrack:
            while self._tail.tag != tag:
                self._tail = self._stack.pop()

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
            if self._tail is not None:
                self._tail.tail = self._text.getvalue()
            elif self._stack:
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


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        backtrack = len(sys.argv) > 2 and bool(sys.argv[2])
        tree = HTML2ETree.parse(sys.argv[1], backtrack)
        print(str(ET.tostring(tree.getroot(), 'utf-8'), 'utf-8'))
