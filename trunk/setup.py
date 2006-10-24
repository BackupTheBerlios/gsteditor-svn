from distutils.core import setup

from gsteditor import APPVERSION

setup(name='gsteditor', version=APPVERSION, 
        description='GStreamer Graphical Pipeline Editor',
        author='Brendan Howell', author_email='mute@howell-ersatz.com',
        url='http://gsteditor.wordpress.com',
        py_modules=['gsteditor', 'gsteditorcanvas', 'gsteditorelement',
                    'gstparamwin'],
        data_files=[('glade-sources', ['glade-sources/arrow-icon.png', 
                        'glade-sources/gsteditor.glade']),
                    ('', ['README', 'LICENSE'])]
        )