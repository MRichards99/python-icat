"""HTTP with chunked transfer encoding for urllib.

This module provides the handlers ChunkedHTTPHandler and
ChunkedHTTPSHandler that are suitable to be used as openers for
urllib.  These handlers differ from the standard counterparts in that
they send the data using chunked transfer encoding to the HTTP server.

**Note**: This module might be useful independently of python-icat.
It is included here because python-icat uses it internally, but it is
not considered to be part of the API.  Changes in this module are not
considered API changes of python-icat.  It may even be removed from
future versions of the python-icat distribution without further
notice.
"""

from httplib import HTTPConnection, HTTPSConnection
from urllib2 import URLError, HTTPHandler, HTTPSHandler


# We always set the Content-Length header for these methods because some
# servers will otherwise respond with a 411
_METHODS_EXPECTING_BODY = {'PATCH', 'POST', 'PUT'}

def stringiterator(buffer):
    """Wrap a string in an iterator that yields it in one single chunk."""
    if len(buffer) > 0:
        yield buffer

def fileiterator(f, chunksize=8192):
    """Yield the content of a file by chunks of a given size at a time."""
    while True:
        chunk = f.read(chunksize)
        if not chunk:
            break
        yield chunk

class ChunkedHTTPConnectionMixin:
    """Implement chunked transfer encoding in HTTP.

    This is designed as a mixin class to modify either HTTPConnection
    or HTTPSConnection accordingly.
    """

    def _send_request(self, method, url, body, headers):
        # This method is taken and modified from the Python 2.7
        # httplib.py to prevent it from trying to set a Content-length
        # header and to hook in our send_body() method.
        # Admitted, it's an evil hack.
        header_names = {k.lower(): k for k in headers.keys()}
        skips = {}
        if 'host' in header_names:
            skips['skip_host'] = 1
        if 'accept-encoding' in header_names:
            skips['skip_accept_encoding'] = 1

        self.putrequest(method, url, **skips)

        chunked = False
        if 'transfer-encoding' in header_names:
            if headers[header_names['transfer-encoding']] == 'chunked':
                chunked = True
            else:
                raise HTTPException("Invalid Transfer-Encoding")

        for hdr, value in headers.iteritems():
            self.putheader(hdr, value)
        self.endheaders()
        self.send_body(body, chunked)

    def send_body(self, body, chunked):
        """Send the body, either as is or chunked.

        The empty line separating the headers from the body must have
        been sent before calling this method.
        """
        if body is not None:
            if isinstance(body, type(b'')):
                bodyiter = stringiterator(body)
            elif isinstance(body, type(u'')):
                bodyiter = stringiterator(body.encode('ascii'))
            elif hasattr(body, 'read'):
                bodyiter = fileiterator(body)
            elif hasattr(body, '__iter__'):
                bodyiter = body
            else:
                raise TypeError("expect either a string, a file, "
                                "or an iterable")
            if chunked:
                for chunk in bodyiter:
                    self.send(hex(len(chunk))[2:].encode('ascii') 
                              + b"\r\n" + chunk + b"\r\n")
                self.send(b"0\r\n\r\n")
            else:
                for chunk in bodyiter:
                    self.send(chunk)

class ChunkedHTTPConnection(ChunkedHTTPConnectionMixin, HTTPConnection):
    pass

class ChunkedHTTPSConnection(ChunkedHTTPConnectionMixin, HTTPSConnection):
    pass


class ChunkedHTTPHandlerMixin:
    """Internal helper class.

    This is designed as a mixin class to modify either HTTPHandler or
    HTTPSHandler accordingly.  It overrides do_request_() inherited
    from AbstractHTTPHandler.
    """

    def do_request_(self, request):
        # The original method from AbstractHTTPHandler sets some
        # defaults that are unsuitable for our use case.  In
        # particular it tries to enforce Content-length to be set (and
        # fails doing so if data is not a string), while for chunked
        # transfer encoding Content-length must not be set.

        # Compatibility: in Python 2, we must call get_host() which
        # extracts the host part from the URL.  In Python 3, the
        # splitting is already done in the constructor, so we may just
        # access the attribute host instead.  In Python 3.4,
        # get_host() has been removed.
        try:
            host = request.get_host()
        except AttributeError:
            host = request.host
        if not host:
            raise URLError('no host given')

        if request.data is not None:
            if not request.has_header('Content-type'):
                raise URLError('no Content-type header given')
            if not request.has_header('Content-length'):
                if isinstance(request.data, (type(b''), type(u''))):
                    request.add_unredirected_header(
                        'Content-length', '%d' % len(request.data))
                else:
                    request.add_unredirected_header(
                        'Transfer-Encoding', 'chunked')
        else:
            if request.get_method().upper() in _METHODS_EXPECTING_BODY:
                request.add_unredirected_header('Content-length', '0')

        sel_host = host
        if request.has_proxy():
            # Similar compatibility issue for selector as for host.
            try:
                selector = request.get_selector()
            except AttributeError:
                selector = request.selector
            scheme, sel = splittype(selector)
            sel_host, sel_path = splithost(sel)
        if not request.has_header('Host'):
            request.add_unredirected_header('Host', sel_host)
        for name, value in self.parent.addheaders:
            name = name.capitalize()
            if not request.has_header(name):
                request.add_unredirected_header(name, value)

        return request

class ChunkedHTTPHandler(ChunkedHTTPHandlerMixin, HTTPHandler):

    def http_open(self, req):
        return self.do_open(ChunkedHTTPConnection, req)

    http_request = ChunkedHTTPHandlerMixin.do_request_

class ChunkedHTTPSHandler(ChunkedHTTPHandlerMixin, HTTPSHandler):

    def https_open(self, req):
        if hasattr(self, '_context') and hasattr(self, '_check_hostname'):
            # Python 3.2 and newer
            return self.do_open(ChunkedHTTPSConnection, req,
                                context=self._context, 
                                check_hostname=self._check_hostname)
        elif hasattr(self, '_context'):
            # Python 2.7.9
            return self.do_open(ChunkedHTTPSConnection, req,
                                context=self._context)
        else:
            # Python 2.7.8 or 3.1 and older
            return self.do_open(ChunkedHTTPSConnection, req)

    https_request = ChunkedHTTPHandlerMixin.do_request_

