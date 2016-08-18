rule java_archive {
    meta:
        description = "Java Archive"
        extension = "JAR"
        author = "http://bytesides.blogspot.nl/2013/05/identifying-jar-files-with-yara.html"
    strings:
        $magic = { 50 4b 03 04 ( 14 | 0a ) 00 }
        $string_1 = "META-INF/"
        $string_2 = ".class" nocase

    condition:
        $magic at 0 and 1 of ($string_*)
}
