"""
Deney sonuçlarının analizi.

sonuclar/ klasöründeki bütün JSON dosyalarını okur, tek bir tabloda birleştirir ve
kontrol koşulu ile grup koşulundaki gruba uyma oranlarını karşılaştırır.
Özet tablolar terminale yazılır, grafik sonuclar/uyma_orani.png olarak kaydedilir.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

SONUC_KLASORU = Path("sonuclar")
GRAFIK_DOSYASI = SONUC_KLASORU / "uyma_orani.png"

KOSUL_ADLARI = {"kontrol": "Kontrol (tek başına)", "grup": "Grup (4 suç ortağı)"}
KOSUL_RENKLERI = {"kontrol": "#2a78d6", "grup": "#eb6834"}


def sonuclari_oku() -> pd.DataFrame:
    """Bütün deney dosyalarındaki denemeleri tek bir tabloda (DataFrame) toplar."""
    satirlar = []
    for dosya_yolu in sorted(SONUC_KLASORU.glob("deney_*.json")):
        with open(dosya_yolu, encoding="utf-8") as dosya:
            kayit = json.load(dosya)
        for deneme in kayit["denemeler"]:
            satirlar.append({**deneme, "model": kayit["ayarlar"]["model"], "dosya": dosya_yolu.name})
    return pd.DataFrame(satirlar)


def uyma_oranlari(tablo: pd.DataFrame) -> pd.DataFrame:
    """Her soru ve koşul için gruba uyma oranını (%) hesaplar."""
    tablo = tablo.assign(
        uydu=tablo["sonuc"] == "uydu",
        soru_kisa=tablo["soru"].str.extract(r"Referans çizgi (\d+ cm)")[0],
    )
    oranlar = tablo.groupby(["soru_kisa", "kosul"], sort=False)["uydu"].mean().mul(100)
    return oranlar.unstack("kosul")[["kontrol", "grup"]]


def grafik_ciz(oranlar: pd.DataFrame, baslik: str) -> None:
    """Soru başına iki koşulun uyma oranlarını yan yana çubuklarla çizer ve dosyaya kaydeder."""
    fig, ax = plt.subplots(figsize=(7, 4.2))
    genislik = 0.36
    konumlar = range(len(oranlar))

    for sira, kosul in enumerate(["kontrol", "grup"]):
        x = [k + (sira - 0.5) * (genislik + 0.02) for k in konumlar]
        cubuklar = ax.bar(x, oranlar[kosul], width=genislik, color=KOSUL_RENKLERI[kosul], label=KOSUL_ADLARI[kosul])
        ax.bar_label(cubuklar, labels=[f"%{deger:.0f}" for deger in oranlar[kosul]], padding=3, color="#52514e", fontsize=9)

    ax.set_xticks(list(konumlar), [f"Referans {soru}" for soru in oranlar.index])
    ax.set_ylim(0, 110)
    ax.set_yticks([0, 25, 50, 75, 100], ["%0", "%25", "%50", "%75", "%100"])
    ax.set_ylabel("Grubun yanlış cevabını verme oranı", color="#52514e")
    ax.set_title(baslik, loc="left", fontsize=11, color="#0b0b0b", pad=30)

    ax.grid(axis="y", color="#e1e0d9", linewidth=0.8)
    ax.set_axisbelow(True)
    for kenar in ["top", "right", "left"]:
        ax.spines[kenar].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(colors="#52514e", length=0)
    ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=9)

    fig.tight_layout()
    fig.savefig(GRAFIK_DOSYASI, dpi=150)


if __name__ == "__main__":
    tablo = sonuclari_oku()
    if tablo.empty:
        raise SystemExit("sonuclar/ klasöründe deney dosyası bulunamadı. Önce deney.py'yi çalıştırın.")

    print(f"Toplam {len(tablo)} deneme, {tablo['dosya'].nunique()} dosyadan okundu.")
    print(f"Model(ler): {', '.join(tablo['model'].unique())}\n")

    print("Koşullara göre sonuçların dağılımı (%):")
    dagilim = pd.crosstab(tablo["kosul"], tablo["sonuc"], normalize="index").mul(100).round(1)
    print(dagilim, "\n")

    oranlar = uyma_oranlari(tablo)
    print("Soru başına gruba uyma oranı (%):")
    print(oranlar.round(1), "\n")

    modeller = ", ".join(tablo["model"].unique())
    grafik_ciz(oranlar, f"Grup baskısı altında uyma oranı ({modeller}, n = {len(tablo)})")
    print(f"Grafik kaydedildi: {GRAFIK_DOSYASI}")
    