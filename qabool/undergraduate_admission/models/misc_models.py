from django.db import models
from django.utils import translation
from django.utils.translation import ugettext_lazy as _


class Lookup(models.Model):
    lookup_type = models.CharField(max_length=20, null=True, blank=False, db_index=True)
    lookup_value_ar = models.CharField(max_length=100, null=True, blank=False)
    lookup_value_en = models.CharField(max_length=100, null=True, blank=False)
    show = models.BooleanField(verbose_name=_('Show'), default=True)
    display_order = models.PositiveSmallIntegerField(null=True, verbose_name=_('Display Order'))

    class Meta:
        verbose_name_plural = _('Admission: Look ups')
        ordering = ['lookup_type', '-display_order']

    @property
    def lookup_value(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.lookup_value_ar
        else:
            return self.lookup_value_en

    def __str__(self):
        return self.lookup_value

    @staticmethod
    def get_lookup_choices(lookup_type, add_dashes=True):
        try:
            choices = Lookup.objects.filter(
                show=True,
                lookup_type=lookup_type)

            ch = [(o.lookup_value_ar, str(o)) for o in choices]
            if add_dashes:
                ch.insert(0, ('', '---------'))

            return ch
        except:  # was OperationalError and happened when db doesn't exist yet but later changed it to general except to catch an weird exceptions like ProgrammingError
            return [('--', '--')]


class City(models.Model):
    city_name_ar = models.CharField(max_length=100, verbose_name=_('City Name Arabic'))
    city_name_en = models.CharField(max_length=100, verbose_name=_('City Name English'))
    show = models.BooleanField(verbose_name=_('Show'), default=True)
    display_order = models.PositiveSmallIntegerField(null=True, verbose_name=_('Display Order'))

    @property
    def city(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.city_name_ar
        else:
            return self.city_name_en

    def __str__(self):
        return self.city

    class Meta:
        ordering = ['-display_order']
        verbose_name_plural = _('Admission: Cities')


class Agreement(models.Model):
    class AgreementTypes:
        INITIAL = 'INITIAL'
        CONFIRMED = 'CONFIRMED'
        CONFIRMED_N = 'CONFIRMED-N'
        CONFIRMED_T = 'CONFIRMED-T'
        STUDENT_AGREEMENT_1 = 'STUDENT-AGREEMENT_1'
        STUDENT_AGREEMENT_2 = 'STUDENT-AGREEMENT_2'
        STUDENT_AGREEMENT_3 = 'STUDENT-AGREEMENT_3'
        STUDENT_AGREEMENT_4 = 'STUDENT-AGREEMENT_4'
        HOUSING_AGREEMENT = 'HOUSING-AGREEMENT'
        HOUSING_ROOMMATE_REQUEST_AGREEMENT = 'HOUSING-ROOMMATE-REQUEST-AGREEMENT'
        HOUSING_ROOMMATE_SEARCH_INSTRUCTIONS = 'HOUSING-ROOMMATE-SEARCH-INSTRUCTIONS'
        HOUSING_ROOMMATE_REQUEST_INSTRUCTIONS = 'HOUSING-ROOMMATE-REQUEST-INSTRUCTIONS'
        AWARENESS_WEEK_AGREEMENT = 'AWARENESS-WEEK-AGREEMENT'

        @classmethod
        def choices(cls):
            return (
                (cls.INITIAL, _('Initial agreements')),
                (cls.CONFIRMED, _('Confirmation agreements')),
                (cls.CONFIRMED_N, _('Confirmation agreements for None Saudi')),
                (cls.CONFIRMED_T, _('Confirmation agreements for Transfer students')),
                (cls.STUDENT_AGREEMENT_1, _('Student agreements 1')),
                (cls.STUDENT_AGREEMENT_2, _('Student agreements 2')),
                (cls.STUDENT_AGREEMENT_3, _('Student agreements 3')),
                (cls.STUDENT_AGREEMENT_4, _('Student agreements 4')),
                (cls.HOUSING_AGREEMENT, _('Student Housing: Initial agreements')),
                (cls.HOUSING_ROOMMATE_REQUEST_AGREEMENT, _('Student Housing: Request agreements')),
                (cls.HOUSING_ROOMMATE_SEARCH_INSTRUCTIONS, _('Student Housing: Search Instructions')),
                (cls.HOUSING_ROOMMATE_REQUEST_INSTRUCTIONS, _('Student Housing: Request Instructions')),
                (cls.AWARENESS_WEEK_AGREEMENT, _('Awareness week agreements')),
            )

    semester = models.ForeignKey(
        'AdmissionSemester',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name='agreements',
        verbose_name='Semester',
    )
    status = models.ForeignKey(
        'RegistrationStatusMessage',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name='status_messages',
        verbose_name='Status Message',
    )
    agreement_type = models.CharField(max_length=100, null=True, blank=False, verbose_name=_('Agreement Type'),
                                      choices=AgreementTypes.choices())
    agreement_text_ar = models.TextField(max_length=2000, verbose_name=_('Agreement Text (Arabic)'), blank=True,
                                         null=True)
    agreement_text_en = models.TextField(max_length=2000, verbose_name=_('Agreement Text (English)'), blank=True,
                                         null=True)
    show = models.BooleanField(verbose_name=_('Show'), default=True)

    class Meta:
        verbose_name_plural = _('Admission and Student Affairs: Agreements')

    @property
    def agreement(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.agreement_text_ar
        else:
            return self.agreement_text_en

    def __str__(self):
        return str(self.agreement_type)


# Auxiliary table in the database for BI reports
class Aux1To100(models.Model):
    counter = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Counter'))


# Important dates model for Qabool. It should display as list in the homepage sidebar.
class ImportantDateSidebar(models.Model):
    title_ar = models.CharField(max_length=200, verbose_name=_('Arabic Title'))
    title_en = models.CharField(max_length=200, verbose_name=_('English Title'))
    description_ar = models.CharField(max_length=300, null=True, verbose_name=_('Arabic Description'))
    description_en = models.CharField(max_length=300, null=True, verbose_name=_('English Description'))
    show = models.BooleanField(verbose_name=_('Show'), default=True)
    display_order = models.PositiveSmallIntegerField(null=True, verbose_name=_('Display Order'))

    @property
    def title(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.title_ar
        else:
            return self.title_en

    @property
    def description(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.description_ar
        else:
            return self.description_en

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['display_order']
        verbose_name_plural = _('Admission: Important Date Sidebar')
