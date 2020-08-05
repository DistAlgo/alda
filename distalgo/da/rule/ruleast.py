from da.compiler.dast import DistNode, NameScope, NamedVar
from pprint import pprint

class DARules(DistNode): 
    _fields = []

    def __init__(self, *args):
        """Populate fields named in "fields" with values in *args."""
        # print('fields:', self._fields)
        # print('args:', args)
        # super().__init__(parent,ast)
        assert(len(self._fields) == len(args))
        for f, a in zip(self._fields, args):
            setattr(self, f, a)

class LogicVar (DARules):
    _fields = ['name']

class Assertion (DARules):
    _fields = ['pred', 'args']

    @property
    def arity(self):
        return len(self.args)

class Rule(DARules):
    _fields = ['concl', 'hypos']

    @property
    def cpred(self):
        return self.concl.pred

    @property
    def hpreds(self):
        return {c.pred for c in self.hypos}

    def get_arity(self, pred):
        for c in [self.concl] + self.hypos:
            if pred == c.pred:
                return c.arity
        return None

class RuleSet(NameScope):
    _fields = NameScope._fields+['decls', 'rules']
    def __init__(self, parent=None, ast=None):
        super().__init__(parent, ast)
        self.decls = ""
        self.rules = []
        self.filename = ""
        self._index = str(RuleSet._index)

    @property
    def unique_name(self):
        return type(self).__name__ + self._index + "_" + self.decls

    @property
    def cpreds(self):
        return {r.cpred for r in self.rules}

    @property
    def hpreds(self):
        return set.union(*[r.hpreds for r in self.rules])

    @property
    def base(self):
        return self.hpreds - self.cpreds

    @property
    def derived(self):
        return self.cpreds

    @property
    def bounded_base(self):
        return {x for x in self.base if x.name not in self._names}

    @property
    def unbounded_base(self):
        return {x for x in self.base if x.name in self._names}

    @property
    def bounded_derived(self):
        return {x for x in self.derived if x.name not in self._names}

    @property
    def unbounded_derived(self):
        return {x for x in self.derived if x.name in self._names}

    def add_name(self, name):
        """Override the add_name function in Namescope, 
        Find names not only within current scope, but from parent scope
        """
        obj = self.find_name(name)
        if obj is not None:
            return obj
        else:
            obj = NamedVar(name=name)
            self._names[name] = obj
            return obj

    def get_arity(self, pred):
        """get the arity of predicate pred
        """
        for r in self.rules:
            a = r.get_arity(pred)
            if a:
                return a
        return None

    def all_initialized_by(self, node):
        """ if all the bounded variables assigned by the ast node.
        """
        for b in self.bounded_base | self.bounded_derived:
            if not (b.last_assignment_before(node) or b.is_assigned_in(node)):
                return False
        return True

