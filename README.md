# General overview

The main idea behind this software is to allow the user to control playback of tracks on a playlist via
RFID capable smartcards. I.e. the user can start playback of a playlist by putting a corresponding smartcard 
(called a `playlist card`) on the reader and pausing playback by removing the card from the reader again. 
The playlist which is played back depends on the identity of smartcard which is placed on the reader. I.e. different 
playlist cards cause different playlists to be played. In addition to that the user can control the following 
aspects via another set of smartcards called `function cards`.

- Restart the selected playlist
- Restart the current track
- Go to the next track
- Go to the previous track
- End the program

For instance one would restart a playlist by first placing the `rewind function card` on the reader and removing it
again. The UI then shows a text that says that the playlist which is selected by the next `playlist card` is 
restarted. This command is executed as soon as the next `playlist card` is put on the RFID reader. Restarting a track
would be achieved by first placing the `restart function card` on the reader followed by the corresponding `playlist card`.

The whole purpose behind all this is to increase the accessibility of audio books for persons who are impaired in such ways
that make using the UI of modern computers difficult or impractical. This is (hopefully) achieved by transforming the task 
of using a piece of software via a mouse or touch controlled GUI into a series of simple manual interactions which require 
the user to place easy to handle physical objects (smartcards) at a certain location (the reader).

This software is written in Python and depends on [`pygame`](https://www.pygame.org/docs/) for implemeting the UI and 
`pyscard` for handling card access. [`pyscard`](https://github.com/LudovicRousseau/pyscard) in turn relies on the `pcscd` 
daemon which abstracts away access to smartcard readers on Linux and macOS. On Windows `PCSC` is part of the operating 
system. This software can use any card and reader combination which is supported by `pyscard`. I developed this software
under Linux and I have successfully installed it on an older MacBook. I see no principal reason why it should not work 
under Windows but I have not tested this, yet.

# Supported cards and readers

Cards are identified by this software primarily by their Answer To Reset or ATR, which is a sequence of bytes that is 
automatically sent by a smartcard as soon as it is powered on. Different types of cards have different ATRs but two cards 
of the same type have identical ATRs. You can use `id_gen.py`, which is part of this repo, to read the ATR of RFID capable 
smartcards you may have lying around. If you manage to find at least six different cards with different ATRs you can use them
to control the five functions mentioned above and one playlist. I have tested the following cards or RFID capable devices

- The German national ID card (ePA)
- The German health system card (eGK)
- Bank cards
- Credit cards
- Different company badges
- Yubikeys and other security sticks
- Fido tokens

Hunting for a usable set of cards or other RFID enabled devices seemed to be impractical in the long run, so another solution was 
needed. Different smartcard families allow to identify cards which are part of this family by a unique card serial number and offer
commands to read this serial number from the card. As I had some preexisting knowledge with respect to DESFire cards and as blank
DESFire cards are sold for instance on Amazon I decided to implement reading the serial number of DESFire cards as
an alternative to the ATR for identifying individual cards. 

It also seemed to be impractical to use the full seven byte serial number in the various config files and so the program
`id_gen.py` calculates and prints a simplified card id for each DESFire card which is placed on the reader

```
Put a (DESFire) card on the reader to get its id
Press Enter to stop

Not a DESFire card. ATR 3B 88 80 01 89 01 A0 11 20 20 09 07 3E
Card type unknown
Not a DESFire card. ATR 3B 84 80 01 80 82 90 00 97
Card type is known and has id 0
Card Id: 51918
```

or the full ATR for non DESFire cards as well as their id if the card type is known. You might say that using a smartcard intended 
for security purposes in a scenario like this is totally overblown and you are right. But that is what seemed to work with my reader
and the software stack immediately available to me. If I end up owning a reader that can read simple RFID tags and if these
are compatible with `pyscard` then maybe I will adapt this software accordingly.

As `id_gen.py` simply calculates a hash over the serial number read from the card and uses the first two bytes of this
hash as an id (see method `uid_to_card_id()` of class `DESFireUidReader` in `desfire.py`) it is not that unlikely that two
of your cards are assigned the same id. In that case you could use some other bytes from the hash, hash some additional data
or use more hash bytes to make sure all of your cards end up having a different id.

# Run the software and configuration

You can run this software though the command `python3 sound.py <config_dir>`. Maybe you have to replace `python3` by `python`
depending on your system. The config dir is optional. If it is mssing the current directory is used. When started the program
reads the file `ui_config` in the config dir and interprets any `.json` file in this directory as a playlist. When an error
reading a card is encountered the background of the UI flashes red once. An error reading a file is signalled by a single flashing
of the background in blue.

## Config of program

The overall config of this software is split between two files: `ui_config` and `soundyconsts.py`. In the JSON file `ui_config`
under `sounds` you can  configure the sounds which are played when for instance an error occurs or a card is successfully read
by referencing a corresponding file. Any file format supported by [`pygame`](https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound) 
can be used here. According to the documentation currently OGG and WAV are supported for this purpose. Please note that this limitation 
does not apply to the music files on the playlist. These can be [MP3 or OGG](https://www.pygame.org/docs/ref/music.html#pygame.mixer.music).

In the `ids` "section" you can configure which cards are used as `function cards` as specified by their id. As written above the
card ids of DESFire and other cards known to this software can de determined using `id_gen.py`. The ids of cards which are identified 
by their ATR only is determined by their position in the list `ALL_ATRS` contained in the module `soundyconsts.py`.

The "section" `size` specifies the size of the UI in pixels as well as the font sizes used for displaying text. Finally the "key" 
`wait_reader_sec` determines how long the software waits for the reader to become ready. The messages displayed on the UI can
be customized in the file `soundyconsts.py` as can be the command which is used to clear the console after program start. Please
change the constant `CLEAR_COMMAND` to `cls` under Windows.

## Config of playlists

Any `.json` file in the config dir is interpreted as a playlist. playlists have to have the following structure.

```
{
    "play_list": "Test playlist",
    "file_name": "./test_play_list.json",
    "current_title": 0,
    "play_time": 0.0,
    "card_id": 28435,
    "data_dir": "/user/test/testdata",
    "titles": [
        "track1.mp3",
        "track2.mp3",
        "track3.mp3"
    ]
}

```

The "key" `play_list` can be used to set the name of the playlist. This will also occur in the title bar of the window in which the UI will
be displayed. `file_name` is set to the file name under which the playlist was read upon program start. It can be set to the empty string if 
you create a new playlist by hand. This information is used when a playlist needs to be updated on disk by the program. `current_title` holds the 
zero based index of the track which would be played and `play_time` is used to determine the offset in seconds into this file. This is used to restart 
playback on the same spot where it was stopped. For this to work 100% reliably, MP3 files should not be encoded with a variable bit rate. This is 
[a limitation](https://www.pygame.org/docs/ref/music.html#pygame.mixer.music.play) of `pygame`. The value `card_id` determines the id of the
card which is used as the `playlist card` for this playlist. As described above these ids can be determined by `id_gen.py` for DESFire cards
and by the position of its ATR in `ALL_ATRS` for all other cards. `data_dir` specifies the directory in which the actual sound files are stored.
The list `titles` specifies the names and positions of the individual tracks on this playlist, i.e. the sequence in this list determines the sequence
in which these tracks are played back. 

You can use the program `create_list.py` from this repo to create a new playlist. Execute `python3 create_list.py <dir to list> <new playlist file>`,
where `<dir to list>` is the directory which contains the music files of the playlist and `<new playlist file>` has to specify the name of the file
in which the new playlist is to be saved. The contents of the given directory is listed, sorted and added to the playlist as its `titles` component.
Additionally you have to enter a name for the playlist and the the id of the corresponding `playlist card`.

# Installation on macOS

I installed `pcscd` and Python 3.12 via `brew` which both worked without a problem. Unfortunatley this has precluded me
from installing `pyscard` and `pygame` via `pip3` as global modules. The workaround is to install them in a Python virtual
environment and run this software also from the venv.

# Other considerations

This chapter mentions some other aspects which can be important when putting this software to use for its intended purpose of supporting impaired
persons. In my specific case I wanted to make sure that the user is never forced to interact with the operating system of the machine on which
this software runs. My ideal scenario was that the user simply opens a Laptop, the machine boots, the user is automatically logged in and the 
program is started automatically without additional intervention. On top of that the machine should never go into sleep mode and the whole setup 
should not be adversely affected if the user closes the laptop and reopens it. I solved all this by configuring an older macBook correspondingly.

Another potential problem was created by the power management functions of some PC speakers which turn themselves off when no sound is played 
but fail to turn themselves back on again when playing back the audio book is resumed. I solved this problem by playing a "beep" sound each time 
a card was successfully read which not only provides feedback to the user that the card was read but also wakes up the speakers much more realiably
than playing back the contents of an audio book.