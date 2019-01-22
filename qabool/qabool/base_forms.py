from crispy_forms.helper import FormHelper


class BaseCrispyForm:

    def __init__(self, *args, **kwargs):
        super(BaseCrispyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'col-lg-4 col-md-5 col-xs-5'
        self.helper.field_class = 'col-lg-8 col-md-7 col-xs-7'


class BaseCrispySearchForm(BaseCrispyForm):

    def __init__(self, *args, **kwargs):
        super(BaseCrispySearchForm, self).__init__(*args, **kwargs)
        self.helper.form_method = 'get'
