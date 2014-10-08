import logging
from lxml import etree
from addo.destination import Destination

log = logging.getLogger(__name__)


class LegacyTaxonomies(dict):
    """
    Parse the Taxonomy XML from the legacy CMS. This is a heirarchical set of XML data which links the different
    destinations together. It is used by the Destinations Parser to provide relational information to the Destination
    class.
    """
    INT_PROPERTIES = [
        'geo_id',
        'atlas_node_id',
        'ethyl_content_object_id',
    ]

    def __init__(self):
        self._sets = {}

    def parse_xml(self, source):
        """Iterates each taxonomy object in the source XML and parses it"""
        xml = etree.parse(source)
        for taxonomy_data in xml.findall('taxonomy'):
            self.parse_taxonomy_set(taxonomy_data)

    def parse_taxonomy_set(self, taxonomy_xml):
        """
        Recursively iterates all of the node object in the taxonomy.

        cPython has an inbuilt default recursion limit of 100. If we expect a taxonomy depth greater than that
        this code should be modified to parse via events instead.
        """

        set_name = taxonomy_xml.findtext('taxonomy_name')

        def _parse_node(parent_node, parents=None):
            """The actual recursion function (generator). This iterates all of the child nodes of the element passed.
            It yields the node data, and node keys as it finds. It keeps a few lists in memory to collate the
            child/parent information as it is being parsed
            """
            for node in parent_node.findall('node'):
                node_name = node.findtext('node_name')
                if node_name is None:
                    # We cannot proceed without a name
                    log.warn('Taxonomy Source has a node missing a node name')
                    continue
                node_key = node_name.strip().lower().replace(' ', '_')
                node_data = {
                    'name': node_name,
                    'parents': parents,
                    'children': [],
                }
                # capture the integer properties of the node
                for property in self.INT_PROPERTIES:
                    if property in node.attrib:
                        node_data[property] = int(node.get(property)) if len(node.get(property)) > 0 else None
                # Loop the children nodes
                parents.append(node_key)
                for child_key, child_data in _parse_node(node, parents[:]):
                    if child_data['parents'][-1] == node_key:
                        node_data['children'].append(child_key)
                    yield child_key, child_data
                parents.pop()

                yield node_key, node_data

        set_data = {key: data for key, data in _parse_node(taxonomy_xml, [])}
        self._sets[set_name] = [key for key in set_data.keys()]
        self.update(set_data)


class LegacyParser(object):
    """
    This parsing class takes a source IO of some kind (usually a file handle, but could be a stream from elsewhere)
    and emits a sequence of Destination objects.

    Its current implementation uses lxml to parse the entire source IO object into memory, and then iterates the
    elements in the source structure. If we were expecting gigabytes of XML, we could alter this implementation to
    use SAX (or equivalent) events to parse the structure, only holding in memory at most 2 Destination objects
    at a time.

    Even in its current implementation enough memory is only required for the source IO and a small dict for each
    destination. Each destination object is not kept inside of the loop.
    """

    def __init__(self, source, taxonomy=None):
        """If we had some schema knowledge we could validate here, although validating an XSD schema would load
        the entire source into memory. If we wanted to parse using events (see above) we definitely would not want
        to do that here
        """
        self.xml = etree.parse(source)
        self.taxonomy = LegacyTaxonomies()
        if taxonomy:
            self.taxonomy.parse_xml(taxonomy)
        # Fetch the dest metadata
        self.metadata = {}
        for destination_xml in self.xml.iter('destination'):
            title = destination_xml.get('title')
            if title is None or len(title) == 0:
                log.warn('Destination is missing the title attribute, or it is empty.')
                continue
            title = title.strip()
            title_ascii = destination_xml.get('title-ascii')
            if title_ascii is not None and len(title_ascii) > 0:
                name = destination_xml.get('title-ascii').lower().replace(' ', '_')
            else:
                name = title.lower().replace(' ', '_')
            metadata = {
                'title': title,
                'name': name,
                'asset_id': destination_xml.get('asset_id'),
            }
            self.metadata[name] = metadata

    def destinations(self):
        for destination_xml in self.xml.iter('destination'):
            title = destination_xml.get('title')
            if title is None or len(title) == 0:
                log.warn('Destination is missing the title attribute, or it is empty.')
                continue
            title = title.strip()
            title_ascii = destination_xml.get('title-ascii')
            if title_ascii is not None and len(title_ascii) > 0:
                name = destination_xml.get('title-ascii').lower().replace(' ', '_')
            else:
                name = title.lower().replace(' ', '_')
            metadata = self.metadata[name]  # Fetched from XML earlier.
            content = self._recursive_dict(destination_xml)[1]  # As it is a recursive function, it returns a set
            # Clean up the content a little
            self.cleanup_content(content)

            if name not in self.taxonomy:
                log.warn('%s in destinations cannot be found in the taxonomy' % name)
                children = []
                parents = []
            else:
                children = self.taxonomy[name]['children']
                parents = self.taxonomy[name]['parents']
            destination = Destination(source=self,
                                      content=content,
                                      children=children,
                                      parents=parents,
                                      **metadata)
            atlas_id = destination_xml.get('atlas_id')
            if atlas_id is not None and len(atlas_id.strip()) > 0:
                destination.atlas_id = int(atlas_id)
            yield destination

    def _recursive_dict(self, element):
        '''Recursively iterate an element and convert all of its members to a either a dict or a list
        '''
        child_data = map(self._recursive_dict, element)
        if len(child_data) == 0:
            if element.text is None:
                return element.tag, {}
            else:
                return element.tag, unicode(element.text.strip())

        lists = {}
        data = {}
        for tag_name, tag_data in child_data:
            if tag_name in data:
                if tag_name in lists:
                    lists[tag_name].append(tag_data)
                else:
                    lists[tag_name] = [data[tag_name], tag_data]
            else:
                data[tag_name] = tag_data
        data.update(lists)
        return element.tag, data

    def cleanup_content(self, content):
        if 'history' in content and len(content['history']) == 1:
            content['history'] = content['history']['history']
        if 'introductory' in content and len(content['introductory']) == 1 and \
                        'introduction' in content['introductory'] and len(content['introductory']['introduction']) == 1:
            content['introduction'] = content['introductory']['introduction']['overview']
            del(content['introductory'])
