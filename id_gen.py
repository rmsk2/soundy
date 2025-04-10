#! /usr/bin/env python3

import os
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
import desfire
from soundyconsts import *
import uidfactory


class CardIdObserver(CardObserver):
    def __init__(self, uid_repo):
        
        self._uid_repo = uid_repo

    def update(self, _, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            atr_txt = toHexString(card.atr)

            if atr_txt not in ALL_ATRS:
                print(f"Card type unknown. ATR {atr_txt}")
                continue

            uid_reader = self._uid_repo.to_uid_r(atr_txt)
            card_id, ok = uid_reader.make_card_id(card)
            if not ok:
                print(f"Error reading {uid_reader.get_name()} card")
                continue

            print(f"{uid_reader.get_name()} card. Card id: {card_id}")

        for card in removedcards:
            pass


if __name__ == "__main__":
    try:
        os.system(CLEAR_COMMAND)
        u = uidfactory.UidReaderRepo()
        print(f"Put a card on the reader to get its id")
        cardmonitor = CardMonitor()
        uid_observer = CardIdObserver(u)
        cardmonitor.addObserver(uid_observer)

        input("Press Enter to stop\n\n")
    except KeyboardInterrupt:
        print()
    except Exception as e:
        print(e)
    finally:
        cardmonitor.deleteObserver(uid_observer)