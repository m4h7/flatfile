from .column import MetadataColumn
from .metadata import Metadata

def metadata_parse(s):
    md = Metadata()
    lines = s.splitlines()
    for line in lines:
        cstart = line.find('#')
        if cstart != -1:
            line = line[:cstart]
        line = line.strip()
        if line == "":
            continue
        items = line.split(' ')
        if items[0] == 'column':
            name = items[1]
            type_ = items[2]
            meaning = None
            if len(items) > 3:
                meaning = items[3]
            md.add_column(MetadataColumn(name, type_, meaning))
        elif items[0] == 'checksum':
            checksum_type = items[1]
            md.set_checksum(checksum_type)
        else:
            raise Exception('unknown line {}'.format(line))
    md.finalize()
    return md
