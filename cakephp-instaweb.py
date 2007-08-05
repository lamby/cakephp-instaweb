#!/usr/bin/env python

"""
  cakephp-instaweb.py

  Copyright (C) 2007 Chris Lamb <chris@chris-lamb.co.uk>

  Permission is hereby granted, free of charge, to any person obtaining a
  copy of this software and associated documentation files (the "Software"),
  to deal in the Software without restriction, including without limitation
  the rights to use, copy, modify, merge, publish, distribute, sublicense,
  and/or sell copies of the Software, and to permit persons to whom the
  Software is furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
  DEALINGS IN THE SOFTWARE.
"""

from twisted.internet import reactor, error
from twisted.web import static, server, twcgi, rewrite
from twisted.application import strports

from optparse import OptionParser

import os, sys

def main():
    options = parse_options()

    class PHPScript(twcgi.FilteredScript):
        filter = "/etc/alternatives/php-cgi"
        def runProcess(self, env, request, qargs=[]):
            env['SCRIPT_NAME'] = '/index.php'
            twcgi.FilteredScript.runProcess(self, env, request, qargs)

    root = static.File(options.webroot)
    root.processors = {'.php' : PHPScript}
    root.indexNames = ['index.php']

    def rewrite_rule(request):
        # Emulate Apache's mod_rewrite - if the file does not exist, then
        # rewrite as a suffix to '/index.php?url='
        if not os.access("%s/%s" % (options.webroot, request.path), os.F_OK):
            request.uri = "/index.php?url=%s" % request.path
            request.postpath = ['index.php']
        return request

    if options.rewrite:
        root = rewrite.RewriterResource(root, rewrite_rule)

    try:
        reactor.listenTCP(options.port, server.Site(root), interface=options.interface)
    except error.CannotListenError, e:
        print >>sys.stderr, "Couldn't listen on port %d: %s" % (options.port, e.socketError)
        sys.exit(-1)

    print >>sys.stderr, "Running on http://localhost:%d/" % options.port
    print >>sys.stderr, "Press CTRL+C to stop hosting"
    reactor.run()

def parse_options():
    usage = "%prog [webroot]"
    parser = OptionParser(usage=usage)
    parser.add_option("-p", "--port", dest="port", type="int",
        help="serve on port PORT (default: 8080)",
        metavar="PORT", default="8080")
    parser.add_option("-i", "--interface", dest="interface",
        help="interface to serve from (default: 127.0.0.1)",
        default="127.0.0.1")
    parser.add_option("-r", "--disable-rewrite", dest="rewrite",
        help="disable URL rewriting", action="store_false",
        default=True)

    (options, args) = parser.parse_args()

    if len(args) == 0:
        options.webroot = find_webroot()
    elif len(args) == 1:
        options.webroot = args[0]
    else:
        parser.error('incorrect number of arguments')

    return options

def find_webroot():
    webroot = os.getcwd()
    search = ['src', 'app', 'webroot']
    for i in range(len(search)):
        path = os.path.join(*[webroot] + search[i:])
        if os.path.exists(path):
            webroot = path
            break
    return webroot

if __name__ == "__main__":
    main()
