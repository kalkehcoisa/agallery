from collections import OrderedDict
from wtforms_alchemy import ModelForm
from wtforms.fields import SubmitField


class OrderedSubmitForm(ModelForm):
    def __init__(self, *ag, **kw):
        super(OrderedSubmitForm, self).__init__(*ag, **kw)

    def __iter__(self):
        field_order = getattr(self.meta, 'field_order', None)
        if field_order:
            temp_fields = OrderedDict()
            for name in field_order:
                for fname, fval in self._fields.items():
                    if name == '*':
                        if fname not in field_order:
                            temp_fields[fname] = fval
                    else:
                        if fname == name:
                            temp_fields[fname] = fval
            self._fields = temp_fields
        return super(ModelForm, self).__iter__()

    submit = SubmitField(label='Submit')
