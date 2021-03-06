"""Miscellany of text-munging functions.
"""
import string, types
def stringyString(object, indentation=''):
    """Expansive string formatting for sequence types.
    list.__str__ and dict.__str__ use repr() to display their
    elements.  This function also turns these sequence types
    into strings, but uses str() on their elements instead.
    Sequence elements are also displayed on seperate lines,
    and nested sequences have nested indentation.
    """
    braces = ''
    sl = []
    if type(object) is types.DictType:
        braces = '{}'
        for key, value in object.items():
            value = stringyString(value, indentation + '   ')
            if isMultiline(value):
                if endsInNewline(value):
                    value = value[:-len('\n')]
                sl.append("%s %s:\n%s" % (indentation, key, value))
            else:
                sl.append("%s %s: %s" % (indentation, key,
                                         value[len(indentation) + 3:]))
    elif type(object) in (types.TupleType, types.ListType):
        if type(object) is types.TupleType:
            braces = '()'
        else:
            braces = '[]'
        for element in object:
            element = stringyString(element, indentation + ' ')
            sl.append(string.rstrip(element) + ',')
    else:
        sl[:] = map(lambda s, i=indentation: i+s,
                    string.split(str(object),'\n'))
    if not sl:
        sl.append(indentation)
    if braces:
        sl[0] = indentation + braces[0] + sl[0][len(indentation) + 1:]
        sl[-1] = sl[-1] + braces[-1]
    s = string.join(sl, "\n")
    if isMultiline(s) and not endsInNewline(s):
        s = s + '\n'
    return s
def isMultiline(s):
    """Returns True if this string has a newline in it."""
    return (string.find(s, '\n') != -1)
def endsInNewline(s):
    """Returns True if this string ends in a newline."""
    return (s[-len('\n'):] == '\n')
def docstringLStrip(docstring):
    """Gets rid of unsightly lefthand docstring whitespace residue.
    You'd think someone would have done this already, but apparently
    not in 1.5.2.
    BUT since we're all using Python 2.1 now, use L{inspect.getdoc}
    instead.  I{This function should go away soon.}
    """
    if not docstring:
        return docstring
    docstring = string.replace(docstring, '\t', ' ' * 8)
    lines = string.split(docstring,'\n')
    leading = 0
    for l in xrange(1,len(lines)):
        line = lines[l]
        if string.strip(line):
            while 1:
                if line[leading] == ' ':
                    leading = leading + 1
                else:
                    break
        if leading:
            break
    outlines = lines[0:1]
    for l in xrange(1,len(lines)):
        outlines.append(lines[l][leading:])
    return string.join(outlines, '\n')
def greedyWrap(inString, width=80):
    """Given a string and a column width, return a list of lines.
    Caveat: I'm use a stupid greedy word-wrapping
    algorythm.  I won't put two spaces at the end
    of a sentence.  I don't do full justification.
    And no, I've never even *heard* of hypenation.
    """
    outLines = []
    if inString.find('\n\n') >= 0:
        paragraphs = string.split(inString, '\n\n')
        for para in paragraphs:
            outLines.extend(greedyWrap(para) + [''])
        return outLines
    inWords = string.split(inString)
    column = 0
    ptr_line = 0
    while inWords:
        column = column + len(inWords[ptr_line])
        ptr_line = ptr_line + 1
        if (column > width):
            if ptr_line == 1:
                pass
            else:
                ptr_line = ptr_line - 1
            (l, inWords) = (inWords[0:ptr_line], inWords[ptr_line:])
            outLines.append(string.join(l,' '))
            ptr_line = 0
            column = 0
        elif not (len(inWords) > ptr_line):
            outLines.append(string.join(inWords, ' '))
            del inWords[:]
        else:
            column = column + 1
    return outLines
wordWrap = greedyWrap
def removeLeadingBlanks(lines):
    ret = []
    for line in lines:
        if ret or line.strip():
            ret.append(line)
    return ret
def removeLeadingTrailingBlanks(s):
    lines = removeLeadingBlanks(s.split('\n'))
    lines.reverse()
    lines = removeLeadingBlanks(lines)
    lines.reverse()
    return '\n'.join(lines)+'\n'
def splitQuoted(s):
    """Like string.split, but don't break substrings inside quotes.
    >>> splitQuoted('the \"hairy monkey\" likes pie')
    ['the', 'hairy monkey', 'likes', 'pie']
    Another one of those \"someone must have a better solution for
    this\" things.  This implementation is a VERY DUMB hack done too
    quickly.
    """
    out = []
    quot = None
    phrase = None
    for word in s.split():
        if phrase is None:
            if word and (word[0] in ("\"", "'")):
                quot = word[0]
                word = word[1:]
                phrase = []
        if phrase is None:
            out.append(word)
        else:
            if word and (word[-1] == quot):
                word = word[:-1]
                phrase.append(word)
                out.append(" ".join(phrase))
                phrase = None
            else:
                phrase.append(word)
    return out
def strFile(p, f, caseSensitive=True):
    """Find whether string p occurs in a read()able object f
    @rtype: C{bool}
    """
    buf = ""
    buf_len = max(len(p), 2**2**2**2)
    if not caseSensitive:
        p = p.lower()
    while 1:
        r = f.read(buf_len-len(p))
        if not caseSensitive:
            r = r.lower()
        bytes_read = len(r)
        if bytes_read == 0:
            return False
        l = len(buf)+bytes_read-buf_len
        if l <= 0:
            buf = buf + r
        else:
            buf = buf[l:] + r
        if buf.find(p) != -1:
            return True
