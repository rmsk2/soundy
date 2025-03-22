#! /usr/bin/env python3

from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
import desfire

ATR_DES_FIRE = "3B 81 80 01 80 80"

class DesFireCardIdObserver(CardObserver):
    def __init__(self):
        self._des_fire = desfire.DESFireUidReader(ATR_DES_FIRE)

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            atr_txt = toHexString(card.atr)
            if atr_txt != ATR_DES_FIRE:
                print(f"Not a DESFire card. ATR {atr_txt}")
                return
            
            res, ok = self._des_fire.make_card_id(card, -1)
            if not ok:
                print("Error reading DESFire card")
                return

            print(f"Card Id: {res}")

        for card in removedcards:
            pass


if __name__ == "__main__":
    print("Put a DESFire card on the reader to get its id")
    cardmonitor = CardMonitor()
    selectobserver = DesFireCardIdObserver()
    cardmonitor.addObserver(selectobserver)

    input("Press Enter to stop\n\n")

    cardmonitor.deleteObserver(selectobserver)