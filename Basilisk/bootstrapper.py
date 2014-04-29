from PySide.QtGui import QApplication
from locator import view_locator
from binder import bind
import sys


def create_app(view_model_cls, args = sys.argv):
    ''' Create an application with shell using the `view_model` '''
    app = QApplication(args)
    vm = view_model_cls()
    v = view_locator(vm)
    bind(vm, v)
    v.show()
    app.exec_()
