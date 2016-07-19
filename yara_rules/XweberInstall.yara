rule xweber_install {
    meta:
        author = "RJM"
        info = "Grill_APT_xweber_install.exe"

        strings:
                $s1 = "xweber_install.exe" 
                $s2 = "\\sysprep\\sysprep.exe" 
                $s3 = "ping 127.0.0.1 -n 5"
                $s4 = "cmd.exe /c del /a /f"
              

        condition:
                3 of them
}
