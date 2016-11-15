import struct

VALID_TYPES = ['u32le', 'u64le', 'u128le', 'string']
VALID_COMPRESSION = ['lz4', 'none']
VALID_CHECKSUM = ['crc32', 'none']

class Metadata:
    def __init__(self):
        self.checksum = None
        self.columns = []
        self._name = {}

    def add_column(self, c):
        for x in self.columns:
            if c.name == x.name:
                raise Exception('Duplicate name {}'.format(c.name))
        self.columns.append(c)

    def set_checksum(self, checksum_type):
        if checksum_type in VALID_TYPES:
            self.checksum = checksum_type

    def finalize(self):
        nonstrings = []
        strings = []
        for c in self.columns:
            if c.type_ == 'string':
                strings.append(c)
            else:
                nonstrings.append(c)
        strings.sort(key=lambda x: x.name)
        nonstrings.sort(key=lambda x: x.name)
        self.columns = nonstrings + strings
        offset = 0
        for c in self.columns:
            c.offset = offset
            if c.type_ == 'u32le':
                offset += 4
            elif c.type_ == 'u64le':
                offset += 8
            elif c.type_ == 'u128le':
                offset += 16
            elif c.type_ == 'string':
                offset += 4
            else:
                assert not "unknown type"

    def write(self, kv, fobj):
        append_values = []
        for c in self.columns:
            if c.name in kv:
                if c.type_ == 'string':
                    s = kv[c.name]
                    b = s.encode('utf-8')
                    append_values.append(b)
                    v = len(b)
                else:
                    v = kv[c.name]
                fobj.write(c.encode_uint(v))
        for b in append_values:
            fobj.write(b)
        for k in kv.keys():
            found = False
            for c in self.columns:
                if c.name == k:
                    found = True
                    break
            if not found:
                print('key not in metadata: "{}"'.format(k))
                print('known keys:')
                for c in self.columns:
                    print('"{}" -> {}'.format(c.name, c.name == k))
                print('-----------')
                raise Exception('key not in metadata: {}'.format(k))

    def read(self, f):
        fixed_size = 0
        fixed_fmt = '<'
        for c in self.columns:
            if c.type_ == 'u32le' or c.type_ == 'string':
                fixed_size += 4
                fixed_fmt += 'I'
            elif c.type_ == 'u64le':
                fixed_size += 8
                fixed_fmt += 'Q'
            elif c.type_ == 'u128le':
                fixed_size += 16
                # TODO
            else:
                raise Exception('unknown column type')
        buf = f.read(fixed_size)
        print (fixed_fmt)
        values = struct.unpack(fixed_fmt, buf)
        r = {}
        readlist = []
        for i, c in enumerate(self.columns):
            if c.type_ == 'u32le':
                r[c.name] = values[i]
            elif c.type_ == 'string':
                readlist.append((c.name, values[i]))
            elif c.type_ == 'u64le':
                r[c.name] = values[i]
            else:
                raise Exception('unk col type')
        for col_name, size in readlist:
            b = f.read(size)
            s = b.decode('utf-8')
            r[col_name] = s
        return r
