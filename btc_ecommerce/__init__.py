# btc_ecommerce package
import copy
from django.template.context import BaseContext

def patched_copy(self):
    # BaseContext() compiles safely as dict_ defaults to None
    duplicate = BaseContext()
    duplicate.__class__ = self.__class__
    # Manually copy instance dictionary attributes
    duplicate.__dict__.update(self.__dict__)
    # Perform a shallow copy of the dicts stack list
    duplicate.dicts = self.dicts[:]
    return duplicate

# Apply the patch to support Python 3.14+ compatibility
BaseContext.__copy__ = patched_copy
