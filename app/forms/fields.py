"""Custom form fields for FRacker."""
from decimal import Decimal, InvalidOperation
from wtforms import DecimalField


class MoneyField(DecimalField):
    """
    A DecimalField that accepts comma-formatted numbers.
    Strips commas and currency symbols before validation.
    Examples: "12,234.44" -> 12234.44, "$1,000" -> 1000
    """

    def process_formdata(self, valuelist):
        if valuelist:
            # Get the raw value
            raw_value = valuelist[0]
            # Strip whitespace, dollar signs, and commas
            cleaned = raw_value.strip().replace('$', '').replace(',', '')
            if cleaned:
                try:
                    self.data = Decimal(cleaned)
                except InvalidOperation:
                    self.data = None
                    raise ValueError(self.gettext('Not a valid decimal value.'))
            else:
                self.data = None
        else:
            self.data = None
