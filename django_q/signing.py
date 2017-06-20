"""Package signing."""
try:
    import cPickle as pickle
except ImportError:
    import pickle

from django.core import signing

from django_q.conf import Conf

import json

BadSignature = signing.BadSignature


class SignedPackage(object):

    """Wraps Django's signing module with custom Pickle serializer."""

    @staticmethod
    def dumps(obj, compressed=Conf.COMPRESSED):
        return json.dumps(obj)

    @staticmethod
    def loads(obj):
        return json.loads(obj)


class PickleSerializer(object):

    """Simple wrapper around Pickle for signing.dumps and signing.loads."""

    @staticmethod
    def dumps(obj):
        return pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def loads(data):
        return pickle.loads(data)
