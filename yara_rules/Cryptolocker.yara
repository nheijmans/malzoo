rule malware_cryptolocker_pubkey {
    strings:
        $blob = { 06 02 00 00 00 A4 00 00
           52 53 41 31 00 04 00 00  01 00 01 00 71 B8 8E E8
            C1 0E EA 86 1D 09 75 F9  57 CF D4 4C EC 61 76 77
            A3 99 3E 4A B8 AB BA 6A  DF 9D B2 DE 39 62 7A 13
            71 76 C7 90 68 FE FB 3D  2D 89 26 DD 1D 99 54 7D
            A6 56 43 16 30 22 36 FD  3D A2 21 9F BA 71 1A 48
            62 42 90 14 07 FD 07 DF  D7 F1 79 03 4A 13 4B A4
            73 AD 20 32 BF DB ED A5  55 FB 17 21 B5 1F 9F 5C
            0A E3 B9 B2 DA 30 87 95  1D 93 0F 24 92 D6 CF 33
            81 C1 E4 F6 4E 15 EA C6  86 DE 49 D0 }

    condition:
        $blob
}
