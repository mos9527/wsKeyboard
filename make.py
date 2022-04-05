original = open('wskeyboard.py',encoding='utf-8').read()
web      = open('index.html',encoding='utf-8').read()
combined = f"""page='''{web}'''
"""  + original
open('build.py','w',encoding='utf-8').write(combined)
import os
os.system('''pyinstaller --icon NONE --onefile ./build.py''')
os.system('''copy dist/build.exe wskeyboard.exe''')