rule jpg_image : jpg
{
    meta:
        author      = "nheijmans"
        date        = "2016/12/23"
        description = "Check for a filetype that we do not want analyzed"

    strings:
        $jpg = { ffd8 ffe0 }

    condition:
        $jpg at 0
}
rule gif_image : gif
{
    strings:
        $gif = { 4749 4638 }

    condition:
        $gif at 0
}

rule png_image : png
{
    strings:
        $png = { 8950 4e47 }

    condition:
        $png at 0
}
