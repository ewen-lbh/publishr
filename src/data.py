import json
import logging
import os
import re
import sys
import webbrowser
from collections import namedtuple

from src import ui, shared


def get(config, utils):
    def get_description(**data):
        langs = config.get('description/languages')
        descs = dict()
        for lang in langs:
            file = schemes.apply('description/file', lang=lang, **data)
            if os.path.isfile(file):
                logging.debug(f'Found a description file for language {lang}')
                with open(file, 'r') as f:
                    descs[lang] = f.read()
            else:
                logging.warning(f'Description file not found for language {lang}')
                descs[lang] = ui.text(f'description({lang})')
        return descs

    def get_kind(tracks):
        if len(tracks) >= 4:
            kind = 'Album'
        elif len(tracks) >= 1:
            kind = 'EP'
        else:
            kind = 'Single'

        return ui.ask('kind', choices=('Single', 'EP', 'Album'), default=kind)

    def get_tracks(title):

        any_remixes = ui.ask('at least one remix', choices='yn', default='no')

        tracks = list()
        dir = schemes.apply('paths/dirs/audios', title=title, slug=slug)
        dirlist = utils.listdir(dir)

        logging.info(f"Found {len(dirlist)} {shared.plural('track', len(dirlist))}")

        for filename in dirlist:
            if not re.match(r'.+\.mp3$', filename):
                logging.debug(f'Skipping file "{filename}"')
                continue

            logging.info(f'Audio file "{filename}"...')

            # determinate if it's a remix or not
            if any_remixes:
                is_remix = ui.ask('remix', choices='yn', default='no')
            else:
                is_remix = False

            if is_remix:
                artist = ui.ask('Original artist')
            else:
                artist = config.get('defaults/artist')

            # extract track info
            try:
                trackinfo = schemes.extract('paths/files/audios', filename)[0]
            except ValueError:
                try:
                    trackinfo = schemes.extract('paths/renamed/audios', filename)[0]
                except ValueError:
                    logging.fatal(f'The audio file "{filename}" does not match any scheme (neither paths/files/audios nor paths/files/renamed)')

            trackinfo['filename'] = filename
            trackinfo['artist'] = artist
            tracknum = trackinfo['tracknum']


            # set track title
            title = schemes.apply('titles/' + ('remix' if is_remix else 'track'), **trackinfo)
            if config.get('options/confirm/track-title'):
                title = ui.ask('Track name', default=title)
            trackinfo['title'] = title

            # set track number
            if config.get('options/confirm/track-number'):
                tracknum = ui.ask('Track #', default=tracknum)
            trackinfo['tracknum'] = tracknum

            # add to tracks data list
            tracks.append(trackinfo)

        return tracks

    if os.path.isfile(config.get('paths/misc/track_data')):
        if not config.get('options/automatic/recover'):
            recover = False
            if ui.ask('Recover song data from latest run ?', choices='yn'):
                recover = True
        else:
            recover = True
    else:
        recover = False


    if recover:
        with open(config.get('paths/misc/track_data'), 'r') as f:
            json_raw = f.read()
        data = json.loads(json_raw)
    else:
        schemes = shared.Schemer(config, None)

        title = ui.ask('Title')
        slug = ui.ask('Title slug', default=shared.slugify(title))

        tracks = get_tracks(title)

        kind = get_kind(tracks)

        descriptions = get_description(title=title, kind=kind, slug=slug)

        # data dict
        data = {
            "title": title, "slug": slug, "tracks": tracks, "kind": kind, "descriptions": descriptions
        }

        with open(config.get('paths/misc/track_data'),'w') as f:
            json_raw = json.dumps(data, indent=4)
            f.write(json_raw)


    return data
