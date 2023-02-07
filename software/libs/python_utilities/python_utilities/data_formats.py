def ReadKeyValueDataFile(string, header_char='#', delim = ':'):
    '''
    Breakup lines into key value pairs
    Any value not in a key value pair and has none white space characters is added to a list
    '''
    lines = string.split("\n")
    key_value = list()
    data = list()
    for line in lines:
        line = line.strip()
        if len(line) == 0:
            continue # skip line
        if line[0] == header_char:
            split = line.strip().split(delim)
            key = split[0].lstrip(header_char).strip()
            value = delim.join([pt.strip() for pt in split[1:]])
            key_value.append((key, value))
        else:
            data.append(line)
    return key_value, data

def ReadHpFileFormat(data):
    '''
    HP Data file is a new line delimited list.
    Header:
        ```
        NPoints-1
        Step Size
        ??
        ```
    returns: x, y array
    '''
    import numpy as np
    npoints, step_size, _ = data[:3]
    npoints = int(npoints)
    step_size = float(step_size)
    y = np.array(data[3:], dtype=float)
    assert len(y) == npoints+1
    return [pt*step_size for pt in range(len(y))], y


