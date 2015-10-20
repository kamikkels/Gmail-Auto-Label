#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
autolabelflask

REST interface for Autolabeler, starts up a autolabeler via webhooks

@category   Utility
@version    $ID: 1.1.1, 2015-07-17 17:00:00 CST $;
@author     KMR
@licence    GNU GPL v.3
"""

import os, yaml
import time, sys
import autolabel
from daemon import Daemon
from flask import Flask, request, jsonify, redirect

class autolabelDaemon(Daemon):
    DIR = os.path.dirname(os.path.realpath(__file__))
    conf = yaml.safe_load(open("{}/flask.cfg".format(DIR)))
    app = Flask(__name__)

    gal = autolabel.autolabel()

    def run(self):
        @self.app.route(self.conf['RUNCALL'])
        def labeler():
            """ Run the autolabeler, and return the results
            :return: output of the labeler run
            """
            return self.gal.run()

        @self.app.route(self.conf['AUTHCALL'])
        def oauth2callback():
            """ Authenticate the app with the GMail API
            :return: results of the authentication run
            """
            con = self.gal.get_gmailcon()
            if 'code' not in request.args:
                auth_uri = con.get_auth_url()
                del con
                return redirect(auth_uri)
            else:
                auth_code = request.args.get('code')
                try:
                    result = con.set_credentials(auth_code)
                except:
                    return 'Get credentials [Failed]'
                return 'Get credentials {}'.format(result)

        self.app.run(host=self.conf['HOST'], port=self.conf['PORT'])

if __name__ == "__main__":
    daemon = autolabelDaemon('/tmp/gal.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)