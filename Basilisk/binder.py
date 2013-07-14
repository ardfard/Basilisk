from PySide.QtCore import *
from PySide.QtGui import *
import GUI_helper
import inspect

class BindError(Exception):
    pass

_line_edit_settings = { str : (None, Qt.AlignLeft),
                        float : (QDoubleValidator(), Qt.AlignRight),
                        int : (QIntValidator(), Qt.AlignRight) ,
                        type(None) : (None, Qt.AlignLeft)}

def line_edit_binder(line_edit, property, obj):
    print type(obj)
    print dir(obj)
    init_val = getattr(obj,property)
    line_edit.setText(str(init_val))
    property_type = type(init_val)
    validator, alignment = _line_edit_settings[property_type]
    line_edit.setAlignment(alignment)
    if validator : line_edit.setValidator(validator)

    def on_text_edited(text):
        try:
            value = property_type(text)
        except ValueError:
            value = None
        setattr(obj, property, value)

    line_edit.textEdited.connect(on_text_edited)

    def on_vm_changed(sender, prop_name):
        if prop_name == property: 
            value = getattr(sender, property)
            if not line_edit.hasFocus():
                line_edit.setText(str(value))
        if prop_name == property+'_validity':
            validity = getattr(sender, property+'_validity')
            print validity
            GUI_helper.set_line_edit_validity(line_edit, validity)

    validity = getattr(obj, property+'_validity', None)
    if validity:
        GUI_helper.set_line_edit_validity(line_edit, validity)
    obj.property_changed.connect(on_vm_changed)

def check_box_binder(check_box, property, obj):
    init_val = getattr(obj, property)
    check_box.setCheckState(Qt.Checked if init_val else Qt.Unchecked)
    check_box.stateChanged.connect(lambda s: setattr(obj, property, bool(s)))

def push_button_binder(push_button, property, obj):
    push_button.clicked.connect(getattr(obj, property))
    
def combo_box_binder(combo_box, property, obj):
    def on_property_changed(sender, prop):
        if prop == property+'_option':
            items = [str(item) for item in getattr(obj, property+'_option')()]
            combo_box.clear()
            combo_box.addItems(items)
        elif prop == property:
            value = getattr(obj, property)
            combo_box.setCurrentIndex(combo_box.findText(str(value)))

    def current_index_changed(string):
        if string == '': return
        if str(getattr(obj, property)) != string:
            setattr(obj,property, string)

    on_property_changed(obj, property+'_option')
    on_property_changed(obj, property)
    obj.property_changed.connect(on_property_changed)
    combo_box.currentIndexChanged[str].connect(current_index_changed)


def action_binder(action, property, obj):
    action.triggered.connect(getattr(obj, property))

def group_box_binder(group_box, property, obj):
    widget_binder(group_box, property,obj)
    
def layout_binder(layout, prop, obj):

    temp = getattr(obj, prop)()
    if isinstance(temp,QWidget):
        view = temp
    else :
        view = view_locator(temp)
        bind(vm, view)
    layout.addWidget(view)
    
def table_binder(table, property, obj):
    def model_changed(sender, prop):
        if prop == property:
            model = getattr(obj, prop)()
            table.setModel(model)
        
    model_changed(obj, property)
    obj.property_changed.connect(model_changed)

def widget_binder(widget, property, obj):
    def on_viewmodel_changed(sender, prop):
        if prop == property:
            vm = getattr(obj, property)()
            v = view_locator(vm)
            if widget.layout() != None: 
            # delete layout
                pass
            else:
                l = QVBoxLayout()
                l.addWidget(v)
                widget.setLayout(l)
            bind(vm, v)

    on_viewmodel_changed(obj,property)
    obj.property_changed.connect(on_viewmodel_changed)

_control_binder = { QLineEdit : line_edit_binder,
                    QPushButton : push_button_binder,
                    QComboBox : combo_box_binder,
                    QCheckBox : check_box_binder,
                    QAction : action_binder,
                    QGroupBox: group_box_binder,
                    QBoxLayout: layout_binder,
                    QTableView: table_binder,
                    QWidget: widget_binder}


def get_public_attributes(obj):
    return (p for p in dir(obj) if not p.startswith('_'))


def bind(viewmodel, view):
    for p in get_public_attributes(viewmodel):
        control = getattr(view.ui,p, None)
        if control:
            print p
            typ = type(control)
            while(True):
                try:
                    _control_binder[typ](control, p, viewmodel)
                    break
                except KeyError:
                    if typ == object:
                        break
                    else:
                        typ = typ.__base__


def view_locator(viewmodel):
    module = inspect.getmodule(viewmodel)
    view_name = type(viewmodel).__name__[:-5]
    return getattr(module, view_name)()


#def get_properties(obj):
#    return (p for p in dir(obj) if p[0] != '_' and not callable(getattr(obj,p)))

#def bind_properties(viewmodel, view):
#    for p in get_properties(viewmodel):
#        try :
#            control = getattr(view,p)
#        except AttributeError:
#            continue
#        _control_binder[type(control)](control, p, viewmodel)

#def get_methods(obj):
#    return (p for p in dir(obj) if p[0] != '_' and callable(getattr(obj,p)))

#def bind_methods(viewmodel, view):  
#    for p in get_methods(viewmodel):
#        try:
#            control = getattr(view,p)
#        except AttributeError:
#            continue
#        control.pressed.connect(getattr(viewmodel, p))
