SpeechAdjuster is an open-source software tool for acquiring listener preferences
and intelligibility scores. Listeners are allowed to adjust speech characteristics
in real-time by using a virtual interface. SpeechAdjuster is not a
speech processing tool thus the user has to generate the stimuli (e.g., target
speech, noise) prior to its use. The use of pre-computed stimuli gives the advantage
that almost any speech transformation, of arbitrary complexity, can
be investigated. As an example, the acquired information from such tests
can be used in speech enhancement algorithms for defining the proper balance
between intelligibility and supra-intelligibility aspects of speech such
as listening effort, quality, naturalness, and pleasantness.  

To install, use pip install speechadjuster, 
then below that, if you want to test the 
tool, download the stimuli from this link https://github.com/osimantir/stimuli.git. 

Contributors   

Olympia Simantiraki (olina.simantiraki@gmail.com)<br/> 
Martin Cooke (m.cooke@ikerbasque.org)


Citing

If you use this tool, please cite the following publication: 

@inproceedings{Simantiraki21,
  author="Simantiraki, O. and Cooke, M.",
  title="{SpeechAdjuster: A tool for investigating listener preferences and speech intelligibility}",
  year="2021",
  booktitle="Proc. Interspeech", 
  note="in press"
  }