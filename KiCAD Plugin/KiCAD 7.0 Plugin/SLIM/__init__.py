#https://forum.kicad.info/t/howto-register-a-python-plugin-inside-pcbnew-tools-menu/5540/22
try:
    # Note the relative import!
    from .slim_layout_v1 import *
    # Instantiate and register to Pcbnew
    # text_by_date().register()
    moveSLIM().register()
    # moveSLIMDlg().register()
    distributeFootprints().register()
except Exception as e:
    import os
    plugin_dir = os.path.dirname(os.path.realpath(__file__))
    log_file = os.path.join(plugin_dir, 'SLIM.log')
    with open(log_file, 'w') as f:
        f.write(repr(e))

