import csv
import sys
import pinyin
from kivy.app import App
from random import sample
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.settings import SettingsWithTabbedPanel
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty


filepath = 'mgchin.csv'
filepath = r'hzquiz.yml'
char_choice = 'simp'


with open(filepath, encoding='utf-8') as f:
            a = Builder.load_string(f.read())
with open('json.json', encoding='utf-8') as f:
            json = f.read()

def build_colour(dobj, code='[color={0}]{1}[/color]'):
    # really unpythonic design
    # fix me somehow!
    op = []
    colours = [None, App.get_running_app().config.get('Colours','tone1c'),
               App.get_running_app().config.get('Colours','tone2c'),
               App.get_running_app().config.get('Colours','tone3c'),
               App.get_running_app().config.get('Colours','tone4c'),
               App.get_running_app().config.get('Colours','tone5c')]
    char = dobj[char_choice]
    tones = dobj['pinyin'].split(' ')
    tones = [i[-1] for i in tones]
    for i in tones:
        try:
            int(i)
        except ValueError:
            i = '1'
    assert len(char) == len(tones)
    for i, j in enumerate(char):
        op.append(code.format(colours[int(tones[i])],j))
    return ''.join(op)

def make_pinyin(dobj, dbg = False):
    pinyin_choice = App.get_running_app().config.get('Settings','pinyin_choice')
    #print(pinyin_choice)
    if pinyin_choice in ['1', 1, 'True', True]:
        #print('one')
        return dobj['pinyin']
    elif pinyin_choice in ['0', 0, 'False', False]:
        #print('zero')
        return pinyin.get(dobj[char_choice])

def build_dic(file, fr=False):
    try:
        print('d len',len(d))
    except:
        pass
    op = []
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i in reader:
            op.append(i)
    print('op len', len(op))
    return op

d = build_dic(filepath, fr = True)

def hzchoicegen(answer, choices = 3):
    for i in d:
        if i[char_choice] == answer:
            answer = i
    op = sample(d,choices+1)
    if not answer in op:
        op[-1] = answer
    return sample(op,len(op)), answer

def gen_questions():
    print('gq',len(d))
    questions = []
    for i in d:
        for j in range(int(App.get_running_app().config.get('Settings','repeats'))) :
            questions.append(hzchoicegen(i))
    questions = sample(questions, len(questions))
    global clear
    clear = False
    return questions

clear = False

class HanziQuiz(Screen):
    def __init__(self, **kwargs):
        super(HanziQuiz, self).__init__(**kwargs)
        self.questions=[]
        self.gq()
        self.new_question()
        self.buttons = []
        
    def new_question(self):
        global clear
        if clear == True:
            self.gq()
        print('nq',len(self.questions))
        self.pq = self.questions.pop(0)
        self.main_text.text = build_colour(self.pq[1])
        self.main_text.font_name = App.get_running_app().config.get('Settings','char_font')
        self.buttons = [make_pinyin(i) for i in self.pq[0][:]]
        self.buttons = sample(self.buttons, len(self.buttons))
        self.b1_button.text, self.b2_button.text, self.b3_button.text, self.b4_button.text = self.buttons
        self.b1_button.font_name, self.b2_button.font_name, self.b3_button.font_name, self.b4_button.font_name = [App.get_running_app().config.get('Settings','other_font') for i in range(4)]
        self.bottom_text.text = ' '

    def next_function(self):
        self.questions.append(self.pq)
        self.new_question()
        
    def check_answer(self, text):
        result = text == make_pinyin(self.pq[1])
        print(text,make_pinyin(self.pq[1]),result)
        if result == True:
            if len(self.questions) == 0:
                self.main_text.text = 'Done'
                self.gq()
            else:
                self.new_question()

    def gq(self):
        self.questions = []
        print('before', len(self.questions))
        self.questions = gen_questions()
        print('after',len(self.questions))
        self.new_question()
        
    def show_meaning(self):
        self.bottom_text.text = self.pq[1]['meaning']

class PinyinQuiz(Screen):
    def __init__(self, **kwargs):
        super(PinyinQuiz, self).__init__(**kwargs)
        #self.questions = gen_questions()
        self.gq()
        self.new_question()
        self.buttons = []
        
    def new_question(self):
        global clear
        if clear == True:
            self.gq()
        self.pq = self.questions.pop(0)
        self.main_text.text = make_pinyin(self.pq[1])
        self.main_text.font_name = App.get_running_app().config.get('Settings','other_font')
        self.buttons = [i[char_choice] for i in self.pq[0][:]]
        self.buttons = sample(self.buttons, len(self.buttons))
        self.b1_button.text, self.b2_button.text, self.b3_button.text, self.b4_button.text = self.buttons
        self.b1_button.font_name, self.b2_button.font_name, self.b3_button.font_name, self.b4_button.font_name = [App.get_running_app().config.get('Settings','char_font') for i in range(4)]
        self.bottom_text.text = ' '

    def next_function(self):
        self.questions.append(self.pq)
        self.new_question()
        
    def check_answer(self, text):
        result = text == self.pq[1][char_choice]
        #print(result)
        if result == True:
            if len(self.questions) == 0:
                self.main_text.text = 'Done'
                self.gq()
            else:
                self.new_question()
    def gq(self):
        self.questions = gen_questions()
        self.new_question()
        
    def show_meaning(self):
        self.bottom_text.text = self.pq[1]['meaning']

class MeaningQuiz(Screen):
    def __init__(self, **kwargs):
        super(MeaningQuiz, self).__init__(**kwargs)
        #self.questions = self.questions()
        self.gq()
        self.new_question()
        self.buttons = []
        
    def new_question(self):
        global clear
        if clear == True:
            self.gq()
        self.pq = self.questions.pop(0)
        self.main_text.text = self.pq[1]['meaning']
        self.main_text.font_name = App.get_running_app().config.get('Settings','other_font')
        self.buttons = [i[char_choice] for i in self.pq[0][:]]
        self.buttons = sample(self.buttons, len(self.buttons))
        self.b1_button.text, self.b2_button.text, self.b3_button.text, self.b4_button.text = self.buttons
        self.b1_button.font_name, self.b2_button.font_name, self.b3_button.font_name, self.b4_button.font_name = [App.get_running_app().config.get('Settings','char_font') for i in range(4)]
        self.bottom_text.text = ' '

    def next_function(self):
        self.questions.append(self.pq)
        self.new_question()
        
    def check_answer(self, text):
        result = text == self.pq[1][char_choice]
        #print(result)
        if result == True:
            if len(self.questions) == 0:
                self.main_text.text = 'Done'
                self.gq()
            else:
                self.new_question()
    def gq(self):
        self.questions = gen_questions()
        self.new_question()

    def show_pinyin(self):
        self.bottom_text.text = make_pinyin(self.pq[1])

class LoadList(Screen):
    def load(self, selection):
        self.file_path = str(selection[0])
        print(self.file_path)
        global d
        global clear
        if '.csv' in str(self.file_path):
            App.get_running_app().config.set('Settings','list', self.file_path)
            d = build_dic(self.file_path)
            clear = True
        else:
            print('Error: Not CSV!', self.file_path)
    def cancel(self):
        pass
        

class Menu(Screen):
    pass

class MySettingsWithTabbedPanel(SettingsWithTabbedPanel):
    def on_close(self):
        Logger.info("main.py: MySettingsWithTabbedPanel.on_close")

    def on_config_change(self, config, section, key, value):
        Logger.info(
            "main.py: MySettingsWithTabbedPanel.on_config_change: "
            "{0}, {1}, {2}, {3}".format(config, section, key, value))
        
class main(App):
    def build(self):
        global d 
        d = build_dic(App.get_running_app().config.get('Settings','list'))
        root = ScreenManager()
        root.add_widget(Menu(name='menu'))
        root.add_widget(LoadList(name='loadlist'))
        root.add_widget(HanziQuiz(name='hanziquiz'))
        root.add_widget(PinyinQuiz(name='pinyinquiz'))
        root.add_widget(MeaningQuiz(name='meaningquiz'))
        self.settings_cls = MySettingsWithTabbedPanel
        global char_choice
        if App.get_running_app().config.get('Settings', 'char_choice') == True:
            char_choice = 'trad'
        elif App.get_running_app().config.get('Settings', 'char_choice') == False:
            char_choice = 'simp'
        return root
    
    def build_config(self, config):
        # Set the default values for the configs sections.
        config.setdefaults('Settings', {'repeats': 3, 'pinyin_choice': True,
                                        'char_choice':False, 
                                        'char_font':'RenDong Yang Bamboo stone.ttf', 
                                        'other_font':'NotosansCJK.ttc'})
        config.setdefaults('Colours', {'tone1c':'0000aa', 'tone2c':'00aa00',
                                       'tone3c':'ff8800', 'tone4c':'aa0000',
                                       'tone5c':'777777'})

    def build_settings(self, settings):
        settings.add_json_panel('Settings', self.config, data=json)

    def on_config_change(self, config, section, key, value):
        # Respond to changes in the configuration.
        # is this the secret to my salvation
        Logger.info("main.py: App.on_config_change: {0}, {1}, {2}, {3}".format(
            config, section, key, value))

    def close_settings(self, settings=None):
        # The settings panel has been closed.
        Logger.info("main.py: App.close_settings: {0}".format(settings))
        super(main, self).close_settings(settings)
        
    # Needed for Phones
    def on_pause(self):
        return True
    def on_resume(self):
      pass

if __name__ == "__main__":
    main().run()
