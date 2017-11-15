from factory import Faker, Iterator, PostGenerationMethodCall, SubFactory
from factory.django import DjangoModelFactory
from django.utils.timezone import get_default_timezone

from apps.data.factories import EntryFactory, RepositoryFactory
from . import models

PIXELER_PASSWORD = 'SurferRosa1988'


class SpeciesFactory(DjangoModelFactory):

    name = Faker('word')
    reference = SubFactory(EntryFactory)
    repository = SubFactory(RepositoryFactory)
    description = Faker('text', max_nb_chars=300)

    class Meta:
        model = 'core.Species'
        django_get_or_create = ('name', )


class StrainFactory(DjangoModelFactory):

    name = Faker('word')
    description = Faker('text', max_nb_chars=300)
    species = SubFactory(SpeciesFactory)
    reference = SubFactory(EntryFactory)

    class Meta:
        model = 'core.Strain'
        django_get_or_create = ('name', )


class OmicsUnitTypeFactory(DjangoModelFactory):

    name = Faker('word')
    description = Faker('text', max_nb_chars=300)

    class Meta:
        model = 'core.OmicsUnitType'
        django_get_or_create = ('name', )


class OmicsUnitFactory(DjangoModelFactory):

    reference = SubFactory(EntryFactory)
    strain = SubFactory(StrainFactory)
    type = SubFactory(OmicsUnitTypeFactory)
    status = Iterator(s[0] for s in models.OmicsUnit.STATUS_CHOICES)

    class Meta:
        model = 'core.OmicsUnit'
        django_get_or_create = ('reference', 'strain')


class PixelerFactory(DjangoModelFactory):

    username = Faker('user_name')
    password = PostGenerationMethodCall(
        'set_password', PIXELER_PASSWORD
    )
    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    is_active = Faker('pybool')
    is_staff = Faker('pybool')
    is_superuser = Faker('pybool')
    date_joined = Faker('date_time_this_decade', tzinfo=get_default_timezone())
    last_login = Faker('date_time_this_decade', tzinfo=get_default_timezone())

    class Meta:
        model = 'core.Pixeler'
        django_get_or_create = ('username',)


class OmicsAreaFactory(DjangoModelFactory):

    name = Faker('word')
    description = Faker('text', max_nb_chars=300)

    class Meta:
        model = 'core.OmicsArea'
        django_get_or_create = ('name',)


class ExperimentFactory(DjangoModelFactory):

    omics_area = SubFactory(OmicsAreaFactory)
    description = Faker('text', max_nb_chars=300)
    created_at = Faker('datetime')
    released_at = Faker('datetime')
    saved_at = Faker('datetime')

    class Meta:
        model = 'core.Experiment'
        django_get_or_create = ('omics_area', 'created_at')


class AnalysisFactory(DjangoModelFactory):

    description = Faker('text', max_nb_chars=300)
    pixeler = SubFactory(PixelerFactory)
    notebook = Faker('file_path', depth=1, category=None, extension=None)
    secondary_data = Faker('file_path', depth=1, category=None, extension=None)
    created_at = Faker('date')
    saved_at = Faker('date')

    class Meta:
        model = 'core.Analysis'
        django_get_or_create = ('secondary_data', 'pixeler',)


class PixelSetFactory(DjangoModelFactory):

    pixels_file = Faker('file_path', depth=1, category=None, extension=None)
    description = Faker('text', max_nb_chars=300)
    analysis = SubFactory(AnalysisFactory)

    class Meta:
        model = 'core.PixelSet'


class PixelFactory(DjangoModelFactory):

    value = Faker('pyfloat')
    quality_score = Faker('pyfloat', left_digits=0)
    omics_unit = SubFactory(OmicsUnitFactory)
    pixel_set = SubFactory(PixelSetFactory)

    class Meta:
        model = 'core.Pixel'
        django_get_or_create = ('value', 'omics_unit', 'pixel_set')
