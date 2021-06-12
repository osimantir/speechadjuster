#######################################################
## This script generates csv format files
## and plots with the listeners' responses.
#######################################################
#######################################################
## Author: Olympia Simantiraki
## License: GNU GPL v3
## Version: v1.0.0
## Email: olina.simantiraki@gmail.com
#######################################################

import pandas as pd
from datetime import datetime
import numpy as np
import os
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib import colors
import sys
from configparser import ConfigParser,NoSectionError, NoOptionError
import argparse
import logging
import filecmp


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create a file handler
handler = logging.FileHandler('logfile.log', mode='a')
handler.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter('%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
handler.setFormatter(formatter)
# add the file handler to the logger
logger.addHandler(handler)
logger.info("------------------------------------")
logger.info("The script results.py has started.")

parser = ConfigParser()
# get the path to config.ini
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
parser.read(config_path)

parser2 = argparse.ArgumentParser(prog='PROG',description='results.py (part of SpeechAdjuster tool): The arguments for running this script should be '
                                                          'identical to those used for running the main module SpeechAdjuster.py. It creates .csv files of the collected data and stores them in the folder called results: '
                                                          'one file with the username passed in the arguments and an aggregate .csv file called alldata.csv '
                                                          'in which the data of all participants are concatenated. It also generates plots with results and stores them under the folder called plots.')
parser2.add_argument('-u', '--username', type=str, help='Participant unique ID. (type: string)')
parser2.add_argument('-a','--adjustmentfolder', type=str, help='Path(s) to target speech folders (e.g. ﻿stimuli/examples/tilt/adjustment/) for the adjustment phase. If more than one split them with commas without using spaces. (type: strings with comma delimiter)')
parser2.add_argument('-t','--testfolder', type=str, help='Path(s) to target speech folders (e.g. stimuli/examples/tilt/test/) for the test phase. If more than one split them with commas without using spaces. The total number of paths provided for the test '
                                                         'phase should be equal to those provided for the adjustment phase. If paramenter is empty, trials do not consist of a test phase.'
                                                         '(type: strings with comma delimiter)')
parser2.add_argument('-m', '--masker', type=str, help='Path with masker filename (e.g. stimuli/maskers/SSN.wav). If paramenter is empty, target speech is presented in quiet. (type: string)')
args = parser2.parse_args()
try:
    args = parser2.parse_args()
    logger.info(args)
except SystemExit:
    exc = sys.exc_info()[1]
    logger.error(exc)

try:
    logger.info("Parameters checking has started. ")
    username = args.username
    maskerfile = args.masker
    adjustmentfolder = args.adjustmentfolder
    testfolder =  args.testfolder
    prefix = parser.get('stimuli', 'prefix')
    numOftrials=parser.getint('setup_adj', 'numOftrials')
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

    assert numOftrials > 0, logger.error('The paramenter numOftrials should be greater than zero.')
    assert speech_on >= 0, logger.error('The parameter speech_on should be greater than or equal to zero.')
    assert exittime >= 0, logger.error('The parameter exittime should be greater than or equal to zero.')
    assert numOftesting > 0, logger.error('The parameter numOftesting should be greater than zero.')
    assert test1audio >= 0, logger.error('The parameter test1audio should be greater than or equal to zero.')
    assert testaudio >= 0, logger.error('The parameter testaudio should be greater than or equal to zero.')
    assert button_on >= audio_on, logger.error('The parameter button_on should be greater than or equal to the parameter audio_on.')
    assert audio_on >= 0, logger.error('The parameter audio_on should be greater than or equal to zero.')
    assert gap >= 0, logger.error('The parameter gap should be greater than or equal to zero.')
    assert adjustmentfolder, logger.error('The argument adjustmentfolder should not be empty.')
    assert username, logger.error('The argument username should not be empty.')
    assert audiochunk > 0, logger.error('The parameter audiochunk should be greater than zero.')
    assert maskerchunk > 0, logger.error('The parameter maskerchunk should be greater than zero.')

except AssertionError as error:
    sys.exit("[ERROR] in configuration file or in command line arguments.")
except ValueError:
    logger.error(
            '[ERROR] wrong parameter type. Check again the types of the parameters  in congig.ini and command line. \n '
            'Parameters of type integer, float, boolean cannot be empty.')
    sys.exit('[ERROR] wrong parameter type. Check again the types of the parameters  in congig.ini and command line. \n '
            'Parameters of type integer, float, boolean cannot be empty.')
except (NoSectionError, NoOptionError):
    logger.error(
        '[ERROR] in configuration file. All the parameters and section titles should be out of comments.')
    sys.exit(
        '[ERROR] in configuration file. All the parameters and section titles should be out of comments.')

if maskerfile:
    if not os.path.exists(maskerfile):
        logger.error("Masker file " + maskerfile + " does not exist.")
        sys.exit()

if not os.path.exists(directory + 'plots'):
    os.makedirs(directory + 'plots')
adjustmentfolder = adjustmentfolder.split(',')
len_adjustmentfolder = len(adjustmentfolder)
lowerlevel = 1

max_highlevel=0

for k in range(0, len_adjustmentfolder):
    if len(next(os.walk(adjustmentfolder[k]))[1]) == 1:
        logger.error(
            'More than one levels/folders should exist.')
        sys.exit("[ERROR] More than one levels/folders should exist.")

    # find the max of the highlevels of all blocks
    if len(next(os.walk(adjustmentfolder[k]))[1]) > max_highlevel:
        max_highlevel = len(next(os.walk(adjustmentfolder[k]))[1])


if not testfolder:
    testphase = False
    numOftesting = 0
else:
    testphase = True
    testfolder = testfolder.split(',')
    len_testfolder = len(testfolder)

    if len_testfolder != len_adjustmentfolder:
        logger.error(
            'The total number of paths provided in the command line for the test phase should be equal to that provided for the adjustment phase.')
        sys.exit(
            "[ERROR] The total number of paths provided in the command line for the test phase should be equal to that provided for the adjustment phase.")
    for j in range(0, len(testfolder)):
        testfolder[j] = testfolder[j] + '/'
        for i in range(lowerlevel, len(next(os.walk(adjustmentfolder[j]))[1]) + 1):
            if not os.path.exists(testfolder[j] + prefix + str(i)):
                logger.error('Test phase: folder ' + testfolder[j] + prefix + str(
                    i) + " does not exist. In the directory  " + testfolder[
                                 j] + " only the folders with the target speech stimuli should exist starting with the prefix " + prefix +
                             '.\n All the folders with integer IDs from 1 to the maximum number of levels with step 1 should exist.\n The total number of levels/folders provided in the directory for the test phase should be equal to that provided for the adjustment phase.')
                sys.exit('[ERROR] Test phase: folder ' + testfolder[j] + prefix + str(
                    i) + " does not exist. In the directory  " + testfolder[
                             j] + " only the folders with the target speech stimuli should exist starting with the prefix " + prefix +
                         '.\n All the folders with integer IDs from 1 to the maximum number of levels with step 1 should exist.\n The total number of levels/folders provided in the directory for the test phase should be equal to that provided for the adjustment phase.')

            dcmp = filecmp.dircmp(testfolder[j] + prefix + str(lowerlevel) + '/',
                                  testfolder[j] + prefix + str(i) + '/')
            if '.DS_Store' in dcmp.left_only: dcmp.left_only.remove('.DS_Store')
            if '.DS_Store' in dcmp.right_only: dcmp.right_only.remove('.DS_Store')
            res_left = [x for x in dcmp.left_only if re.search('.wav', x)]
            res_right = [x for x in dcmp.right_only if re.search('.wav', x)]

            if len([name for name in os.listdir(testfolder[j] + '/' + prefix + str(i)) if
                    name.endswith(".wav")]) == 0:
                sys.exit('[ERROR] The directory ' + testfolder[j] + prefix + str(
                    i) + '  does not contain .wav files.')
                logger.error('[ERROR] The directory ' + testfolder[j] + prefix + str(
                    i) + '  does not contain .wav files.')

            if len(dcmp.left_only) > 0 or len(dcmp.right_only) > 0:
                logger.error(
                    'All the levels/folders in the same directory should contain .wav files with the same filenames.')
                logger.error(
                    'Files only in directory ' + testfolder[j] + prefix + str(lowerlevel) + '/' + '  : ' + str(
                        dcmp.left_only))
                logger.error('Files only in directory ' + testfolder[j] + prefix + str(i) + '/' + '  : ' + str(
                    dcmp.right_only))
                sys.exit(
                    "[ERROR] Test phase: file does not exist. \nAll the levels/folders in the same directory should contain .wav files with the same filenames.\n\n" +
                    'Different files in directory ' + testfolder[j] + prefix + str(
                        lowerlevel) + '/' + '  : ' + str(dcmp.left_only) + '\nDifferent files in directory ' +
                    testfolder[j] + prefix + str(i) + '/' + '  : ' + str(dcmp.right_only))

logger.info("Parameters checking has ended successfully. ")

cdict = {'red':   ((0.0, 0.0, 0.0),
                   (0.5, 0.0, 1.0),
                   (1.0, 0.1, 1.0)),

         'green': ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),

         'blue':  ((0.0, 0.0, 0.1),
                   (0.5, 1.0, 0.0),
                   (1.0, 0.0, 0.0))
        }

cmap = colors.LinearSegmentedColormap('custom', cdict)

def datatocsv():
    """datatocsv function reads the pID_results.txt and generates the pID.csv. The file is stored under the folder called results.
        It also generates a plot with the target speech level adjustments that the listener has performed during each trial. The
        plot is saved under the folder called plots.
    """
    logger.info("function datatocsv")
    StartToMatch = "Trial no:"
    EndToMatch = "end of adjusting"
    Response_inline = "Response"
    target_audio_inline = "Audio"
    level_inline = 'level = '
    blk = 'Block :'
    tgtpath = 'Target audio path :'
    stabilization = []
    target_audio = []
    response = []
    trial_no=[]
    starting_level=[]
    fullpath = []
    pref_level=[]
    tr= []
    stps=[]
    blknum = []
    tpath=[]
    fig1 = Figure(figsize=(5, 5), dpi=200)
    block_no = 0

    higherlevel = len(next(os.walk(adjustmentfolder[block_no]))[1])

    with open('results/' + username +'_results.txt') as input_data:
        for line in input_data:
            if StartToMatch in line:
                original_word1 = line
                original_word1_split = original_word1.split(" ")
                trial_no.append(original_word1_split[6])
                starting_level.append(original_word1_split[9].replace('\n',''))

            if level_inline in line:
                line = line.replace('\n', '')
                stps.append(line)

            if EndToMatch in line:
                if stps!=[]:
                    tr = [tr, stps]
                s1 = original_word1[11:23]
                original_word3 = line
                s2 = original_word3[11:23]
                FMT = '%H:%M:%S.%f'
                tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
                tmp = tdelta.seconds + tdelta.microseconds * 0.000001
                # stab_time= float(tmp) - audio_on
                stab_time = float(tmp)

                stabilization.append(stab_time)

                # ax = fig1.add_subplot(111)

                time=[]
                pref=[]
                time.append(0)
                pref.append(float(starting_level[-1]))

                for i in stps:
                    stps_t = i.split(" ")
                    tdelta = datetime.strptime(stps_t[1], FMT) - datetime.strptime(s1, FMT)
                    tmp = tdelta.seconds + tdelta.microseconds * 0.000001
                    pref.append(float(stps_t[-1]))
                    time.append(tmp)

                time.append(stab_time+audio_on)
                pref.append(pref[-1])
                clr = np.random.randint(1,255)

                ax = fig1.add_subplot(111)
                ax.plot(time[1:-1], pref[1:-1], 'o-', color=cmap(clr), linewidth=.5);
                # ax.plot(time, pref, color=cmap(clr), linewidth=.5);

                pref_level.append(int(pref[-1]))
                ax.axis(ymax=higherlevel + 1, ymin=lowerlevel - 1)

                ax.set_ylabel('Adjustments')
                ax.set_xlabel('Time (sec)')

                ax.set_title('Block ' + str(blknum[len(blknum)-1]))

                stps=[]

            line = line.replace('\n', '')
            if target_audio_inline in line:
                line_split=line.split(" ")
                ftarget_audio = line_split[5].split('/')
                fullpath.append(line_split[5:])
                target_audio.append(ftarget_audio[-1])
            if blk in line:
                line_split = line.split(" ")
                blknum.append(line_split[-1])
                block_no += 1
                if block_no > 1:
                    higherlevel = len(next(os.walk(adjustmentfolder[block_no-1]))[1])

                fig1.legend(trial_no, title="trial no")
                if line_split[-1]!='1':
                    canvas = FigureCanvasAgg(fig1)
                    ax.vlines(button_on, ymax=max_highlevel + 1, ymin=lowerlevel - 1, color='grey', linestyle='--')
                    fig1.savefig(directory + 'plots/' + str(username) + '_block'+str(blknum[len(blknum)-2])+ 'adjustments.pdf')
                    fig1 = Figure(figsize=(5, 5), dpi=200)

            if Response_inline in line:
                line_split = line.split(" ")
                response.append(line_split[5:])
            if tgtpath in line:
                line_split = line.split(" ")
                tpath.append(line_split[-1])
    fig1.legend(trial_no, title="trial no")
    if len(blknum) == 1:
        canvas = FigureCanvasAgg(fig1)
        # fig1.legend(trial_no, title="trial no")
        ax.vlines(button_on, ymax=higherlevel + 1, ymin=lowerlevel - 1, color='grey', linestyle='--')
        fig1.savefig(directory + 'plots/' + str(username) + '_block1' + 'adjustments.pdf')
    else:
        canvas = FigureCanvasAgg(fig1)
        ax.vlines(button_on, ymax=higherlevel + 1, ymin=lowerlevel - 1, color='grey', linestyle='--')
        fig1.savefig(directory + 'plots/' + str(username) + '_block' + str(blknum[len(blknum) - 1]) + 'adjustments.pdf')

    if testphase:
        stabilization = np.repeat(stabilization, repeats=numOftesting, axis=0)
        trial_no = np.repeat(trial_no, repeats=numOftesting, axis=0)
        starting_level = np.repeat(starting_level, repeats=numOftesting, axis=0)
        pref_level = np.repeat(pref_level, repeats=numOftesting, axis=0)

        blknum = np.repeat(blknum, repeats=numOftrials*numOftesting, axis=0)
    else:
        blknum = np.repeat(blknum, repeats=numOftrials, axis=0)

    df = pd.DataFrame()
    df['pID'] = np.repeat(str(username), repeats=len(trial_no), axis=0)
    df['knob'] = knob
    df['block'] = blknum
    df['teston'] = testphase
    df['trial_no'] = trial_no
    df['starting_level'] = starting_level
    df['stabilization_time'] = stabilization
    df['pref_level'] = pref_level

    if testphase and maskerfile=='':
        df['target_audio'] = target_audio
        df['response'] = response
        df['fullpath'] = fullpath
        df['masker'] = float('nan')

    elif testphase:
        df['target_audio'] = target_audio
        df['response'] = response
        df['fullpath'] = fullpath
        df['masker'] = np.repeat(maskerfile, repeats=len(df['fullpath']), axis=0)

    elif maskerfile!='':
        df['target_audio'] = float('nan')
        df['response']= float('nan')
        df['fullpath'] = np.repeat(tpath, repeats=numOftrials, axis=0)
        df['masker'] = np.repeat(maskerfile, repeats=len(df['starting_level']), axis=0)

    else:
        df['target_audio'] = float('nan')
        df['response'] = float('nan')
        df['fullpath'] = np.repeat(tpath, repeats=numOftrials, axis=0)
        df['masker'] = float('nan')

    df.to_csv(directory + 'results/' + username + '.csv', index=False,
                  header=['pID','knob','block','teston','trial_no', 'starting_level', 'stabilization_time', 'pref_level','target_audio', 'response', 'fullpath', 'masker'])

def plot_data():
    """plot_data function reads the pID.csv and adds the new participant's data in the aggregate file alldata.csv which is
        stored under the folder called results. If alldata.csv does not exist it creates it.
        Additionally, it generates plots with the results of all participants. The plots are saved under the folder called plots.
    """
    logger.info("function plot_data")
    if os.path.exists(directory + 'results/' + username + '.csv'):
        df = pd.read_csv(directory + 'results/' + username + '.csv', delimiter=',')
    else:
        print(directory + 'results/' + username + '.csv' ' does not exist. ')
        return
    if os.path.exists(directory + 'results/alldata.csv'):
        data = pd.read_csv(directory + 'results/alldata.csv', delimiter=',')
        data = data.append(df)
    else:
        data = df

    data.to_csv(directory + 'results/alldata.csv', index=False,
              header=['pID','knob','block','teston','trial_no', 'starting_level', 'stabilization_time', 'pref_level','target_audio', 'response', 'fullpath', 'masker'])

    fig3 = Figure(figsize=(5, 5), dpi=200)
    fig7 = Figure(figsize=(5, 5), dpi=200)
    ax3 = fig3.add_subplot(111)
    ax7 = fig7.add_subplot(111)
    j=[]

    for i in range(1,data['block'].max()+1):
        dt1 = data[data['block'] == i].reset_index(drop=True)
        fig2 = Figure(figsize=(5, 5), dpi=200)
        canvas = FigureCanvasAgg(fig2)
        ax2 = fig2.add_subplot(111)
        higherlevel = len(next(os.walk(adjustmentfolder[i-1]))[1])
        ax2.hist(dt1['pref_level'])
        ax2.axis(xmax=higherlevel + 1, xmin=lowerlevel - 1)
        ax2.set_title('Listener preferences')
        ax2.set_ylabel('Frequency')
        ax2.set_xlabel('Available options (levels)')
        ax2.set_title('Block ' + str(i))
        fig2.savefig(directory+ 'plots/block' + str(i) + 'hist.pdf')

        ax3.boxplot(dt1['stabilization_time'], positions=[i])
        ax3.set_ylabel('Stabilization time (sec)')
        ax3.set_xlabel('Block')
        ax3.axhline(y=button_on, color='grey', linestyle='--')

        ax7.boxplot(dt1['pref_level'], positions=[i])
        ax7.set_ylabel('Listener preferences')
        ax7.set_xlabel('Block')
        ax7.axhline(y=lowerlevel, color='grey', linestyle='--')
        ax7.axhline(y=max_highlevel, color='grey', linestyle='--')
        ax7.axis(ymax=max_highlevel + 1, ymin=lowerlevel - 1)
        j.append(str(i))

    ax3.set_xticks(range(1,data['block'].max()+1))
    ax3.set_xticklabels(j)
    ax3.set_xlim(0, data['block'].max() + 1)
    canvas = FigureCanvasAgg(fig3)
    fig3.savefig(directory+ 'plots/boxplotstabtime.pdf')
    ax7.set_xticks(range(1, data['block'].max() + 1))
    ax7.set_xticklabels(j)
    ax7.set_xlim(0, data['block'].max() + 1)
    canvas = FigureCanvasAgg(fig7)
    fig7.savefig(directory + 'plots/boxplotprefs.pdf')

    dataton = data[data['teston']==True].reset_index(drop=True)

    if dataton.empty:
        pass
    else:
        import matplotlib.pyplot as plt

        for i in range(1, dataton['block'].max() + 1):
            fig6 = Figure(figsize=(10, 10), dpi=200)
            dt1 = dataton[dataton['block'] == i].reset_index(drop=True)

            p_id = dt1["pID"].unique()
            ax_main = fig6.add_subplot(111)

            wavfs = dt1["target_audio"].unique()
            all_prefs = [None] * len(p_id)


            for pts in range(0,len(p_id)):
                p_val = [-1] * len(wavfs)
                for wvs in range(0,len(wavfs)):
                    cur_prt = dt1[dt1["pID"] == p_id[pts]].reset_index(drop=True)
                    for tmp in range(0, len(cur_prt['target_audio'])):
                        if cur_prt['target_audio'][tmp]==wavfs[wvs]:
                            p_tmp = cur_prt.loc[cur_prt['target_audio'] == wavfs[wvs]]
                            p_val[wvs] = p_tmp['pref_level'][tmp]

                all_prefs[pts]=np.array(p_val)

            all_prefs = np.array(all_prefs)
            im = ax_main.imshow(all_prefs, cmap='Greens')
            # im = ax_main.imshow(all_prefs, cmap=plt.cm.winter)
            #  im = ax_main.imshow(all_prefs,cmap=plt.cm.RdBu)

            for pts in range(0,len(p_id)):
                for j in range(0, len(wavfs)):
                    text = ax_main.text(j, pts, all_prefs[pts,j], ha="center", va="center", color="black", fontweight='bold')

            ax_main.set_xticks(np.arange(len(wavfs)))
            ax_main.set_xticklabels(wavfs)
            ax_main.set_yticks(np.arange(len(p_id)))
            ax_main.set_yticklabels(p_id)
            ax_main.set_ylabel('Participant ID')
            ax_main.set_xlabel('Stimulus')
            plt.setp(ax_main.get_xticklabels(), rotation=45, ha="right",
                     rotation_mode="anchor")
            plt.setp(ax_main.get_yticklabels(), rotation=45, ha="right",
                     rotation_mode="anchor")

            canvas = FigureCanvasAgg(fig6)
            fig6.savefig(directory + 'plots/block' +str(i)+ 'heatmap.pdf')


def main(args=None):
    print("Hello " + str(username) + "!")
    logger.info("function main")
    if not os.path.exists(directory + 'results/' + username + '.csv'):
        datatocsv()
    plot_data()

if __name__ == "__main__":
     sys.exit(main())