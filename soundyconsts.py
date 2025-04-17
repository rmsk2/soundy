from typing import Any

# Function codes
FUNC_PLAYLIST_RESTART = 0
FUNC_SONG_RESTART = 1
FUNC_END = 2
FUNC_PERFORMED = 3
FUNC_SONG_SKIP = 4
FUNC_SONG_PREV = 5

# Error codes
ERR_TYPE_COMM = 1
ERR_TYPE_FILE = 2

# ATRs of known card types
ATR_DES_FIRE = "3B 81 80 01 80 80"
ATR_E_PERSO = "3B 84 80 01 80 82 90 00 97"
ATR_GIRO = "3B 87 80 01 80 31 C0 73 D6 31 C0 23"
ATR_EGK = "3B 85 80 01 30 01 01 30 30 34"
ATR_NTAG = "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 03 00 00 00 00 68"
ALL_ATRS = [ATR_E_PERSO, ATR_GIRO, ATR_EGK, ATR_DES_FIRE, ATR_NTAG]

# Change to cls on Windows
CLEAR_COMMAND = 'clear'

# This should be as long as the longest string to be displayed
EMPTY_STR = '                                  '
ERR_MSG_LOAD_PLAYLIST = "Unable to load playlists"
STD_MSG = "Hello"
CAPTION_DEFAULT = "Simple audio book player"
ERR_MSG_LOAD_CONFIG = "Unable to load configuration"
MSG_PLAYLIST_BEGINING = "Go back to beginning of audio book"
MSG_RESTART_SONG = "Go back to beginning of chapter"
MSG_SKIP_SONG = "To next chapter"
MSG_NEXT_SONG = "To previous chapter"
MSG_PLAY_FORMAT_STR = "Chapter {song} of {num_songs}"

NO_CARD_ID = -1
NO_ATR = ""


def acr122u_buzzer_off(card):
    try:
        card.connection = card.createConnection()
        card.connection.connect()
        response, sw1, sw2 = card.connection.transmit([0xFF, 0x00, 0x52, 0x00, 0x00])
        if (sw1 != 0x90) or (sw2 != 0x00):
            return None

        res = response
    except:
        res = None

    return res

# A UiReader knows how to calculate an individual identity for
# the cards of a specifc type using their serial number
class IUidReader:
    def make_card_id(self, card: Any) -> tuple[int, bool]:
        # id, ok
        return NO_CARD_ID, False

    def get_atr(self) -> str:
        return NO_ATR

    def get_name(self) -> str:
        return ""