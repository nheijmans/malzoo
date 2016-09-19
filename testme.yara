rule evil_txt {
    meta:
        description:"Testing rule"
        author: "niels"

    strings:
        $a = "niels"
        $b = "hotsbots"
        $c  = "knetter"

    condition:
        1 of them

}
