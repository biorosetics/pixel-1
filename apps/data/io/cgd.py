import pandas

from hashlib import blake2b

from ..models import Entry, Repository


class ChrFeatureParser(object):
    """
    Expected columns:

    (A) 1.  Feature name (mandatory); this is the primary systematic name,
        if available
    (B) 2.  Gene name (locus name)
    (C) 3.  Aliases (multiples separated by |)
    (D) 4.  Feature type
    (E) 5.  Chromosome
    (F) 6.  Start Coordinate
    (G) 7.  Stop Coordinate
    (H) 8.  Strand
    (I) 9.  Primary CGDID
    (J) 10. Secondary CGDID (if any)
    (K) 11. Description
    (L) 12. Date Created
    (M) 13. Sequence Coordinate Version Date (if any)
    (N) 14. Blank
    (O) 15. Blank
    (P) 16. Date of gene name reservation (if any).
    (Q) 17. Has the reserved gene name become the standard name? (Y/N)
    (R) 18. Name of S. cerevisiae ortholog(s) (multiples separated by |)
    """

    def __init__(self, file_path):

        self.file_path = file_path
        self.features = None
        self.entries = {
            'new': [],
            'update': [],
        }

    def parse(self):

        headers = (
            'name',  # A
            'locus',  # B
            'aliases',  # C
            'type',  # D
            'chromosome',  # E
            'start',  # F
            'stop',  # G
            'strand',  # H
            'cgdid',  # I
            'cgdid_2',  # J
            'description',  # K
            'created',  # L
            'crd_versionned',  # M
            'blk_1',  # N
            'blk_2',  # O
            'reserved',  # P
            'is_standard',  # Q
            'orthologs',  # R
        )
        self.features = pandas.read_table(
            self.file_path,
            header=None,
            names=headers,
            skiprows=8
        )

    def _to_entries(self, ignore_aliases):

        if self.features is None:
            return

        repository, _ = Repository.objects.get_or_create(name='CGD')
        root_url = 'http://www.candidagenome.org/cgi-bin/locus.pl?dbid='
        known_entries = repository.entries.values_list('identifier', flat=True)
        entries = dict(update=[], new=[])

        for idx, feature in self.features.iterrows():
            url = '{}{}'.format(root_url, feature['cgdid'])
            aliases = []

            if not pandas.isna(feature['aliases']) and not ignore_aliases:
                aliases = feature['aliases'].split('|')

            for identifier in (feature['name'], *aliases):

                # The Entry primary key is precomputed given an identifier and
                # a repository. By doing so, we will be able to create a set()
                # to remove duplicates potentially generated by aliases.
                pk = blake2b(
                    bytes(
                        '/'.join((identifier, repository.pk.hex)),
                        encoding='utf8'
                    ),
                    digest_size=16
                ).hexdigest()

                entry = Entry(
                    pk=pk,
                    identifier=identifier,
                    description=feature['description'],
                    url=url,
                    repository=repository,
                )

                if identifier in known_entries:
                    entries['update'].append(entry)
                else:
                    entries['new'].append(entry)

        self.entries['new'] = list(set(entries.get('new')))
        self.entries['update'] = list(set(entries.get('update')))

    def save(self, ignore_aliases=True):

        self._to_entries(ignore_aliases=ignore_aliases)

        # Create new entries
        Entry.objects.bulk_create(self.entries['new'], batch_size=500)

        # Update old entries
        for updated_entry in self.entries['update']:
            entry = Entry.objects.get(
                identifier=updated_entry.identifier,
                repository=updated_entry.repository
            )
            entry.description = updated_entry.description
            entry.save(update_fields=['description', ])
