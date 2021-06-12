#######################################################
## This is the main module of the SpeechAdjuster tool.
#######################################################
#######################################################
## Author: Olympia Simantiraki
## License: GNU GPL v3
## Version: v1.0.0
## Email: olina.simantiraki@gmail.com
#######################################################

import sys
from configparser import ConfigParser, NoSectionError, NoOptionError
import argparse
import logging
import platform
import os
import filecmp
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create a file handler
handler = logging.FileHandler('logfile.log', mode='w')
handler.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter('%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
logging.Formatter.converter = time.gmtime
handler.setFormatter(formatter)
# add the file handler to the logger
logger.addHandler(handler)

parser = ConfigParser()
# get the path to config.ini
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
parser.read(config_path)

parser2 = argparse.ArgumentParser(prog='PROG',description='speechadjuster.py (main module)')
parser2.add_argument('-u', '--username', type=str, help='Participant unique ID. (type: string)')
parser2.add_argument('-a','--adjustmentfolder', type=str, help='Path(s) to target speech folders (e.g. ﻿stimuli/examples/tilt/adjustment/) for the adjustment phase. If more than one split them with commas without using spaces. (type: strings with comma delimiter)')
parser2.add_argument('-t','--testfolder', type=str, help='Path(s) to target speech folders (e.g. stimuli/examples/tilt/test/) for the test phase. If more than one split them with commas without using spaces. The total number of paths provided for the test '
                                                         'phase should be equal to those provided for the adjustment phase. If paramenter is empty, trials do not consist of a test phase.'
                                                         '(type: strings with comma delimiter)')
parser2.add_argument('-m', '--masker', type=str, help='Path with masker filename (e.g. stimuli/maskers/SSN.wav). If paramenter is empty, target speech is presented in quiet. (type: string)')
args = parser2.parse_args()

if all(v is None for v in [args.adjustmentfolder,args.masker,args.testfolder,args.username]):
    parser2.print_help(sys.stderr)
    sys.exit(1)

try:
    args = parser2.parse_args()
    logger.info(args)
except SystemExit:
    exc = sys.exc_info()[1]
    logger.error(exc)

platform = platform.system()
logger.info("Platform  "+ str(platform))

try:
    logger.info("Parameters checking has started. ")
    username = args.username

    prefix = parser.get('stimuli', 'prefix')
    numOftrials = parser.getint('setup_adj', 'numOftrials')
    button_on = parser.getfloat('setup_adj', 'button_on')
    audio_on = parser.getfloat('setup_adj', 'audio_on')
    gap = parser.getfloat('setup_adj', 'gap')
    numOftesting = parser.getint('setup_test', 'numOftesting')
    test1audio = parser.getfloat('setup_test', 'test1audio')
    testaudio = parser.getfloat('setup_test', 'testaudio')
    speech_on = parser.getfloat('setup_test', 'speech_on')
    knob = parser.getboolean('setup_adj', 'knob')
    saveaudio = parser.getboolean('setup_adj', 'saveaudio')
    directory = parser.get('instructions', 'directory')
    blktxt=parser.get('instructions', 'blktxt')
    exittime = parser.getfloat('instructions', 'exittime')
    audiochunk = parser.getfloat('stimuli', 'audiochunk')
    maskerchunk = parser.getfloat('stimuli', 'maskerchunk')
    uplimtxt = parser.get('instructions','uplimtxt')
    lowlimtxt = parser.get('instructions','lowlimtxt')
    testparttxt = parser.get('instructions', 'testparttxt')
    btntxt = parser.get('instructions', 'btntxt')
    adjarrowstxt = parser.get('instructions', 'adjarrowstxt')
    adjknobtxt = parser.get('instructions', 'adjknobtxt')
    instructions = parser.get('instructions', 'instructionstxt')
    btnstart = parser.get('instructions', 'btnstart')
    endtxt = parser.get('instructions', 'endtxt')

    assert numOftrials > 0, sys.exit('The paramenter numOftrials should be greater than zero.')
    assert speech_on >= 0, sys.exit('The parameter speech_on should be greater than or equal to zero.')
    assert exittime >= 0, sys.exit('The parameter exittime should be greater than or equal to zero.')
    assert numOftesting > 0, sys.exit('The parameter numOftesting should be greater than zero.')
    assert test1audio >= 0, sys.exit('The parameter test1audio should be greater than or equal to zero.')
    assert testaudio >= 0, sys.exit('The parameter testaudio should be greater than or equal to zero.')
    assert button_on >= audio_on, sys.exit('The parameter button_on should be greater than or equal to the parameter audio_on.')
    assert audio_on >= 0, sys.exit('The parameter audio_on should be greater than or equal to zero.')
    assert gap >= 0, sys.exit('The parameter gap should be greater than or equal to zero.')
    assert args.adjustmentfolder, sys.exit('[ERROR] The argument --adjustmentfolder should not be empty.')
    assert username, sys.exit('The argument --username should not be empty.')
    assert audiochunk > 0, sys.exit('The parameter audiochunk should be greater than zero.')
    assert maskerchunk > 0, sys.exit('The parameter maskerchunk should be greater than zero.')

except AssertionError as error:
    sys.exit("[ERROR] in configuration file (config.ini) or in command line arguments.")
except ValueError:
    logger.error(
            '[ERROR] wrong parameter type. Check again the types of the parameters  in congig.ini and command line. \n '
            'Parameters of type integer, float, boolean cannot be empty.')
    sys.exit('[ERROR] wrong parameter type. Check again the types of the parameters  in congig.ini and command line. \n '
            'Parameters of type integer, float, boolean cannot be empty.')
except (NoSectionError, NoOptionError):
    logger.error(
        '[ERROR] in configuration file (config.ini). \n-hint- all the parameters and section titles should be out of comments.')
    sys.exit(
        '[ERROR] in configuration file (config.ini). \n-hint- all the parameters and section titles should be out of comments.')

if args.masker:
    if not os.path.exists(args.masker):
        logger.error("Masker file " + args.masker + " does not exist.")
        sys.exit('[ERROR] masker file does not exist.')
    else:
        quiet = False

if os.path.exists(directory + 'results/' + str(username) + "_results.txt") :
    print("[ERROR] the filename " + str(directory + 'results/' + str(username) + "_results.txt") + "  already exists. Use a different ID.")
    logger.error(directory + 'results/' + str(username) + "_results.txt"  + " already exists.")
    sys.exit()

if not args.masker:
    quiet = True

args.adjustmentfolder = args.adjustmentfolder.split(',')
len_adjustmentfolder = len(args.adjustmentfolder)
lowerlevel = 1

for ch in range(0,len_adjustmentfolder):
    if not os.path.exists(args.adjustmentfolder[ch]):
        logger.error('The directory ' + args.adjustmentfolder[ch] +' does not exist.')
        sys.exit('[ERROR] The directory ' + str(args.adjustmentfolder[ch]) +' does not exist.')

for k in range(0, len_adjustmentfolder):
    if len(next(os.walk(args.adjustmentfolder[k]))[1]) == 1:
        logger.error(
            'More than one levels/folders should exist.')
        sys.exit("[ERROR] More than one levels/folders should exist.")

for j in range(0, len_adjustmentfolder):
    args.adjustmentfolder[j] = args.adjustmentfolder[j] + '/'
    for i in range(lowerlevel, len(next(os.walk(args.adjustmentfolder[j]))[1]) + 1):
        if not os.path.exists(args.adjustmentfolder[j] +prefix+ str(i)):
            logger.error('Adjustment phase: folder ' + args.adjustmentfolder[j] + prefix + str(i) + " does not exist. In the directory  " + args.adjustmentfolder[j] + " only the folders with the target speech stimuli should exist starting with the prefix " +prefix+
                         '.\nAll the folders with integer IDs from 1 to the maximum number of levels with step 1 should exist.')
            sys.exit("[ERROR] Adjustment phase: folder does not exist.\n"+ 'Adjustment phase: folder ' + args.adjustmentfolder[j] + prefix + str(i) + " does not exist. In the directory  " + args.adjustmentfolder[j] + " only the folders with the target speech stimuli should exist starting with the prefix " +prefix+
                         '.\nAll the folders with integer IDs from 1 to the maximum number of levels with step 1 should exist.')

        dcmp = filecmp.dircmp( args.adjustmentfolder[j] + prefix + str(lowerlevel) + '/', args.adjustmentfolder[j]+ prefix + str(i) + '/')
        if '.DS_Store' in dcmp.left_only: dcmp.left_only.remove('.DS_Store')
        if '.DS_Store' in dcmp.right_only: dcmp.right_only.remove('.DS_Store')
        res_left = [x for x in dcmp.left_only if re.search('.wav', x)]
        res_right = [x for x in dcmp.right_only if re.search('.wav', x)]

        if len([name for name in os.listdir(args.adjustmentfolder[j] +'/'+ prefix + str(i)) if name.endswith(".wav")]) == 0:
            sys.exit('[ERROR] The directory '+ args.adjustmentfolder[j] +  prefix + str(i) + '  does not contain .wav files.' )
            logger.error('[ERROR] The directory '+ args.adjustmentfolder[j] + prefix + str(i) + '  does not contain .wav files.' )

        if (len(dcmp.left_only) > 0 and len(res_left) > 0) or (len(dcmp.right_only) > 0  and len(res_right) > 0):
            logger.error(
                'All the levels/folders in the same directory should contain .wav files with the same filenames.')
            logger.error('Files only in directory '+ args.adjustmentfolder[j] + prefix + str(lowerlevel) +'/' +'  : '+ str(dcmp.left_only))
            logger.error('Files only in directory ' + args.adjustmentfolder[j] + prefix + str(i)  + '/' + '  : ' + str(dcmp.right_only))
            sys.exit("[ERROR] Adjustment phase: file does not exist. \nAll the levels/folders in the same directory should contain .wav files with the same filenames.\n\n"+
                     'Different files in directory '+ args.adjustmentfolder[j] + prefix + str(lowerlevel) +'/' +'  : '+ str(dcmp.left_only)+'\nDifferent files in directory ' + adjustmentfolder[j] + prefix + str(i)  + '/' + '  : ' + str(dcmp.right_only))

if not args.testfolder:
    testphase = False
    numOftesting = 0
else:
    testphase = True
    args.testfolder = args.testfolder.split(',')
    len_testfolder = len(args.testfolder)

    if len_testfolder != len_adjustmentfolder:
        logger.error('The total number of paths provided in the command line for the test phase should be equal to that provided for the adjustment phase.')
        sys.exit("[ERROR] The total number of paths provided in the command line for the test phase should be equal to that provided for the adjustment phase.")
    for j in range(0, len(args.testfolder)):
        args.testfolder[j] = args.testfolder[j] + '/'
        for i in range(lowerlevel, len(next(os.walk(args.adjustmentfolder[j]))[1]) + 1):
            if not os.path.exists(args.testfolder[j] +prefix+ str(i)):
                logger.error('Test phase: folder ' + args.testfolder[j] +prefix+ str(i) + " does not exist. In the directory  " +args.testfolder[j]+ " only the folders with the target speech stimuli should exist starting with the prefix " +prefix+
                             '.\n All the folders with integer IDs from 1 to the maximum number of levels with step 1 should exist.\n The total number of levels/folders provided in the directory for the test phase should be equal to that provided for the adjustment phase.')
                sys.exit('[ERROR] Test phase: folder ' + args.testfolder[j] +prefix+ str(i) + " does not exist. In the directory  " +args.testfolder[j]+ " only the folders with the target speech stimuli should exist starting with the prefix " +prefix+
                             '.\n All the folders with integer IDs from 1 to the maximum number of levels with step 1 should exist.\n The total number of levels/folders provided in the directory for the test phase should be equal to that provided for the adjustment phase.')

            dcmp = filecmp.dircmp(args.testfolder[j] + prefix + str(lowerlevel) + '/',
                                  args.testfolder[j] + prefix + str(i) + '/')
            if '.DS_Store' in dcmp.left_only: dcmp.left_only.remove('.DS_Store')
            if '.DS_Store' in dcmp.right_only: dcmp.right_only.remove('.DS_Store')
            res_left = [x for x in dcmp.left_only if re.search('.wav', x)]
            res_right = [x for x in dcmp.right_only if re.search('.wav', x)]

            if len([name for name in os.listdir(args.testfolder[j] + '/' + prefix + str(i)) if
                        name.endswith(".wav")]) == 0:
                sys.exit('[ERROR] The directory ' + args.testfolder[j] + prefix + str(
                    i) + '  does not contain .wav files.')
                logger.error('[ERROR] The directory ' + args.testfolder[j] + prefix + str(
                    i) + '  does not contain .wav files.')

            if len(dcmp.left_only) > 0 or len(dcmp.right_only) > 0:
                logger.error('All the levels/folders in the same directory should contain .wav files with the same filenames.')
                logger.error(
                    'Files only in directory ' + args.testfolder[j] + prefix + str(lowerlevel) + '/' + '  : ' + str(
                        dcmp.left_only))
                logger.error('Files only in directory ' + args.testfolder[j] + prefix + str(i) + '/' + '  : ' + str(
                    dcmp.right_only))
                sys.exit(
                    "[ERROR] Test phase: file does not exist. \nAll the levels/folders in the same directory should contain .wav files with the same filenames.\n\n" +
                    'Different files in directory ' + args.testfolder[j] + prefix + str(
                        lowerlevel) + '/' + '  : ' + str(dcmp.left_only) + '\nDifferent files in directory ' +
                    args.testfolder[j] + prefix + str(i) + '/' + '  : ' + str(dcmp.right_only))

    # for mac works:
    # wavs_test = glob.glob(testfolder[0] +'/'+  prefix +str(lowerlevel) + '/*.wav')
    # wavs_test = [w.replace(testfolder[0] +'/'+ prefix + str(lowerlevel) + '/', '') for w in wavs_test]

logger.info("Parameters checking has ended successfully. ")

is_mac = platform == 'Darwin'

os.environ['KIVY_NO_ARGS'] = 'T'

import kivy
kivy.require('1.0.8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from hyperknob import HyperKnob
from kivy.config import Config
from datetime import datetime
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock
from kivy.core.window import Window
import pyaudio
import wave
import math
import numpy as np
import random
import threading
from kivy.properties import BooleanProperty, NumericProperty, ListProperty


Config.set('kivy', 'exit_on_escape', '1')
Window.clearcolor = (.6, .6, .6, .2)
Window.fullscreen = 'auto'
_is_desktop = False


class SpeechAdjuster(RelativeLayout):

    completion_button = Button(text=btntxt,
                     pos_hint={'center_x': .5, 'center_y': .3}, size_hint=(.35, .08),
                     font_size='45dp', background_color=[1, 1, 1, .1],
                     color=[1, 1, 1, .1])

    adj_label = Label(color=[.9, .9, .9, 1], font_size='50dp',
                           pos_hint={'center_x': .5, 'center_y': .95})

    higher_lim = Label(text='', pos_hint={'center_x': .5, 'center_y': .8},
                           size_hint=(.28, .05), font_size='50dp', color=(1, 1, 1, .7))
    lower_lim = Label(text='', pos_hint={'center_x': .5, 'center_y': .4},
                           size_hint=(.28, .05),
                           font_size='50dp', color=[1, 1, 1, .7])

    button_up = Button(background_color=[1, 1, 1, .7], background_normal='graphics/up.png',
                      background_down='graphics/up.png',
                      border=(8, 8, 8, 8), color=[1, 1, 1, .5], size_hint=(.09, .09),
                      pos_hint={'center_x': .5, 'center_y': .67})

    button_down = Button(background_color=[1, 1, 1, .7], background_normal='graphics/down.png',
                        background_down='graphics/down.png',
                        border=(8, 8, 8, 8), color=[1, 1, 1, .5], size_hint=(.09, .09),
                        pos_hint={'center_x': .5, 'center_y': .54})

    test_label = Label(text=testparttxt, color=[1, 1, 1, .1], font_size='50dp',
                        pos_hint={'center_x': .18, 'center_y': .18})

    text_in = TextInput( is_focusable=True, focus=True, background_color=[1, 1, 1, .1],
                           font_size='50dp', size_hint=(.98, .11), pos_hint={'center_x': .5, 'center_y': .08},
                           multiline=False)

    hyper_knob = HyperKnob(pos_hint={'center_x': .5, 'center_y': .55}, size=('500dp', '500dp'),
                          minangle=-140, maxangle=140, line_start=.82, line_end=.95, knob_radius=.95,
                          track_proportion=.8)

    block_num_label = Label(text='', color=[.9, .9, .9, 1], font_size='37dp',
                     pos_hint={'center_x': .5, 'center_y': .96})

    instr_label = Label(text=instructions, color=[.9, .9, .9, 1], font_size='37dp',
                   pos_hint={'center_x': .5, 'center_y': .8})

    start_button = Button(text=btnstart, markup=True, pos_hint={'center_x': .5, 'center_y': .15},
                    size_hint=(.15, .05), font_size='40dp', background_color=[.1, .1, .1, 1],
                    color=[1, 1, 1, 1])

    on_adjustmentphase = BooleanProperty(True)
    value_changed = BooleanProperty(False)
    button_pressed = BooleanProperty(False)
    key_pressed = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(SpeechAdjuster, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        self.p = pyaudio.PyAudio()
        self.p_noise = pyaudio.PyAudio()
        self.current_pos = 0
        self.prev_wav_len = 1
        self.block_num = 1
        self.iteration = 1
        self.tmp_fid = 0
        self.data_append = tuple()

        self.count_frames=0
        self.data2=[]

        self.button_up.bind(on_press=self.increment)
        self.button_down.bind(on_press=self.decrement)
        self.button_up.bind(on_release=self.button_release)
        self.button_down.bind(on_release=self.button_release)
        self.text_in.bind(on_text_validate=self.on_validate)
        self.start_button.bind(on_release=self.start_controller)
        self.completion_button.bind(on_release=self.completion_button_pressed)

        Clock.schedule_once(self.starting_panel)

    def show_keyboard(self, event):
        self.text_in.focus = True

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """When the up/down keyboard arrow is pressed, the speech level increases/decreases by 1.
        """
        if self.on_adjustmentphase:

            if keycode[1] == 'down':

                if self.value > lowerlevel:
                    self.value -= 1
                    self.lower_lim.text = ''
                    self.higher_lim.text = ''

                if self.value == lowerlevel:
                    self.lower_lim.text = lowlimtxt
                    self.lower_lim.color = [.6, 0, 0, 1]
                    self.value = lowerlevel;

            if keycode[1] == 'up':

                if self.value < self.higherlevel:
                    self.value += 1
                    self.lower_lim.text = ''
                    self.higher_lim.text = ''

                if self.value == self.higherlevel:
                    self.higher_lim.text = uplimtxt
                    self.higher_lim.color = [.6, 0, 0, 1]
                    self.value = self.higherlevel;

        if not self.key_pressed:
            pass

    def _keyboard_closed(self):
        pass

    def button_release(self, *kwargs):
        self.button_down.background_color = [1, 1, 1, .7]
        self.button_up.background_color = [1, 1, 1, .7]
        
    def start_controller(self, *kwargs):
        """Initializes variables, sets the widgets on the screen and calls the update function.
        """
        logger.info("function start_controller")

        self.i = 1
        self.threads = []
        self.next_wav = 0
        self.value_changed = False
        self.button_pressed = False
        self.count_phrases = 1
        self.testwavIds_i = 0
        self.trial_no = 1
        self.tphrases = 0
        self.taudio_progress = 0
        self.noise_off = True
        self.key_pressed = False

        self.higherlevel = len(next(os.walk(args.adjustmentfolder[self.block_num-1]))[1])

        wavs_adj = [name for name in os.listdir(args.adjustmentfolder[self.block_num-1] + '/' + prefix + str(lowerlevel)) if
                    name.endswith(".wav")]

        self.adjustwavIds = random.sample(wavs_adj, len(wavs_adj))  # random order of .wav files in adjustment phase

        self.write_txt("Adjustment phase target audio IDs : " + str(self.adjustwavIds))
        self.write_txt("Block : " + str(self.block_num))
        self.write_txt("Target audio path : " + str(args.adjustmentfolder[self.tmp_fid]))

        self.remove_widget(self.start_button)
        self.remove_widget(self.instr_label)
        self.remove_widget(self.block_num_label)

        if not knob:
            self.button_down.disabled = False
            self.button_up.disabled = False
            self.add_widget(self.button_down)
            self.add_widget(self.button_up)
            self.add_widget(self.higher_lim)
            self.add_widget(self.lower_lim)
            self.adj_label.text = adjarrowstxt
        else:
            self.hyper_knob.minvalue = lowerlevel
            self.hyper_knob.maxvalue = self.higherlevel + 0.9
            self.hyper_knob.disabled = False
            self.add_widget(self.hyper_knob)
            self.adj_label.text = adjknobtxt

        if testphase:
            self.add_widget(self.text_in)
            self.add_widget(self.test_label)
            self.text_in.disabled = True

            wavs_test = [name for name in os.listdir(args.testfolder[self.block_num-1] + '/' + prefix + str(lowerlevel)) if
                         name.endswith(".wav")]

            self.testwavIds = random.sample(wavs_test, len(wavs_test))  # random order of .wav files in test phase

        self.completion_button.disabled = False
        self.add_widget(self.adj_label)
        self.add_widget(self.completion_button)
        self.completion_button.disabled = True

        self.update()

    def start_audio(self, *kwargs):
        """For the adjustment phase, it starts the masker and target speech signals simultaneously using different threads
        or only the target speech signal if masker does not exist.
        """
        logger.info("function start_audio")

        if not quiet:
            self.noise_off = False
            self.threads.append(threading.Thread(target=self.play_noise()))

        self.threads.append(threading.Thread(target=self.play_speech()))
        map(lambda x: x.start(), self.threads)

    def play_speech(self):
        """Target speech streaming.
        """

        prev_wav = self.next_wav

        if self.next_wav >= len(self.adjustwavIds):
            self.next_wav = 0

        if not knob:
            self.audio_path = args.adjustmentfolder[self.tmp_fid] + prefix + str(
            self.value)
        else:
            self.audio_path = args.adjustmentfolder[self.tmp_fid] + prefix + str(
            self.value)

        
        self.wf = wave.open(
            self.audio_path + '/' + self.adjustwavIds[self.next_wav],
            'rb')

        if prev_wav == self.next_wav and self.iteration > 1:
            wav_len = self.wf.getnframes()
            self.current_pos = int(self.current_pos*(wav_len/self.prev_wav_len))

        self.prev_wav_len = self.wf.getnframes()
        self.wf.setpos(self.current_pos)

        audiochunk_samples = int(audiochunk * self.wf.getframerate())

        logger.info("function play_speech:" + self.audio_path + '/' + self.adjustwavIds[self.next_wav])
        self.stream_wf = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
                                     channels=self.wf.getnchannels(),
                                     rate=self.wf.getframerate(),
                                     output=True,
                                     stream_callback=self.callback, frames_per_buffer=audiochunk_samples)

    def callback(self, in_data, frame_count, time_info, status):
        self.count_frames =self.count_frames +1;

        data = self.wf.readframes(frame_count)
        # fade = int(frame_count / 2) # ramps half size of the chunk
        fade = int(0.02*self.wf.getframerate()) # ramps of fixed size 20ms

        if self.value_changed:
            # data = np.fromstring(data, np.int16) # np.fromstring is depricated by np.frombuffer
            data = np.frombuffer(bytearray(data), np.int16)

            self.data2 = self.wf2.readframes(frame_count)
            if len(self.data2)>2*fade:
                self.data2 = np.frombuffer(bytearray(self.data2), np.int16)
                fade_out = np.arange(1., 0., -1 / fade)
                self.data2[:fade] = np.multiply(self.data2[:fade], fade_out)

            if len(data)>fade:
                fade_in = np.arange(0., 1., 1 / fade)
                data[:fade] = np.multiply(data[:fade], fade_in)
                if len(self.data2) > 2*fade:
                    data[:fade] = data[:fade]+self.data2[:fade]

            # data=data.tostring()
            data = data.tobytes()
            self.value_changed = False


        if self.button_pressed and self.noise_off:
            self.button_pressed = False

            if saveaudio:
                # save audio to a .wav file
                wav_writer = wave.open('audio_tuning.wav', "wb")
                wav_writer.setframerate(self.wf.getframerate())
                wav_writer.setsampwidth(self.wf.getsampwidth())
                wav_writer.setnchannels(1)

                wav_writer.writeframes(self.data_append)
                wav_writer.close()

            return (data, pyaudio.paComplete)

        if self.value != self.tmp:
            # print('level changed at '+ "%.3f"%(self.count_frames*audiochunk) + 'sec') # uncomment for printing the time points that correspond to the listener's changes in the audio_tuning.wav file

            self.wf2 = self.wf

            self.value_changed = True
            self.current_pos = self.wf.tell()
            self.play_speech()


            if not is_mac:
                self.stream_wf.close()

            self.tmp = self.value
            self.write_txt("level = " + str(self.value))

        if len(data) < 2*frame_count:
            self.current_pos = 0;
            self.next_wav += 1

            Clock.schedule_once(lambda x: self.play_speech(), gap)
            self.wf.close()

            if not is_mac:
                self.stream_wf.close()

        self.data_append = np.append(self.data_append, data)

        if knob:
            self.value = int(math.floor(self.hyper_knob.value))

        return data, pyaudio.paContinue

    def play_noise(self):
        """Masker's streaming.
        """
        logger.info("function play_noise")

        self.noise = wave.open(
                args.masker,
                'rb')

        maskerchunk_samples = int(maskerchunk * self.noise.getframerate())

        self.stream_n = self.p_noise.open(format=self.p_noise.get_format_from_width(self.noise.getsampwidth()),
                                          channels=self.noise.getnchannels(),
                                          rate=self.noise.getframerate(),
                                          output=True,
                                          stream_callback=self.callback_noise, frames_per_buffer=maskerchunk_samples)

    def callback_noise(self, in_data, frame_count, time_info, status):
        data = self.noise.readframes(frame_count)

        if self.button_pressed:
            self.noise_off = True

            return (data, pyaudio.paComplete)

        if len(data) < 2 * frame_count:
            if not self.button_pressed:
                Clock.schedule_once(lambda x: self.play_noise(), 0)
                self.noise.close()

                if not is_mac:
                    self.stream_n.close()

        return data, pyaudio.paContinue

    def enable_completion_button(self, *kwargs):
        """Enables the completion button in the adjustment phase.
        """
        logger.info("function enable_completion_button")

        self.completion_button.color = [.9, .9, .9, 1]
        self.completion_button.background_color = [.1, .1, .1, .3]
        self.completion_button.disabled = False

    def completion_button_pressed(self, instance):
        """Once the completion button is pressed this function deactivates the screen widgets and activates the widgets in the test phase (if exists).
        """
        logger.info("function completion_button_pressed")

        self.write_txt("end of adjusting")
        self.button_pressed = True

        if not knob:
            self.val = self.value
            self.button_down.background_color = [1, 1, 1, .3]
            self.button_up.background_color = [1, 1, 1, .3]
            self.button_up.disabled = True
            self.button_down.disabled = True
            self.lower_lim.text = ''
            self.higher_lim.text = ''
        else:
            self.val = self.value
            self.value = lowerlevel
            self.tmp = self.value
            self.hyper_knob.value = self.tmp
            self.hyper_knob.markeroff_color = [.5, .5, .5, .9]
            self.hyper_knob.disabled = True

        self.next_wav += 1
        self.adj_label.color = [1, 1, 1, .1]
        self.completion_button.color = [1, 1, 1, .1]
        self.completion_button.background_color = [1, 1, 1, .1]
        self.on_adjustmentphase = False

        if testphase:
            self.taudio_progress = 0
            self.test_label.color = [.9, .9, .9, 1]
            self.text_in.background_color = [.9, .9, .9, 1]
            self.text_in.disabled = False

            Clock.schedule_once(self.show_keyboard)

            if self.count_phrases == 1:
                Clock.schedule_once(lambda x: self.tstart_audio(), test1audio)
            else:
                Clock.schedule_once(lambda x: self.tstart_audio(), testaudio)
        else:
            self.update()

        self.completion_button.disabled = True

        return

    def increment(self, *kwargs):
        """"On press of the up key arrow on the screen the speech level increases by 1.
        """
        self.button_up.background_color = [1, 1, 1, .3]

        if self.value < self.higherlevel:
            self.value += 1
            self.lower_lim.text = ''
            self.higher_lim.text = ''

        if self.value == self.higherlevel:
            self.higher_lim.text = uplimtxt
            self.higher_lim.color = [.6, 0, 0, 1]
            self.value = self.higherlevel;

    def decrement(self, *kwargs):
        """On press of the down key arrow on the screen the speech level decreases by 1.
        """
        self.button_down.background_color = [1, 1, 1, .3]

        if self.value > lowerlevel:
            self.value -= 1
            self.lower_lim.text = ''
            self.higher_lim.text = ''

        if self.value == lowerlevel:
            self.lower_lim.text = lowlimtxt
            self.lower_lim.color = [.6, 0, 0, 1]
            self.value = lowerlevel;

    #  for testing phase 
    def on_validate(self, obj):
        """It is called in the test phase after the listener has pressed the key ENTER.
        """
        logger.info("function on_validate: ENTER pressed.")

        if self.taudio_progress == 1:
            self.write_txt("Response: " + self.text_in.text)
            self.text_in.text = ""
            
            self.key_pressed = True

            if self.i == numOftesting:
                self.update()
        elif self.taudio_progress == 2:
            self.write_txt("Response: " + self.text_in.text)
            self.text_in.text = ""
            
            self.key_pressed = False
            self.text_in.disabled = False

            self.tphrases = 0
            self.taudio_progress = 0
            self.i += 1
            
            Clock.schedule_once(self.show_keyboard)

            if self.count_phrases == 1:
                Clock.schedule_once(lambda x: self.tstart_audio(), test1audio)
            else:
                Clock.schedule_once(lambda x: self.tstart_audio(), testaudio)

    def tcallback_speech(self, in_data, frame_count, time_info, status):
        data = self.wf.readframes(frame_count)
        
        if len(data) < 2 * frame_count:
            self.wf.close()
            
            if not is_mac:
                self.stream_wf.close()
            
            if self.count_phrases < numOftesting:
                self.taudio_progress = 2
                self.tphrases = self.tphrases + 1;
                self.count_phrases = self.count_phrases + 1
            elif self.count_phrases == numOftesting:
                self.taudio_progress = 1
                self.count_phrases = 1

            self.write_txt("Audio: " + self.audio_path + '/' + self.testwavIds[self.testwavIds_i])
            self.testwavIds_i += 1

            return data, pyaudio.paComplete

        return data, pyaudio.paContinue

    def tcallback_noise(self, in_data, frame_count, time_info, status):
        data = self.noise.readframes(frame_count)

        if self.taudio_progress == 1 or self.tphrases == 1:
            self.noise.close()

            if not is_mac:
                self.stream_n.close()
            self.tphrases = 0

            return data, pyaudio.paComplete

        if len(data) < (2 * frame_count):
            Clock.schedule_once(lambda x: self.tstart_audio(), 0)

        return data, pyaudio.paContinue

    def tstart_audio(self, *kwargs):
        """For the test phase, it starts the masker and target speech signals simultaneously using different threads
        or only the target speech signal if masker does not exist.
        """
        logger.info("function tstart_audio")

        self.threads = []

        if not quiet:
            Clock.schedule_once(lambda x: self.tplay_speech(), speech_on)
            self.threads.append(threading.Thread(target=self.tplay_noise()))
            map(lambda x: x.start(), self.threads)
        else:
            self.tplay_speech()

    def tplay_noise(self):
        """Masker's streaming.
        """
        logger.info("function tplay_noise")

        self.noise = wave.open(
                args.masker,
                'rb')

        maskerchunk_samples = int(maskerchunk * self.noise.getframerate())

        self.stream_n = self.p_noise.open(format=self.p_noise.get_format_from_width(self.noise.getsampwidth()),
                                          channels=self.noise.getnchannels(),
                                          rate=self.noise.getframerate(),
                                          output=True,
                                          stream_callback=self.tcallback_noise, frames_per_buffer=maskerchunk_samples)

    def tplay_speech(self):
        """Target speech streaming.
        """
        logger.info("function tplay_speech")

        if self.testwavIds_i == len(self.testwavIds):
            self.testwavIds_i = 0

        self.audio_path = args.testfolder[self.tmp_fid] + prefix + str(
            self.val)

        logger.info(self.audio_path + '/' + self.testwavIds[self.testwavIds_i])
        self.wf = wave.open(
            self.audio_path + '/' + self.testwavIds[self.testwavIds_i],
            'rb')

        audiochunk_samples = int(audiochunk * self.wf.getframerate())

        self.stream_wf = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
                                     channels=self.wf.getnchannels(),
                                     rate=self.wf.getframerate(),
                                     output=True,
                                     stream_callback=self.tcallback_speech, frames_per_buffer=audiochunk_samples)

    def update(self):
        """Manages the experiment's flow. It is called before each trial.
        """
        logger.info("function update")
        if self.iteration in range(1, numOftrials+1, 1):
            self.current_pos = 0
            self.on_adjustmentphase = True
            self.adj_label.color = [.9, .9, .9, 1]
            self.completion_button.color = [1, 1, 1, .1]
            self.completion_button.background_color = [1, 1, 1, .1]

            if knob:
                self.remove_widget(self.hyper_knob)
                self.hyper_knob.minvalue = lowerlevel
                self.hyper_knob.maxvalue = self.higherlevel + 0.9
                self.hyper_knob.disabled = False
                self.add_widget(self.hyper_knob)

                self.value = lowerlevel
                self.tmp = self.value
                self.hyper_knob.value = lowerlevel + self.higherlevel*0.02
                self.hyper_knob.markeroff_color = [.2, .2, .2, 1]
                self.hyper_knob.disabled = False
                self.hyper_knob.marker_color = [.4, .4, .2, 1]
                self.hyper_knob.background_color = [1, 1, 0, 1]
                self.hyper_knob.max = self.higherlevel
                self.hyper_knob.minvalue = lowerlevel
                self.hyper_knob.maxvalue = self.higherlevel  + 0.9

            else:
                self.tmp = random.randint(lowerlevel, self.higherlevel)
                self.value = self.tmp

                self.button_down.background_color = [1, 1, 1, .7]
                self.button_up.background_color = [1, 1, 1, .7]

                self.button_up.disabled = False
                self.button_down.disabled = False

                if self.value == lowerlevel:
                    self.lower_lim.text = lowlimtxt
                    self.lower_lim.color = [.6, 0, 0, 1]

                elif self.value == self.higherlevel:
                    self.higher_lim.text = uplimtxt
                    self.higher_lim.color = [.6, 0, 0, 1]

            if testphase:
                self.test_label.color = [1, 1, 1, .1]
                self.text_in.background_color = [1, 1, 1, .1]
                self.text_in.disabled = True
                self.i = 1

            self.write_txt("Trial no: " + str(self.trial_no) + " Starting level: " + str(self.value))
            self.iteration += 1
            self.trial_no += 1

            Clock.schedule_once(self.enable_completion_button, button_on)  # time in seconds that button will be enabled
            Clock.schedule_once(self.start_audio, audio_on)  # time in seconds until audio will start
        else:

            if self.tmp_fid == len_adjustmentfolder - 1:
                Clock.schedule_once(self.ending_panel)
            else:
                self.tmp_fid += 1
                self.iteration = 1
                self.block_num += 1
                logger.info("New block!" + str(self.block_num))
                logger.info("------------------------------------")

                if knob:
                    self.remove_widget(self.hyper_knob)
                else:
                    self.remove_widget(self.button_down)
                    self.remove_widget(self.button_up)
                    self.remove_widget(self.higher_lim)
                    self.remove_widget(self.lower_lim)

                if testphase:
                    self.remove_widget(self.text_in)
                    self.remove_widget(self.test_label)

                self.remove_widget(self.adj_label)
                self.remove_widget(self.completion_button)

                Clock.schedule_once(self.starting_panel)

    def write_txt(self, tex):
        """Writes information in the pID_results.txt file.
            A timestamp is also saved with the data.
           tex: Information to be added in the file
        """
        filename = directory +'results/' + str(username) + "_results.txt"

        if not os.path.exists(directory + 'results/'):
            os.makedirs(directory+'results/')

        if os.path.exists(filename):
            fob = open(directory +'results/' + str(username) + "_results.txt", 'a')
        else:
            fob = open(directory +'results/' + str(username) + "_results.txt", 'w')

        fob.write(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + "   ")
        fob.write(tex + "\n")

    def starting_panel(self, *kwargs):
        """Sets instructions and starting button widgets on the screen. If the starting button is pressed,
        the start_controller function is called.
        """
        logger.info("function starting_panel")
        if len(args.adjustmentfolder) > 1:
            self.block_num_label.text = (blktxt + '  ' + str(self.block_num))

        self.layout = RelativeLayout(size=('1000dp', '500dp'))
        self.instr_label.text_size = self.layout.size

        self.add_widget(self.block_num_label)
        self.add_widget(self.start_button)
        self.add_widget(self.instr_label)

    def ending_panel(self, *kwargs):
        """Sets an end message on the screen and exits the SpeechAdjuster.
        """
        logger.info("function ending_panel")
        logger.info("------------------------------------")

        if knob:
            self.remove_widget(self.hyper_knob)
        else:
            self.remove_widget(self.button_down)
            self.remove_widget(self.button_up)
            self.remove_widget(self.higher_lim)
            self.remove_widget(self.lower_lim)

        if testphase:
            self.remove_widget(self.text_in)
            self.remove_widget(self.test_label)

        self.remove_widget(self.adj_label)
        self.remove_widget(self.completion_button)

        endmessage = Label(text=endtxt, pos_hint={'center_x': .5, 'center_y': .5},
                           size_hint=(.28, .05), font_size='50dp', color=(1, 1, 1, .7))
        self.add_widget(endmessage)

        Clock.schedule_once(App.get_running_app().stop, exittime)

class app(App):

    def build(self):
        return SpeechAdjuster()

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    app().run()

if __name__ == "__main__":
     sys.exit(main())
