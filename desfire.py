#! /usr/bin/env python3
"""
Sample script that monitors smartcard insertion/removal and select
DF_TELECOM on inserted cards

__author__ = "https://www.gemalto.com/"

Copyright 2001-2012 gemalto
Author: Jean-Daniel Aussel, mailto:jean-daniel.aussel@gemalto.com

This file is part of pyscard.

pyscard is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 2.1 of the License, or
(at your option) any later version.

pyscard is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with pyscard; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

from time import sleep

from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
import hashlib


# a simple card observer that tries to select DF_TELECOM on an inserted card
class selectDFTELECOMObserver(CardObserver):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """

    def __init__(self):
        self._apdu_get_version = [0x90, 0x60, 0x00, 0x00, 0x00]
        self._apdu_read_next   = [0x90, 0xAF, 0x00, 0x00, 0x00]

    def read_des_fire_uid(self, card):
        try:
            card.connection = card.createConnection()
            card.connection.connect()
            version_bytes = []
            response, _, sw2 = card.connection.transmit(self._apdu_get_version)
            if sw2 != 0xAF:
                return None

            version_bytes += response
            while sw2 != 0x00:
                response, _, sw2 = card.connection.transmit(self._apdu_read_next)
                version_bytes += response
            
            res = version_bytes[14:21]
        except:
            print("Card communication failure")
            res = None

        return res

    def uid_to_card_id(self, d):
        t = hashlib.md5(bytes(d)).digest()[0:2]
        return t[1]*256 + t[0]

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            print("+Inserted: ", toHexString(card.atr))
            res = self.read_des_fire_uid(card)
            if res == None:
                print("Error reading DESFire card")
                return
            print(f"Card Id: {self.uid_to_card_id(res)}")

        for card in removedcards:
            print("-Removed: ", toHexString(card.atr))


if __name__ == "__main__":
    print("Insert or remove a DESFire card in the system.")
    print("This program will exit in 60 seconds")
    print("")
    cardmonitor = CardMonitor()
    selectobserver = selectDFTELECOMObserver()
    cardmonitor.addObserver(selectobserver)

    sleep(60)

    # don't forget to remove observer, or the
    # monitor will poll forever...
    cardmonitor.deleteObserver(selectobserver)