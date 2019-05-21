# publishr
A script to automate the tedious process of releasing music.

Currently a work in progress.

## Features
- [x] Smartly get release info from user
- [ ] Rename audio files
- [ ] Apply ID3 Metadata (artist, album, track no., cover art image, release date, ...) to audio files
- [ ] Automatically create missing "square" cover art formats
- [ ] Automatically create videos from "wide" cover arts (required for YouTube)
- [ ] Upload to a website (files and database)
- [ ] Upload to YouTube
- [ ] Post to social medias
- [ ] Send a newsletter  

## Installing
Make sure you have PIP & Python (3.6 or later) installed. Then:

`git clone https://github.com/ewen-lbh/publishr.git`

`cd publishr`

`pip install -r requirements.txt`

If you prefer a one-liner: `git clone https://github.com/ewen-lbh/publishr.git && cd publishr && pip install -r requirements.txt`

If you plan on using social medias publishing, website uploading or YouTube uploading:
Rename `example.env` to `.env` and fill in your credentials
(you will need to create API projects for the services you want to use, more details [here](#APIs))

## Configuring
Create a new json file in `config` and name it whatever you want.

Look at an example from `config/example.json` or look at all the config options in `src/internalconf.py`'s `CONFIG_TYPES` constant.

You can also run `python3 run.py` without a `--config` argument and let the config wizard guide you.

## Usage
Assuming you are in the `publishr` directory:

`python3 run.py --config <config filename>`

(You can also use the short flag `-c`)


## APIs
Work in progress section.
 
