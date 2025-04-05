# General overview

The main idea behind this software is to allow the user to control playback of tracks on a playlist via
RFID capable smartcards. I.e. the user can start playback of a playlist by putting a corresponding smartcard 
(called a `playlist card`) on the reader and pausing playback by removing the card from the reader again. 
The playlist which is played back depends on smartcard which is placed on the reader. I.e. different 
playlist cards cause different playlists to be played. In addition to that the user can control the following 
aspects via another set of smartcards called `function cards`.

- Restart the selected playlist
- Restart the current track
- Go to the next track
- Go to the previous track
- End the program

For instance one would restart a playlist by first placing the `restart function card` on the reader and removing it
again. The UI then shows a text that says that the playlist which is selected by the next `playlist card` is 
restarted. This command is executed as soon as the next `playlist card` is put on the RFID reader. Restarting a track
would be achieved by placing the `restart function card` on the reader followed by the corresponding `playlist card`.

The whole purpose behind all this is to increase accessibility of audio books for persons which are impaired in such ways
that make using the UI of modern computers difficult or impractical. This is (hopefully) achieved by transforming the task 
of using a piece of software via a mouse or touch controlled GUI into a series of simple manual interactions which require 
the user to place easy to handle physical objects (smartcards) on a certain location (the reader).

# Supported cards and readers

This software is written in Python and depends on [`pygame`](https://www.pygame.org/docs/) for implemeting the UI and 
`pyscard` for handling card access. [`pyscard`](https://github.com/LudovicRousseau/pyscard) in turn relies on the `pcscd` 
daemon which abstracts away access to smartcard readers on Linux and macOS. On Windows `PCSC` is part of the operating 
system. This software can use any card and reader combination which is supported by `pyscard`.

Cards are identified by this software primarily by their Answer To Reset or ATR, which is a sequence of bytes that is 
automatically sent by a smartcard as soon as it is powered on. Different types of cards have different ATRs but two cards 
of the same type have identical ATRs. You can use `id_gen.py`, which is part of this repo, to read the ATR of RFID capable 
smartcards you may have lying around. If you manage to find at least six different cards with different ATRs you can use them
to control the five functions mentioned above and one playlist.

Hunting for a usable set of cards seemed to be impractical in the long run, so another solution was needed. Different
smartcard families allow to identify cards which are part of this family by a unique card serial number and offer commands 
to read this serial number from the card. As I had some preexisting knowledge with respect to DESFire cards and as blank
DESFire cards are sold for instance on Amazon I decided to implement reading the serial number of DESFire cards as
an alternative to the ATR for identifying individual cards. 

It also seemed to be impractical to use the full seven byte serial number in the various config files and so the program
`id_gen.py` calculates and prints a simplified card id for each DESFire card which is placed on the reader

```
Put a DESFire card on the reader to get its id
Press Enter to stop

Card Id: 60798
Not a DESFire card. ATR 3B 84 80 01 80 82 90 00 97
```

or the full ATR for non DESFire cards. You might say that using a smartcard intended for security purposes in a scenario like
this is totally overblown and you are right. But that is what seemed to work with my reader and the software stack available
to me. 

As `id_gen.py` simply calculates a hash over the serial number read from the card and uses the first two bytes of this
hash as an id (see method `uid_to_card_id()` of class `DESFireUidReader` in `desfire.py`) it is not that unlikely that two
of your cards are assigned the same id. In that case you could use some other bytes from the hash or hash some additional data
to make sure all of your cards end up having a different id.