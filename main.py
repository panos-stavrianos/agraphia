import json
import subprocess
import glob
import inflect
import questionary


def ask_for_order(choices):
    p = inflect.engine()
    i = 1
    ordered = []
    while len(choices) > 1:
        answer = questionary.select(
            f'Choose the {p.number_to_words(p.ordinal(i))} Playlist',
            choices=choices).ask()  # returns value of selection
        ordered.append(answer)
        choices.remove(answer)
        i += 1
    ordered.append(choices[0])
    return ordered


def select_playlists():
    files = glob.glob('playlists/*.m3u')
    files = list(map(lambda x: {'name': x}, files))
    answers = questionary.checkbox(
        'Select Playlists',
        choices=files,
        validate=lambda val: len(val) > 0
    ).ask()

    return ask_for_order(answers)


def start_vlc(playlists):
    playlists_formatted = list(map(lambda x: f'"{x}"', playlists))

    with open('config.json', 'r') as json_file:
        config = json.load(json_file)
    address = '{username}:{password}@{ip}:{port}/{mount}'.format(**config)
    rest = '--sout="#transcode{vcodec=none,acodec=vorb,ab=128,channels=2,samplerate=44100,scodec=none}:std{' \
           'access=shout,mux=ogg,dst=//' + address + '}" '
    cmd = ' '.join(['vlc', *playlists_formatted, rest, '--no-sout-all', '--sout-keep', '--loop'])
    subprocess.Popen(cmd, shell=True).communicate()


playlists = select_playlists()
print(start_vlc(playlists))
