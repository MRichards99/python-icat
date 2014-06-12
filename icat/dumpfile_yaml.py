"""YAML dump file backend for icatdump.py and icatrestore.py.
"""

import icat
import datetime
import yaml

__all__ = ['YAMLDumpFileReader', 'YAMLDumpFileWriter']


# ------------------------------------------------------------
# Helper
# ------------------------------------------------------------

# List of entity types.  This defines in particular the order in which
# the types must be restored.
entitytypes = [
    'user',
    'grouping',
    'rule',
    'publicStep',
    'facility',
    'instrument',
    'parameterType',
    'investigationType',
    'sampleType',
    'datasetType',
    'datafileFormat',
    'facilityCycle',
    'application',
    'investigation',
    'study',
    'sample',
    'dataset',
    'datafile',
    'relatedDatafile',
    'dataCollection',
    'job',
]

def entity2dict(obj, keyindex):
    """Convert an entity object to a dict."""
    d = {}

    for attr in obj.InstAttr:
        if attr == 'id':
            continue
        v = getattr(obj, attr, None)
        if v is None:
            continue
        elif isinstance(v, bool):
            pass
        elif isinstance(v, long) or isinstance(v, int):
            v = int(v)
        elif isinstance(v, datetime.datetime):
            if v.tzinfo is not None and v.tzinfo.utcoffset(v) is not None:
                # v has timezone info, assume v.isoformat() to have a
                # valid timezone suffix.
                v = v.isoformat()
            else:
                # v has no timezone info, assume it to be UTC, append
                # the corresponding timezone suffix.
                v = v.isoformat() + 'Z'
        else:
            try:
                v = str(v)
            except UnicodeError:
                v = unicode(v)
        d[attr] = v

    for attr in obj.InstRel:
        o = getattr(obj, attr, None)
        if o is not None:
            d[attr] = o.getUniqueKey(autoget=False, keyindex=keyindex)

    for attr in obj.InstMRel:
        if len(getattr(obj, attr)) > 0:
            d[attr] = []
            for o in sorted(getattr(obj, attr), 
                            key=icat.entity.Entity.__sortkey__):
                d[attr].append(entity2dict(o, keyindex=keyindex))

    return d


def dict2entity(client, insttypemap, d, objtype, objindex):
    """Create an entity object from a dict of attributes."""
    obj = client.new(objtype)
    mreltypes = None
    for attr in d:
        if attr in obj.InstAttr:
            setattr(obj, attr, d[attr])
        elif attr in obj.InstRel:
            robj = client.searchUniqueKey(d[attr], objindex)
            setattr(obj, attr, robj)
        elif attr in obj.InstMRel:
            if mreltypes is None:
                info = client.getEntityInfo(obj.BeanName)
                mreltypes = { f.name:insttypemap[f.type] 
                              for f in info.fields if f.relType == "MANY" }
            for rd in d[attr]:
                robj = dict2entity(client, insttypemap, 
                                   rd, mreltypes[attr], objindex)
                getattr(obj, attr).append(robj)
        else:
            raise ValueError("invalid attribute '%s' in '%s'" 
                             % (attr, objtype))
    return obj


# ------------------------------------------------------------
# YAMLDumpFileReader
# ------------------------------------------------------------

class YAMLDumpFileReader(object):
    """Backend for icatrestore.py to read a YAML dump file."""

    def __init__(self, client, infile):
        self.client = client
        self.infile = infile
        self.insttypemap = { c.BeanName:t 
                             for t,c in self.client.typemap.iteritems() }

    def getdata(self):
        """Iterate over the data chunks in the dump file.
        """
        # yaml.load_all() returns a generator that yield one chunk
        # (YAML document) from the file in each iteration.
        return yaml.load_all(self.infile)

    def getobjs(self, data, objindex):
        """Iterate over the objects in a data chunk.

        Yield a new entity object in each iteration.  The object is
        initialized from the data, but not yet created at the client.
        """
        for name in entitytypes:
            if name in data:
                for key, d in data[name].iteritems():
                    obj = dict2entity(self.client, self.insttypemap, 
                                      d, name, objindex)
                    yield key, obj


# ------------------------------------------------------------
# YAMLDumpFileWriter
# ------------------------------------------------------------

class YAMLDumpFileWriter(object):
    """Backend for icatdump.py to write a YAML dump file."""

    def __init__(self, outfile):
        self.outfile = outfile
        self.data = {}

    def head(self, service, apiversion):
        """Write a header with some meta information to the dump file."""
        dateformat = "%a, %d %b %Y %H:%M:%S +0000"
        date = datetime.datetime.utcnow().strftime(dateformat)
        head = """%%YAML 1.1
# Date: %s
# Service: %s
# ICAT-API: %s
# Generator: icatdump (python-icat %s)
""" % (date, service, apiversion, icat.__version__)
        self.outfile.write(head)

    def startdata(self):
        """Start a new data chunk.

        If the current chunk contains any data, write it to the dump
        file.
        """
        if self.data:
            yaml.dump(self.data, self.outfile, 
                      default_flow_style=False, explicit_start=True)
        self.data = {}

    def add(self, tag, key, obj, keyindex):
        """Add an entity object to the current data chunk."""
        if tag not in entitytypes:
            raise ValueError("Unknown entity type '%s'" % tag)
        if tag not in self.data:
            self.data[tag] = {}
        self.data[tag][key] = entity2dict(obj, keyindex)

    def finalize(self):
        """Finalize the dump file."""
        self.startdata()
