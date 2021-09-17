# -*- coding: utf-8 -*-
#
# main.py

# application entry point.Runs mainActivity.py
#

import traceback


# Указываем пользоваться системным методом ввода, использующимся на
# платформе, в которой запущенно приложение.
#Config.set('graphics', 'width', '690')
#Config.set('graphics', 'height', '700')
#Config.set('graphics', 'multisamples', '0')
#Config.set('kivy', 'keyboard_mode', 'systemandmulti')

def main():
    __version__ = "1.1.1"
    app = None
    try:
        from mainActivity import MainActivity
        app = MainActivity()
        app.run()
    except Exception as exc:
        # TODO add loggeк
        print(traceback.format_exc())


if __name__ == '__main__':
    main()
