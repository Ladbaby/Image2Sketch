from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
)
from kivy.clock import Clock

from kivy.uix.boxlayout import BoxLayout
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button

from glob import glob

from kivy.factory import Factory
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout

import os
import shutil
import concurrent.futures
import platform

from method2 import method2

# class Photo(Widget):
#     source = StringProperty(None)

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

class Root(FloatLayout):
    source_original = StringProperty('')
    source_processed = StringProperty('')

    # photo_original = ObjectProperty()
    # editor_pane = ObjectProperty()
    # photo_processed = ObjectProperty()

    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)

    temp_path = ''

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
        # file_path = path + filename[0]

        # delete previously used temp file
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)
            print('File removed')
        else:
            print('File does not exist')

        # check if the file exists
        if not os.path.exists(file_path):
            popup_loading = Popup(title='Error', content=Label(text='Image does not exists'))
            popup_loading.open()

        # display original image
        if platform.system() == 'Linux' and file_path[1] != '/':
            self.source_original = '/' + file_path
        else:
            self.source_original = file_path

        # process image
        popup_loading = Popup(title='Inform', content=Label(text='Processing Image'),
              auto_dismiss=False)
        popup_loading.open()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(method2, file_path)
            self.temp_path = future.result()

            if platform.system() == 'Linux' and self.temp_path[1] != '/':
                    self.temp_path = '/' + self.temp_path


        self.source_processed = self.temp_path
        popup_loading.dismiss()
        self.dismiss_popup()


    def save(self, path, filename):
        # with open(os.path.join(path, filename), 'w') as stream:
        #     stream.write(self.text_input.text)
        shutil.copy2(self.temp_path, os.path.join(path, filename))

        self.dismiss_popup()

class ImageApp(App):
    pass
    # def build(self):
    #     root = BoxLayout(orientation='vertical')
    #     layout_photo = PhotoLayout()

    #     curdir = dirname(__file__)
    #     index = 0
    #     for filename in glob(join(curdir, 'images', '*')):
    #         try:
    #             # picture = Photo(source = filename)
    #             if index == 0:
    #                 layout_photo.photo_original.source = filename 
    #             else:
    #                 layout_photo.photo_processed.source = filename 
    #         except Exception as e:
    #             Logger.exception('Pictures: Unable to load <%s>' % filename)
    #         index += 1

    #     root.add_widget(layout_photo)

    #     btn_open_picture = Button(text="Choose a Photo")

    #     layout_menu = BoxLayout(size_hint=(1, None), height=50)
    #     layout_menu.add_widget(btn_open_picture)

    #     root.add_widget(layout_menu)

    #     return root 

    # def on_pause(self):
    #     return True

Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)

if __name__ == '__main__':
    ImageApp().run()