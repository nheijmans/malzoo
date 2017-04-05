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

rule image_jpg {
    meta:
        description = "JPEG Image"
        extension = "JPEG"
        author = "nheijmans"

    strings:
        $magic = { FF D8 }

    condition:
        $magic at 0
}

rule image_png {
    meta:
        description = "PNG Image"
        extension = "PNG"
        author = "nheijmans"

    strings:
        $magic = { 89 50 }

    condition:
        $magic at 0
}

rule image_gif {
    meta:
        description = "GIF Image"
        extension = "GIF"
        author = "nheijmans"

    strings:
        $magic = { 47 49 }

    condition:
        $magic at 0
}

rule office_docs {
    meta:
        description = "Identification of Office files"
        author = "nheijmans"

    strings:
        $d2003 = { D0 CF 11 E0 A1 B1 1A E1 }
        $d2007 = { 50 4B 03 04 14 00 06 00 }

    condition:
        $d2003 or $d2007
}

rule executable {
    meta:
        description = "Identification of Office files"
        author = "nheijmans"

    strings:
        $mz = { 4D 5A }

    condition:
        $mz at 0
}
