try:
    import trio
except ImportError:
    trio = None

try:
    import curio
except ImportError:
    curio = None


def get_testfunc(obj):
    if hasattr(obj, 'hypothesis'):
        return obj.hypothesis.inner_test, True
    return obj, False
