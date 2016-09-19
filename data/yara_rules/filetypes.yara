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
