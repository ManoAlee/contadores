import PySimpleGUI as sg
import sys
print('PySimpleGUI version:', getattr(sg,'__version__','unknown'))
print('module file:', getattr(sg,'__file__','unknown'))
names = [n for n in dir(sg) if any(k in n for k in ('Text','Input','Window','Button','Tab'))]
print('Sample names:', names[:200])
print('Has Text attr?', hasattr(sg,'Text'))
print('Has Button attr?', hasattr(sg,'Button'))
