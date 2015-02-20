# -*- coding: utf-8 -*-

import os
import imp
from importlib import import_module

from noseapp.datastructures import ModifyDict


def _load(obj):
    for atr in dir(obj):
        if not atr.startswith('_'):
            yield (atr, getattr(obj, atr))


class ConfigError(BaseException):
    pass


class Config(ModifyDict):
    """
    App config storage
    """

    def init_nose_config(self, nose_config):
        """
        Merge options from nose argument parser
        """
        self['nose'] = ModifyDict(
            _load(nose_config.options),
        )

    def from_module(self, module):
        """
        Init configuration from python module

        :param module: import path
        :type module: str
        """
        try:
            obj = import_module(module)
        except ImportError:
            raise ImportError('Config {} not found'.format(module))

        self.update(_load(obj))

        return self

    def from_py_file(self, file_path):
        """
        Init configuration from py file

        :param file_path: absolute file path
        :type file_path: str
        """
        if not os.path.isfile(file_path):
            raise ConfigError('config file does not exist "{}"'.format(file_path))

        elif not file_path.endswith('.py'):
            raise ConfigError('config file is not python file')

        module = imp.new_module(file_path.rstrip('.py'))
        module.__file__ = file_path

        try:
            execfile(file_path, module.__dict__)
        except IOError as e:
            e.strerror = 'Unable to load file "{}"'.format(e.strerror)
            raise

        self.update(_load(module))

        return self
