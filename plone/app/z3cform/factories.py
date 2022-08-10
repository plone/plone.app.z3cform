from plone.namedfile.interfaces import IStorage
from plone.namedfile.storages import MAXCHUNKSIZE
from zope.interface import implementer


@implementer(IStorage)
class Zope2FileUploadStorable:
    def store(self, data, blob):
        data.seek(0)
        with blob.open("w") as fp:
            block = data.read(MAXCHUNKSIZE)
            while block:
                fp.write(block)
                block = data.read(MAXCHUNKSIZE)
