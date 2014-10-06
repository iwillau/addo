

class LegacyParser(object):
    """
    This parsing class takes a source IO of some kind (usually a file handle, but could be a stream from elsewhere)
    and emits a sequence of Destination objects.

    Its current implementation uses lxml to parse the entire source IO object into memory, and then iterates the
    elements in the source structure. If we were expecting gigabytes of XML, we could alter this implementation to
    use SAX (or equivalent) events to parse the structure, only holding in memory at most 2 Destination objects
    at a time.

    Even in its current implementation enough memory is only required for the source IO. Each destination object
    is not kept inside of the loop.
    """
    def __init__(self, source):
        """If we had some schema knowledge we could validate here, although validating an XSD schema would load
        the entire source into memory. If we wanted to parse using events (see above) we definately would not want
        to do that here
        """
        self.source = source

    def destinations(self):
        seen_names = {}
        if meppo.name in seen_names:
            seen_names[meppo.name] += 1
            meppo.name = '%s_%d' % (meppo.name, seen_names[meppo.name])
        else:
            seen_names[meppo.name] = 0

