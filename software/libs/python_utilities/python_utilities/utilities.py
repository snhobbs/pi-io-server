import numpy as np


def RegistersToBytes(registers):
  text = []
  for register in registers:
      text.append((register>>8)&0xff)
      text.append((register&0xff))
  return bytes(text)

def TransformBytesToDataType(dtype, data : bytes, byteorder="big"):
    if dtype == "string":
        if isinstance(data, bytes):
            return data.decode("utf-8")
        return "".join([chr(pt) for pt in data])

    signed = dtype[0] != "u"
    return int.from_bytes(data, byteorder=byteorder, signed=signed)

def bytes_to_int32(data, byteorder="big", endianness=None):
    return TransformBytesToDataType("int32", data, byteorder)

def average_vector(vectors):
    '''
    Takes a list of vectors and returns a list of the averaged vectors
    '''
    d = []
    for pt in zip(*list(vectors)):
        d.append(np.mean(pt))
    return d

def fit_exponential(x, y, p0=None):
    import scipy, math
    import numpy as np
    def fit_line(x, r, g):
        return r + g*x
    weights = ([1/abs(math.log(pt)) for pt in list(y)])
    fit, cov = scipy.optimize.curve_fit(fit_line, x, np.log(y), p0=p0, sigma=weights)
    r0=math.exp(fit[0])
    g = fit[1]
    return g, r0


def fit_line(x, y):
    import numpy as np
    polyfit = np.polynomial.polynomial.polyfit
    res = np.polyfit(x, y, 1, full=True)
    # res = polyfit(x, y, 1, full=True)
    terms, residual  = res[:2]
    assert len(terms) == 2
    if len(residual) == 0:
        residual = [[0]]
    assert len(residual) > 0
    return {"slope": terms[0], "intercept": terms[1], "residual": residual[0]}
