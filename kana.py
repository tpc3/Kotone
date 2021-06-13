import MeCab
import jaconv
import english_to_kana


num_table = str.maketrans({
    "1": "いち",
    "2": "にい",
    "3": "さん",
    "4": "よん",
    "5": "ごお",
    "6": "ろく",
    "7": "なな",
    "8": "はち",
    "9": "きゅう",
    "0": "ぜろ",
    "#": "しゃーぷ",
    "\n": "、",
    " ": "、",
    "　": "、",
    "ぁ": "あ",
    "ぃ": "い",
    "ぅ": "う",
    "ぇ": "え",
    "ぉ": "お",
    "ァ": "あ",
    "ィ": "い",
    "ゥ": "う",
    "ェ": "え",
    "ォ": "お",
    "ゔ": "ぶ",
    "ヴ": "ぶ",
    "っ": ",",
    "ッ": ",",
    "づ": "ず",
    "ヅ": "ズ"
})

small_table = {
    "ゃ": "や",
    "ゅ": "ゆ",
    "ょ": "よ",
    "ゎ": "わ",
    "ヵ": "か",
    "ㇰ": "く",
    "ヶ": "け",
    "ㇱ": "し",
    "ㇲ": "す",
    "ㇳ": "と",
    "ㇴ": "ぬ",
    "ㇵ": "は",
    "ㇶ": "ひ",
    "ㇷ": "ぶ",
    "ㇸ": "へ",
    "ㇹ": "ほ",
    "ㇺ": "む",
    "ャ": "や",
    "ュ": "ゆ",
    "ョ": "よ",
    "ㇻ": "ら",
    "ㇼ": "り",
    "ㇽ": "る",
    "ㇾ": "れ",
    "ㇿ": "ろ",
    "ヮ": "わ"
}

alpha_table = str.maketrans({
    "a": "えー",
    "b": "びー",
    "c": "しー",
    "d": "でぃー",
    "e": "いー",
    "f": "えふ",
    "g": "じー",
    "h": "えいち",
    "i": "あい",
    "j": "じぇい",
    "k": "けい",
    "l": "える",
    "m": "えむ",
    "n": "えぬ",
    "o": "おー",
    "p": "ぴー",
    "q": "きゅー",
    "r": "あーる",
    "s": "えす",
    "t": "てぃー",
    "u": "ゆー",
    "v": "ぶい",
    "w": "だぶりゅー",
    "x": "えっくす",
    "y": "わい",
    "z": "ぜっと",
})

readable_hira = [chr(i) for i in range(12353, 12436)]
readable = "。？、,/+'ー"
readable_end = "。？、ー"
readable_before = "きしちにひみりぎじつふびすとキシチニヒミリギジツフビスト"


class AllHiragana:

    def __init__(self):
        self.etk = english_to_kana.EnglishToKana()
        self.mecab = MeCab.Tagger("-Oyomi")
        self.mecab2 = MeCab.Tagger("-Owakati")

    def tokana(self, data):
        result = jaconv.h2z(self.mecab.parse(data)).translate(num_table)
        for i in self.mecab2.parse(data).split():
            if i.isascii():
                converted = self.etk.convert(english=i)
                if converted == "ERROR 辞書にありません":
                    result = result.replace(i, i.lower().translate(alpha_table))
                else:
                    result = result.replace(i, converted)
        result = jaconv.kata2hira(result).replace("ERROR 辞書にありません", "")

        tmp = list(result)
        for j, i in enumerate(result):
            if i in small_table and (result[j-1] not in readable_before or result[j-1] in readable):
                tmp[j] = small_table[i]
            if (i not in readable_hira and i not in readable) or (result[j-1] in readable and i in readable):
                tmp[j] = ""
        if result[-2] in readable and result[-2] not in readable_end:
            del tmp[-2]
        result = "".join(tmp)

        return result[:-1]


uid_voice = ["f1", "f2", "m1", "m2", "r1", "jgr", "imd1", "f1", "f2"]

if __name__ == "__main__":
    import sys
    a = AllHiragana()
    print(a.tokana(sys.argv[1]))
