def get_testfunc(obj):
    if hasattr(obj, 'hypothesis'):
        return obj.hypothesis.inner_test, True
    return obj, False
