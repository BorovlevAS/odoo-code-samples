from .monkeypatches._monkeypatch_aep import _get_patchable_methods


def _patch_method(cls, method_name, func):
    origin_method_name = f"_origin_{method_name}"
    if hasattr(cls, origin_method_name):
        return
    origin_method = getattr(cls, method_name)
    setattr(cls, origin_method_name, origin_method)
    setattr(cls, method_name, func)


def _unpatch_method(cls, method_name):
    origin_method_name = f"_origin_{method_name}"
    if not hasattr(cls, origin_method_name):
        return

    origin_method = getattr(cls, origin_method_name)
    setattr(cls, method_name, origin_method)
    delattr(cls, origin_method_name)


def _patch_methods():
    methods_list = _get_patchable_methods()
    for method_struct in methods_list:
        _patch_method(
            method_struct["class"],
            method_struct["method_name"],
            method_struct["new_method"],
        )


def _unpatch_methods():
    methods_list = _get_patchable_methods()
    for method_struct in methods_list:
        _unpatch_method(
            method_struct["class"],
            method_struct["method_name"],
        )


def post_init_hook(cr, registry):
    _patch_methods()


def post_load_hook():
    _patch_methods()


def uninstall_hook(cr, registry):
    _unpatch_methods()
