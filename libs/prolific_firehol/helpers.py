import decimal
import json


class DecimalEncoder(json.JSONEncoder):
    """
    A decoder that can be used to convert a decimal to a string.
    This is required as the standard library json dumps method is not able to handle
    decimal fields.
    """

    def default(self, value):
        """
        Converts a decimal to a string if ```value``` is a decimal. If ```values``` is
        not a decimal, then the default behaviour of the parent class is used.

        Args:
            value: the value to be converted as part of converting a dictionary to
                json.

        Returns:
            a string representation of the value provided.

        """
        if isinstance(value, decimal.Decimal):
            return str(value)
        return super().default(value)
