import logging


class Destination(object):
    """The container class for all of the Destination data.

    The metadata are object attributes deliberately, so as to mimic pulling/pushing the data via an ORM.
    """

    def __init__(self, source, asset_id, name, title, content, children, parents):
        self.log = logging.getLogger('addo.destination.%s' % name)
        self.source = source
        self.asset_id = asset_id
        self.name = name
        self.title = title
        self.content = content
        self._children_list = children
        self._parent_list = parents

    def get_content(self, *path):
        current = self.content
        for path_location in path:
            if current and path_location in current:
                current = current[path_location]
            else:
                current = None
        return current

    def children(self):
        for child_name in self._children_list:
            if child_name in self.source.metadata:
                yield self.source.metadata[child_name]
            else:
                self.log.warn('Source does not know of child %s' % child_name)

    def number_children(self):
        return len(self._children_list)

    def parents(self):
        for parent_name in self._parent_list:
            if parent_name in self.source.metadata:
                yield self.source.metadata[parent_name]
            else:
                self.log.warn('Source does not know of parent %s' % parent_name)

    def number_parents(self):
        return len(self._parent_list)
