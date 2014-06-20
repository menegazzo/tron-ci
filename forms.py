from wtforms import Form
from wtforms.fields.core import StringField
from wtforms.validators import ValidationError


#===================================================================================================
# CronValidator
#===================================================================================================
class CronValidator(object):
    
    def __init__(self, min_value=None, max_value=None):
        self._min = min_value
        self._max = max_value
    

    def _Validate(self, value):
        value = int(value)
        if self._min is not None and value < self._min:
            raise ValueError()

        if self._max is not None and value > self._max:
            raise ValueError()

        return value


    def __call__(self, form, field, message=None):
        data = field.data
        if data is not None and data.strip():
            
            try:
                # Let's split numerator and denominator.
                result = data.split('/')
                if len(result) == 1:
                    numerator, denominator = result[0], None

                elif len(result) == 2:
                    numerator, denominator = result

                else:
                    raise SyntaxError()

                # Checking numerator.
                result = numerator.split('-')
                if len(result) == 1:
                    value = result[0]
                    if value != '*':
                        value = self._Validate(value)

                elif len(result) == 2:
                    min_value = self._Validate(result[0])
                    max_value = self._Validate(result[1])
                    if min_value >= max_value:
                        raise ValueError()

                else:
                    raise SyntaxError()

                # Checking denominator.
                if denominator is not None:
                    self._Validate(denominator)

            except:
                raise ValidationError(
                    '%s field has an error. Check current syntax and if values are within range %d-%d.' % (
                        field.name.title(),
                        self._min,
                        self._max,
                ))


#===================================================================================================
# DOWCronValidator
#===================================================================================================
class DOWCronValidator(CronValidator):

    _DOW = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    
    def __init__(self):
        CronValidator.__init__(self, 0, 6)


    def _Validate(self, value):
        if value in self._DOW:
            value = self._DOW.index(value)
        return CronValidator._Validate(self, value)


#===================================================================================================
# JobForm
#===================================================================================================
class JobForm(Form):

    minute = StringField('Minute', [CronValidator(0, 59)])
    hour = StringField('Hour', [CronValidator(0, 23)])
    day_of_week = StringField('Day of week', [DOWCronValidator()])
    week = StringField('Week', [CronValidator(1, 53)])
    day = StringField('Day', [CronValidator(1, 31)])
    month = StringField('Month', [CronValidator(1, 12)])
