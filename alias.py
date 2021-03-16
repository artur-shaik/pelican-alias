# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os.path
from urllib.parse import urlparse

from pelican import signals

logger = logging.getLogger(__name__)


class AliasGenerator(object):
    TEMPLATE = """<!DOCTYPE html><html><head><meta charset="utf-8" />
<meta http-equiv="refresh" content="0;url={destination}" />
</head></html>"""

    def __init__(self, context, settings, path, theme, output_path, *args):
        self.output_path = output_path
        self.context = context
        self.alias_delimiter = settings.get('ALIAS_DELIMITER', ',')
        self.add_file_extension = settings.get('ALIAS_FILE_EXTENSION', False)
        self.article_save_as = settings.get('ARTICLE_SAVE_AS')
        self.default_lang = settings.get('ALIAS_MAIN_LANG', 'en')

    def create_alias(self, page, alias):
        # If path starts with a /, remove it
        relative_alias = alias[1:] if alias[0] == '/' else alias

        path = os.path.join(self.output_path, relative_alias)
        directory, filename = os.path.split(path)

        try:
            os.makedirs(directory)
        except OSError:
            pass

        if filename == '':
            path = os.path.join(path, 'index.html')

        if self.add_file_extension:
            extension = self.article_save_as.split('.')[-1]
            if extension and not path.endswith(extension):
                path = f'{path}.{extension}'

        logger.info('[alias] Writing to alias file %s' % path)
        with open(path, 'w') as fd:
            if page.lang and page.lang != self.default_lang:
                destination = f'{page.lang}/{page.url}'
            else:
                destination = page.url
            # if schema is empty then we are working with a local path
            if not urlparse(destination).scheme:
                # if local path is missing a leading slash then add it
                if not destination.startswith('/'):
                    destination = '/{0}'.format(destination)
            fd.write(self.TEMPLATE.format(destination=destination))

    def generate_output(self, writer):
        pages = (
            self.context['pages'] + self.context['articles'] +
            self.context.get('hidden_pages', []))

        for page in pages:
            aliases = page.metadata.get('alias', [])
            if type(aliases) != list:
                aliases = aliases.split(self.alias_delimiter)
            for alias in aliases:
                alias = alias.strip()
                logger.info('[alias] Processing alias %s' % alias)
                self.create_alias(page, alias)


def get_generators(generators):
    return AliasGenerator


def register():
    signals.get_generators.connect(get_generators)
