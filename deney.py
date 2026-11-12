"""
Asch uyma deneyi.

Her denemede suç ortakları bilerek aynı yanlış cevabı verir, ardından gerçek katılımcı cevaplar.
Katılımcının cevabı üç şekilde sınıflandırılır:
- "uydu":     grubun yanlış cevabını verdi
- "bagimsiz": doğru cevabı verdi
- "diger":    ikisinden de farklı bir cevap verdi
"""

from dataclasses import dataclass

from ajanlar import DilModeliAjan, SabitAjan


@dataclass
class Soru:
    """Deneyde sorulan bir soru: metni, doğru cevabı ve suç ortaklarının vereceği yanlış cevap."""

    metin: str
    dogru_cevap: str
    yanlis_cevap: str


SORULAR = [
    Soru("Referans çizgi 8 cm. Hangisi onunla aynı uzunlukta? A) 5 cm  B) 8 cm  C) 10 cm", "B", "A"),
    Soru("Referans çizgi 12 cm. Hangisi onunla aynı uzunlukta? A) 12 cm  B) 9 cm  C) 15 cm", "A", "C"),
    Soru("Referans çizgi 6 cm. Hangisi onunla aynı uzunlukta? A) 3 cm  B) 10 cm  C) 6 cm", "C", "B"),
]


def cevabi_siniflandir(cevap: str, soru: Soru) -> str:
    """Katılımcının cevabının gruba mı uyduğunu, doğruyu mu söylediğini belirler."""
    cevap = cevap.strip().upper()
    if cevap == soru.yanlis_cevap:
        return "uydu"
    if cevap == soru.dogru_cevap:
        return "bagimsiz"
    return "diger"


def deneme_yap(soru: Soru, ortak_sayisi: int, katilimci: DilModeliAjan) -> dict:
    """Tek bir deneme: suç ortakları cevaplar, ardından katılımcı cevaplar. Sonucu sözlük olarak döndürür."""
    ortaklar = [SabitAjan(f"Ajan_{i}", soru.yanlis_cevap) for i in range(1, ortak_sayisi + 1)]

    onceki_cevaplar: list[tuple[str, str]] = []
    for ajan in ortaklar:
        onceki_cevaplar.append((ajan.isim, ajan.cevap_ver(soru.metin, onceki_cevaplar)))

    cevap = katilimci.cevap_ver(soru.metin, onceki_cevaplar)

    return {
        "soru": soru.metin,
        "dogru_cevap": soru.dogru_cevap,
        "grubun_cevabi": soru.yanlis_cevap,
        "ortak_sayisi": ortak_sayisi,
        "katilimci_cevabi": cevap,
        "sonuc": cevabi_siniflandir(cevap, soru),
    }


if __name__ == "__main__":
    TEKRAR_SAYISI = 10  # Her soru kaç kez sorulacak
    ORTAK_SAYISI = 4  # Kaç suç ortağı olacak

    katilimci = DilModeliAjan("Katilimci", "Sen bir grup deneyine katılan bir kişisin.")

    sonuclar = []
    for soru in SORULAR:
        for _ in range(TEKRAR_SAYISI):
            sonuclar.append(deneme_yap(soru, ORTAK_SAYISI, katilimci))

    uyan = sum(1 for s in sonuclar if s["sonuc"] == "uydu")
    print(f"Toplam deneme: {len(sonuclar)}")
    print(f"Gruba uyma: {uyan} ({uyan / len(sonuclar):.0%})")
    print("İlk denemenin kaydı:", sonuclar[0])
    