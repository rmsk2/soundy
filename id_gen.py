#! /usr/bin/env python3

import os
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
import desfire
from soundyconsts import *
import cardy


class CardIdObserver(CardObserver):
    def __init__(self, uid_reader):
        if not isinstance(uid_reader, cardy.IUidReader):
            raise Exception("Wrong type")
        
        self._uid_reader = uid_reader

    def update(self, _, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            atr_txt = toHexString(card.atr)
            if atr_txt != self._uid_reader.get_atr():
                print(f"Not a {self._uid_reader.get_name()} card. ATR {atr_txt}")

                if atr_txt in ALL_ATRS:
                    for i in range(len(ALL_ATRS)):
                        if ALL_ATRS[i] == atr_txt:
                            print(f"Card type is known and has id {i}")
                else:
                    print("Card type unknown")
                return
            
            res, ok = self._uid_reader.make_card_id(card, -1)
            if not ok:
                print(f"Error reading {self._uid_reader.get_name()} card")
                return

            print(f"Card Id: {res}")

        for card in removedcards:
            pass


if __name__ == "__main__":
    try:
        os.system(CLEAR_COMMAND)
        uid_reader = desfire.DESFireUidReader(ATR_DES_FIRE)
        print(f"Put a ({uid_reader.get_name()}) card on the reader to get its id")
        cardmonitor = CardMonitor()
        uid_observer = CardIdObserver(uid_reader)
        cardmonitor.addObserver(uid_observer)

        input("Press Enter to stop\n\n")
    except KeyboardInterrupt:
        print()
    except Exception as e:
        print(e)
    finally:
        cardmonitor.deleteObserver(uid_observer)