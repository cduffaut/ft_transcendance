
class Ascii:
    def __init__(self):
        self.dictionary = {}
        self.setUppercase()
        self.setLowercase()
        self.setSpecialcase()
    
    def setUppercase(self):
        SPACE = "           a        a         a         a         a         a         a         a        a         a       a         a         a        a         a         a         a         a         a          a         a           a               a        a          a        "
        STR1 = "           a  ____  a   _____ a  _____  a  ______ a  ______ a   _____ a  _    _ a  _____ a       _ a  _  __a  _      a  __  __ a  _   _ a   ____  a  _____  a   ____  a  _____  a   _____ a  _______ a  _    _ a __      __a __          __a __   __a __     __a  ______"
        STR2 = "     /\    a |  _ \ a  / ____|a |  __ \ a |  ____|a |  ____|a  / ____|a | |  | |a |_   _|a      | |a | |/ /a | |     a |  \/  |a | \ | |a  / __ \ a |  __ \ a  / __ \ a |  __ \ a  / ____|a |__   __|a | |  | |a \ \    / /a \ \        / /a \ \ / /a \ \   / /a |___  /"
        STR3 = "    /  \   a | |_) |a | |     a | |  | |a | |__   a | |__   a | |  __ a | |__| |a   | |  a      | |a | ' / a | |     a | \  / |a |  \| |a | |  | |a | |__) |a | |  | |a | |__) |a | (___  a    | |   a | |  | |a  \ \  / / a  \ \  /\  / / a  \ V / a  \ \_/ / a    / / "
        STR4 = "   / /\ \  a |  _ < a | |     a | |  | |a |  __|  a |  __|  a | | |_ |a |  __  |a   | |  a  _   | |a |  <  a | |     a | |\/| |a | . ` |a | |  | |a |  ___/ a | |  | |a |  _  / a  \___ \ a    | |   a | |  | |a   \ \/ /  a   \ \/  \/ /  a   > <  a   \   /  a   / /  "
        STR5 = "  / ____ \ a | |_) |a | |____ a | |__| |a | |____ a | |     a | |__| |a | |  | |a  _| |_ a | |__| |a | . \ a | |____ a | |  | |a | |\  |a | |__| |a | |     a | |__| |a | | \ \ a  ____) |a    | |   a | |__| |a    \  /   a    \  /\  /   a  / . \ a    | |   a  / /__ " 
        STR6 = " /_/    \_\\a |____/ a  \_____|a |_____/ a |______|a |_|     a  \_____|a |_|  |_|a |_____|a  \____/ a |_|\_\\a |______|a |_|  |_|a |_| \_|a  \____/ a |_|     a  \___\_\\a |_|  \_\\a |_____/ a    |_|   a  \____/ a     \/    a     \/  \/    a /_/ \_\\a    |_|   a /_____|" 

        STR1 = STR1.split("a")
        STR2 = STR2.split("a")
        STR3 = STR3.split("a")
        STR4 = STR4.split("a")
        STR5 = STR5.split("a")
        STR6 = STR6.split("a")
        SPACE = SPACE.split("a")

        j = 0
        for i in range(ord('A'), ord('Z')+1):
            i = chr(i)
            self.dictionary[i] = []
            self.dictionary[i].append(STR1[j])
            self.dictionary[i].append(STR2[j])
            self.dictionary[i].append(STR3[j])
            self.dictionary[i].append(STR4[j])
            self.dictionary[i].append(STR5[j])
            self.dictionary[i].append(STR6[j])
            self.dictionary[i].append(SPACE[j])
            j += 1

    def setLowercase(self):
        str1 = "        a  _     a       a      _ a       a   __ a        a  _     a  _ a    _ a  _    a  _ a            a        a        a        a        a       a      a  _   a        a        a           a       a        a      "
        str2 = "        a | |    a       a     | |a       a  / _|a        a | |    a (_)a   (_)a | |   a | |a            a        a        a        a        a       a      a | |  a        a        a           a       a        a      "
        str3 = "   __ _ a | |__  a   ___ a   __| |a   ___ a | |_ a   __ _ a | |__  a  _ a    _ a | | __a | |a  _ __ ___  a  _ __  a   ___  a  _ __  a   __ _ a  _ __ a  ___ a | |_ a  _   _ a __   __a __      __a __  __a  _   _ a  ____"
        str4 = "  / _` |a | '_ \ a  / __|a  / _` |a  / _ \\a |  _|a  / _` |a | '_ \ a | |a   | |a | |/ /a | |a | '_ ` _ \ a | '_ \ a  / _ \ a | '_ \ a  / _` |a | '__|a / __|a | __|a | | | |a \ \ / /a \ \ /\ / /a \ \/ /a | | | |a |_  /"
        str5 = " | (_| |a | |_) |a | (__ a | (_| |a |  __/a | |  a | (_| |a | | | |a | |a   | |a |   < a | |a | | | | | |a | | | |a | (_) |a | |_) |a | (_| |a | |   a \__ \\a | |_ a | |_| |a  \ V / a  \ V  V / a  >  < a | |_| |a  / / "
        str6 = "  \__,_|a |_.__/ a  \___|a  \__,_|a  \___|a |_|  a  \__, |a |_| |_|a |_|a   | |a |_|\_\\a |_|a |_| |_| |_|a |_| |_|a  \___/ a | .__/ a  \__, |a |_|   a |___/a  \__|a  \__,_|a   \_/  a   \_/\_/  a /_/\_\\a  \__, |a /___|"
        str7 = "        a        a       a        a       a      a   __/ |a        a    a  _/ |a       a    a            a        a        a | |    a     | |a       a      a      a        a        a           a       a   __/ |a      "
        str8 = "        a        a       a        a       a      a  |___/ a        a    a |__/ a       a    a            a        a        a |_|    a     |_|a       a      a      a        a        a           a       a  |___/ a      "                                                                                                                                                                                                                                          

        str1 = str1.split("a")
        str2 = str2.split("a")
        str3 = str3.split("a")
        str4 = str4.split("a")
        str5 = str5.split("a")
        str6 = str6.split("a")
        str7 = str7.split("a")
        str8 = str8.split("a")

        j = 0
        for i in range(ord('a'), ord('z')+1):
            i = chr(i)
            self.dictionary[i] = []
            self.dictionary[i].append(str1[j])
            self.dictionary[i].append(str2[j])
            self.dictionary[i].append(str3[j])
            self.dictionary[i].append(str4[j])
            self.dictionary[i].append(str5[j])
            self.dictionary[i].append(str6[j])
            self.dictionary[i].append(str7[j])
            self.dictionary[i].append(str8[j])

            j += 1

    def setSpecialcase(self):
        num1 = "   ___  a  __ a  ___  a  ____  a  _  _   a  _____ a    __  a  ______ a   ___  a   ___  a  ___  a    a  _ "
        num2 = "  / _ \ a /_ |a |__ \ a |___ \ a | || |  a | ____|a   / /  a |____  |a  / _ \ a  / _ \ a |__ \ a    a | |"
        num3 = " | | | |a  | |a    ) |a   __) |a | || |_ a | |__  a  / /_  a     / / a | (_) |a | (_) |a    ) |a    a | |"
        num4 = " | | | |a  | |a   / / a  |__ < a |__   _|a |___ \ a | '_ \ a    / /  a  > _ < a  \__, |a   / / a    a | |"
        num5 = " | |_| |a  | |a  / /_ a  ___) |a    | |  a  ___) |a | (_) |a   / /   a | (_) |a    / / a  |_|  a  _ a |_|"
        num6 = "  \___/ a  |_|a |____|a |____/ a    |_|  a |____/ a  \___/ a  /_/    a  \___/ a   /_/  a  (_)  a (_)a (_)"
        space = "        a     a       a        a         a        a        a         a        a        a       a    a    "                                                                                                 

        num1 = num1.split("a")
        num2 = num2.split("a")
        num3 = num3.split("a")
        num4 = num4.split("a")
        num5 = num5.split("a")
        num6 = num6.split("a")
        space = space.split("a")

        j = 0
        for i in "0123456789?.!":
            self.dictionary[i] = []
            self.dictionary[i].append(num1[j])
            self.dictionary[i].append(num2[j])
            self.dictionary[i].append(num3[j])
            self.dictionary[i].append(num4[j])
            self.dictionary[i].append(num5[j])
            self.dictionary[i].append(num6[j])
            self.dictionary[i].append(space[j])


            j += 1

    def putString(self,string, beginstr="", endstr=""):
        j = 0
        while j <= 7:
            for i in string:
                print(beginstr, end="")
                if i == " ":
                    print("   ", end="")
                elif not i.islower() and j > 5:
                    print(self.dictionary[i][6], end="")
                else:
                    print(self.dictionary[i][j], end="")
            print(endstr)
            j += 1


                                                                                                                                                                                                                                                                    