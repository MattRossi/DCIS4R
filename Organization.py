from DCA import DCAUtils, DCAPostFormatter
from DCI import DCIUtils, DCIPostFormatter
import enum

class Orgs(enum.Enum):
    def __init__(self, utils, formatter):
        self.utils = utils
        self.formatter = formatter

    DCI = DCIUtils, DCIPostFormatter
    DCA = DCAUtils, DCAPostFormatter
