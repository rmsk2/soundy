#! /usr/bin/env python3

from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
import desfire
from soundyconsts import *


class DesFireCardIdObserver(CardObserver):
    def __init__(self):
        self._des_fire = desfire.DESFireUidReader(ATR_DES_FIRE)

    def update(self, _, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            atr_txt = toHexString(card.atr)
            if atr_txt != ATR_DES_FIRE:
                print(f"Not a DESFire card. ATR {atr_txt}")

                if atr_txt in ALL_ATRS:
                    for i in range(len(ALL_ATRS)):
                        if ALL_ATRS[i] == atr_txt:
                            print(f"Card type is known and has id {i}")
                else:
                    print("Card type unknown")
                return
            
            res, ok = self._des_fire.make_card_id(card, -1)
            if not ok:
                print("Error reading DESFire card")
                return

            print(f"Card Id: {res}")

        for card in removedcards:
            pass


if __name__ == "__main__":
    try:
        print("Put a (DESFire) card on the reader to get its id")
        cardmonitor = CardMonitor()
        selectobserver = DesFireCardIdObserver()
        cardmonitor.addObserver(selectobserver)

        input("Press Enter to stop\n\n")
    except KeyboardInterrupt:
        print()
    except Exception as e:
        print(e)
    finally:
        cardmonitor.deleteObserver(selectobserver)