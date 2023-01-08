from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    ObjectProperty, StringProperty
)
from kivy.uix.label import Label
from kivy.factory import Factory
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock

import os
import shutil
import platform
import time
import threading
from kivy.core.text import LabelBase
if platform.system() == 'Windows':
    LabelBase.register('Roboto', 'C:/Windows/Fonts/simsun.ttc')

from method2 import method2

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    font = StringProperty('Roboto')
    start_path = StringProperty(".")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if platform.system() == 'Linux':
            if 'ANDROID_STORAGE' in os.environ:
                # from android.permissions import request_permissions, Permission
                # request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
                if os.path.exists('/storage/emulated/0'):
                    self.start_path = "/storage/emulated/0"
                else:
                    self.start_path = os.path.dirname(os.path.abspath(__file__))
            else:
                self.start_path = "/home"
        elif platform.system() == 'Windows':
            self.start_path = "C:\\Users"
                


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    font = StringProperty('Roboto')
    start_path = StringProperty(".")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if platform.system() == 'Linux':
            if 'ANDROID_STORAGE' in os.environ:
                if os.path.exists('/storage/emulated/0'):
                    self.start_path = "/storage/emulated/0"
                else:
                    self.start_path = os.path.dirname(os.path.abspath(__file__))
            else:
                self.start_path = "/home"
        elif platform.system() == 'Windows':
            self.start_path = "C:\\Users"

class Root(FloatLayout):
    source_original = StringProperty('')
    source_processed = StringProperty('')

    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)

    temp_path = ''

    font = StringProperty('Roboto')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if platform.system() == 'Windows':
            self.temp_path = os.getcwd() + '\_temp_.jpg'
        else:
            self.temp_path = os.getcwd() + '/_temp_.jpg'
        if 'ANDROID_STORAGE' in os.environ:
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        file_path = os.path.join(path, filename[0])

        # delete previously used temp file
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)
            print('File removed')
        else:
            print('Temp file does not exist')

        # check if the file exists
        if not os.path.exists(file_path):
            self.popup_loading = Popup(title='Error', content=Label(text='Image does not exists'))
            self.popup_loading.open()
            time.sleep(1)
            self.popup_loading.dismiss()

        # display original image
        if platform.system() == 'Linux' and file_path[1] != '/':
            self.source_original = '/' + file_path
        else:
            self.source_original = file_path

        # process image
        self.popup_loading = Popup(title='Inform', content=Label(text='Processing Image... Please wait\n\nNote: Recommended image size is less than 449*362'),
              auto_dismiss=False)
        self.popup_loading.open()
        
        t = threading.Thread(target=method2, args=(file_path,))
        # set daemon to true so the thread dies when app is closed
        t.daemon = True
        # start the thread
        t.start()

        if platform.system() == 'Linux' and self.temp_path[1] != '/':
            self.temp_path = '/' + self.temp_path

        WAIT_SECONDS = 1
        Clock.schedule_interval(self.monitor_temp, WAIT_SECONDS)
        
        self.dismiss_popup()

    def monitor_temp(self, dt):
        if os.path.exists(self.temp_path):
            self.source_processed = self.temp_path
            self.popup_loading.dismiss()
            return False
        return True

    def save(self, path, filename):
        shutil.copy2(self.temp_path, os.path.join(path, filename))

        self.dismiss_popup()

class ImageApp(App):
    pass

Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)

if __name__ == '__main__':
    ImageApp().run()