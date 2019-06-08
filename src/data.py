import json
import logging
import os
import re
import sys
import webbrowser
from collections import namedtuple

from src import ui, shared
from src.internalconf import COVER_ART_FORMATS


def get(config, utils):
    def get_description(**data):
        langs = config.get('description-languages')
        descs = dict()
        for lang in langs:
            file = schemes.apply('paths/files/descriptions', lang=lang, **data)
            file = os.path.realpath(os.path.normpath(file))
            logging.info(f'Searching for file {file}')
            if os.path.isfile(file):
                logging.debug(f'Found a description file for language {lang}')
                with open(file, 'r') as f:
                    descs[lang] = f.read()
            else:
                logging.warning(f'Description file not found for language {lang}')
                descs[lang] = ui.text(f'description({lang})')
                if config.get('options/save-descriptions'):
                    logging.info(f'Saving description to file "{file}"...')
                    with open(file, 'w', encoding='utf8') as f:
                        f.write(descs[lang])
        return descs

    def get_kind(tracks):
        if len(tracks) >= 4:
            kind = 'Album'
        elif len(tracks) >= 1:
            kind = 'EP'
        else:
            kind = 'Single'

        return ui.ask('kind', choices=('Single', 'EP', 'Album'), default=kind)

    def get_artist(tracks):
        deduped_artists = list(set([e['artist'] for e in tracks]))
        if len(deduped_artists) >= 1:
            artist = deduped_artists[0]
        if len(deduped_artists) < int(config.get('various-artists/threshold')):
            artist = config.get('various-artists/separator').join(deduped_artists)
        else:
            artist = config.get('various-artists/default-name')
            if config.get('various-artists/ask'):
                artist = ui.ask("Collection artist", default=artist)

        return artist

    def get_tracks(title):

        any_remixes = ui.ask('at least one remix', choices='yn', default='no')

        tracks = list()
        # whatever filename, since we only do this to get the dirname
        directory = os.path.dirname(schemes.apply('paths/files/audios', title=title, slug=slug, filename='whatever'))
        dirlist = list()
        for file in utils.listdir(directory):
            patt = config.get('paths/files/audios').replace('<filename>','.+')
            patt = re.compile(patt)

            if patt.match(os.path.join(directory, file)):
                dirlist.append(file)
            else:
                logging.debug(f'File "{file}" does not match pattern "{patt}"')
        

        if len(dirlist):
            logging.info(f"Found {len(dirlist)} valid {shared.plural('file', len(dirlist))}")
        else:
            logging.fatal("No tracks where found.")
            logging.info(f"Make sure that your file names matches the following pattern: {os.path.split(config.get('paths/files/audios'))[1]}")
            if config.get('options/automatic/open-dirs'):
                logging.info(f"Opening directory {directory}")
                webbrowser.open(directory)
            sys.exit(1)

        if config.get('options/show-audiofiles-dirlist'):
            files = str()
            for file in dirlist:
                files += '\n'+(' '*(8+3) + str(os.path.split(file)[1]))
            logging.info(f"Files in directory {directory}:{files}")

        for filename in dirlist:
            if not re.match(r'.+\.mp3$', filename):
                logging.debug(f'Skipping file "{filename}": is not a .mp3 file')
                continue

            logging.info(f'Audio file "{filename}"...')
            if not config.get('options/all-audios-are-final-versions'):
                if not ui.ask('Is this file the latest version ?', choices='yn'):
                    continue

            # turns into an absolute path
            filename = os.path.join(directory, filename)

            # determinate if it's a remix or not
            if any_remixes:
                is_remix = ui.ask('remix', choices='yn', default='no')
            else:
                is_remix = False

            if is_remix:
                artist = ui.ask('Original artist')
            else:
                artist = config.get('defaults/artist')

            # ask for basic track info
            trackinfo = dict()
            trackinfo['tracknum'] = int(ui.ask('Track number', choices=list(range(2,len(dirlist)))))
            trackinfo['track_title'] = ui.ask('Track title', default=os.path.splitext(os.path.split(filename)[1])[0])

            # set basic track info
            trackinfo['filename'] = filename
            trackinfo['artist'] = artist
            trackinfo['title'] = title
            tracknum = trackinfo['tracknum']

            # set video if file exists
            videopath = schemes.apply('paths/files/videos', **trackinfo)
            videopath2 = schemes.apply('paths/renamed/videos', **trackinfo)
            if os.path.isfile(videopath):
                trackinfo['video'] = videopath
            elif os.path.isfile(videopath2):
                trackinfo['video'] = videopath2
            else:
                trackinfo['video'] = False

            # add to tracks data list
            tracks.append(trackinfo)

        return tracks

    def get_coverarts(**data):
        cover_arts = dict()
        for format in COVER_ART_FORMATS:
            cover_arts[format] = dict()

            fulldata = dict(**data, format=format)
            fres_path = schemes.apply('paths/files/covers', **fulldata)
            lres_path = schemes.apply('paths/files/covers-lowres', **fulldata)

            if os.path.isfile(fres_path):
                logging.info(f'Found {format} cover art: {os.path.split(fres_path)[1]}')
                cover_arts[format]['full_res'] = fres_path
            else:
                cover_arts[format]['full_res'] = False
                if format == 'wide':
                    logging.fatal(f'You need at least a wide, full resolution cover art: {fres_path}')

            if os.path.isfile(lres_path):
                logging.info(f'Found low resolution {format} cover art: {os.path.split(lres_path)[1]}')
                cover_arts[format]['low_res'] = lres_path
            else:
                cover_arts[format]['low_res'] = False

        return cover_arts

    if os.path.isfile(config.get('paths/misc/track_data_file')):
        if not config.get('options/automatic/recover'):
            recover = False
            if ui.ask('Recover song data from latest run ?', choices='yn'):
                recover = True
        else:
            recover = True
    else:
        recover = False

    if recover:
        with open(config.get('paths/misc/track_data_file'), 'r') as f:
            json_raw = f.read()
        data = json.loads(json_raw)
    else:
        schemes = shared.Schemer(config, None)

        title = ui.ask('Title')
        slug = ui.ask('Title slug', default=shared.slugify(title))

        tracks = get_tracks(title)

        kind = get_kind(tracks)
        artist = get_artist(tracks)

        descriptions = get_description(title=title, kind=kind, slug=slug)
        cover_arts = get_coverarts(title=title, kind=kind, slug=slug)

        # data dict
        data = {
            "title"            : title,
            "slug"             : slug,
            "tracks"           : tracks,
            "kind"             : kind,
            "descriptions"     : descriptions,
            "cover_arts"       : cover_arts,
            "collection_artist": artist
        }

        with open(config.get('paths/misc/track_data_file'), 'w') as f:
            json_raw = json.dumps(data, indent=4)
            f.write(json_raw)

    return data