from classytags.arguments import Argument
from classytags.core import Options
from classytags.helpers import AsTag


class BaseAllBoundariesTag(AsTag):
    options = Options(
        'as',
        Argument('varname', required=True, resolve=False),
    )

    def get_value(self, context):
        raise NotImplementedError('Implement get_value()')
