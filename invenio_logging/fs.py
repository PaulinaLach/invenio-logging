# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Invenio filesystem logging module.

Configuration
~~~~~~~~~~~~~

.. py:data:: LOGGING_FS_LOGFILE = None

   Enable logging to a console.

.. py:data:: LOGGING_FS_PYWARNINGS = False

   Enable Python warnings.

.. py:data:: LOGGING_FS_BACKUPCOUNT = 5

   Define number of backup files.

.. py:data:: LOGGING_FS_MAXBYTES = 100 * 1024 * 1024

   Define maximal file size.  (Default: 100MB)

.. py:data:: LOGGING_FS_LEVEL = 'WARNING'

   Define valid Python logging level from ``CRITICAL``, ``ERROR``, ``WARNING``,
   ``INFO``, ``DEBUG``, or ``NOTSET``. The default value is set to ``DEBUG``
   if the application is in debug mode otherwise it is set to ``WARNING``.

This extension is automatically installed via ``invenio_base.apps`` and
``invenio_base.api_apps`` entry points.
"""

from __future__ import absolute_import, print_function

import logging
import sys
from logging.handlers import RotatingFileHandler
from os.path import dirname, exists

from .ext import InvenioLoggingBase


class InvenioLoggingFS(InvenioLoggingBase):
    """Invenio-Logging extension. Filesystem handler."""

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        if app.config['LOGGING_FS_LOGFILE'] is None:
            return
        self.install_handler(app)
        app.extensions['invenio-logging-fs'] = self

    def init_config(self, app):
        """Initialize config."""
        app.config.setdefault('LOGGING_FS_LOGFILE', None)
        app.config.setdefault('LOGGING_FS_PYWARNINGS', False)
        app.config.setdefault('LOGGING_FS_BACKUPCOUNT', 5)
        app.config.setdefault('LOGGING_FS_MAXBYTES', 104857600)  # 100MB
        app.config.setdefault(
            'LOGGING_FS_LEVEL',
            'DEBUG' if app.debug else 'WARNING'
        )

        # Support injecting instance path and/or sys.prefix
        if app.config['LOGGING_FS_LOGFILE'] is not None:
            app.config['LOGGING_FS_LOGFILE'] = \
                app.config['LOGGING_FS_LOGFILE'].format(
                    instance_path=app.instance_path,
                    sys_prefix=sys.prefix,
                )

    def install_handler(self, app):
        """Install log handler on Flask application."""
        # Check if directory exists.
        basedir = dirname(app.config['LOGGING_FS_LOGFILE'])
        if not exists(basedir):
            raise ValueError(
                'Log directory {0} does not exists.'.format(basedir))

        handler = RotatingFileHandler(
            app.config['LOGGING_FS_LOGFILE'],
            backupCount=app.config['LOGGING_FS_BACKUPCOUNT'],
            maxBytes=app.config['LOGGING_FS_MAXBYTES'],
            delay=True,
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        handler.setLevel(app.config['LOGGING_FS_LEVEL'])

        # Add handler to application logger
        app.logger.addHandler(handler)

        if app.config['LOGGING_FS_PYWARNINGS']:
            self.capture_pywarnings(handler)
