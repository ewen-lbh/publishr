import datetime
import logging
import os

import eyed3

from src import shared, ui


class Renamer:
    def __init__(self, config, data):
        self.data = data
        self.config = config
        self.schemes = shared.Schemer(config, data)

    def map(self):
        ret = dict()
        newtracksdata = self.data.get('tracks')
        for i, track in enumerate(self.data.get('tracks')):
            src = track.get('filename')
            dst = self.schemes.apply('paths/renamed/audios', **track)
            if src != dst:
                ret[src] = dst
            newtracksdata[i]['filename'] = dst


        return ret, newtracksdata

    def rename(self):
        rename_map, newtracksdata = self.map()

        for src, dst in rename_map.items():
            logging.info(f"Rename {src} --> {dst}")
            os.rename(self.schemes.fullpath('audios', src),
                      self.schemes.fullpath('audios', dst))
            self.data['tracks'] = newtracksdata


def rename(config, data):
    renamer = Renamer(data=data, config=config)
    rename_map, _ = renamer.map()
    if len(rename_map) < 1:
        logging.debug(f"Found no files to rename. (all tracks filename match dirs/renamed/audios)")
        return True

    if config.get('options/confirm/rename-tracks'):
        print(ui.pprint_dict(rename_map, sep='--> '))
        if not ui.ask('Rename ?', choices='yn', default='y'):
            return False

    renamer.rename()
    return True

class Metadata:
    def __init__(self, config, data):
        self.config = config
        self.data = data
        self.schemes = shared.Schemer(config, data)

    def preview(self):
        # get date components for eyed3's custom Date() class
        date_y = int(datetime.date.today().strftime('%Y'))
        date_m = int(datetime.date.today().strftime('%m'))
        date_d = int(datetime.date.today().strftime('%d'))
        # get total count of tracks
        tracklist = self.data.get('tracks')
        total = len(tracklist)

        metadata = {
            "Artist"        : self.data.get('artist'),
            "Album"         : self.data.get('title'),
            "Cover art"     : self.schemes.get('paths/renamed/covers', format='square'),
            "Date"          : f'{date_d}/{date_m}/{date_y}',
            "Title"         : ui.colored('track\'s title', color='red'),
            "Track number"  : ui.colored(f'1-{total}', color='red') + f'/{total}'
        }

        return metadata

    def apply(self, metadata=None):
        if not metadata:
            metadata = self.preview()

        date_y = int(datetime.date.today().strftime('%Y'))
        date_m = int(datetime.date.today().strftime('%m'))
        date_d = int(datetime.date.today().strftime('%d'))
        applied_count = 0
        for track in self.data.get('tracks'):

            filename = track["filename"]
            logging.debug(f'Loading "{filename}" into eyed3...')
            audiofile = eyed3.load(os.path.join(self.schemes.get('paths/dirs/audios'), filename))

            # artist
            audiofile.tag.artist = audiofile.tag.album_artist = metadata['Artist']
            # title
            audiofile.tag.title = track['title']
            # album title
            audiofile.tag.album = metadata['Album']
            # track number (current, total)
            audiofile.tag.track_num = (track['tracknum'], len(self.data.get('tracks')))
            # release date YYYY-MM-dd
            audiofile.tag.original_release_date = eyed3.core.Date(year=date_y, day=date_d, month=date_m)
            audiofile.tag.release_date = eyed3.core.Date(year=date_y, day=date_d, month=date_m)
            # album arts (type, imagedata, imagetype, description)
            audiofile.tag.images.set = (
            3, metadata['Cover art'], 'image/png', self.config.get('defaults/covers-description'))

            logging.debug(f'Saving tags into {filename}...')
            try:
                audiofile.tag.save()
                applied_count += 1
            except Exception as e:
                logging.error('eyed3 error:' + str(e))

        logging.info(f'Applied metadata to {applied_count} audio file{"s" if applied_count != 1 else ""}')

def metadata(config, data):
    metadatator = Metadata(config, data)
    if config.get('options/confirm/apply-metadata'):
        preview = metadatator.preview()
        logging.info("The following metadata will be applied:")
        ui.pprint_dict(preview)
        if not ui.ask('Apply ?', choices='yn', default='y'):
            return False

    metadatator.apply()


