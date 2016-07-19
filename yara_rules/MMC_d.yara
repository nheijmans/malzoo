rule mmc_d {
    meta:
        author = "RJM"
        info = "Grill_APT_mmc.exe"

        strings:
                $s1 = "[%s] the file downloaded successfully !" 
                $s2 = "[%s] the file downloaded failed !" 
                $s3 = "[%s] the file uploaded successfully !"
                $s4 = "[%s] the file uploaded failed !"
                $s5 = ".1000001000"
                $s6 = "1.6.2s"
                $s7 = "-sleeptime"
                $s8 = "-url"
                $s9 = "common.asp?action="
                $s10 = "1.6.1s"
                $s11 = "1.5.1s"

        condition:
                6 of them
}

