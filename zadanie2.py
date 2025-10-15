class Wezel:
    def __init__(self, wartosc):
        self.wartosc = wartosc
        self.nastepny = None
        self.poprzedni = None


class ListaDwukierunkowa:
    def __init__(self):
        self.glowa = None
        self.ogon = None

    def dodajNaPoczatku(self, wartosc):
        nowy = Wezel(wartosc)
        if not self.glowa:
            self.glowa = self.ogon = nowy
        else:
            nowy.nastepny = self.glowa
            self.glowa.poprzedni = nowy
            self.glowa = nowy

    def dodajNaKoncu(self, wartosc):
        nowy = Wezel(wartosc)
        if not self.ogon:
            self.glowa = self.ogon = nowy
        else:
            self.ogon.nastepny = nowy
            nowy.poprzedni = self.ogon
            self.ogon = nowy

    def usunNaPoczatku(self):
        if not self.glowa:
            return
        if self.glowa == self.ogon:
            self.glowa = self.ogon = None
        else:
            self.glowa = self.glowa.nastepny
            self.glowa.poprzedni = None

    def usunNaKoncu(self):
        if not self.ogon:
            return
        if self.glowa == self.ogon:
            self.glowa = self.ogon = None
        else:
            self.ogon = self.ogon.poprzedni
            self.ogon.nastepny = None

    def wyswietlOdPoczatku(self):
        aktualny = self.glowa
        while aktualny:
            print(aktualny.wartosc, end=" -> ")
            aktualny = aktualny.nastepny
        print("None")

    def wyswietlOdKonca(self):
        aktualny = self.ogon
        while aktualny:
            print(aktualny.wartosc, end=" -> ")
            aktualny = aktualny.poprzedni
        print("None")


if __name__ == "__main__":
    lista2 = ListaDwukierunkowa()

    lista2.dodajNaPoczatku("A")
    lista2.dodajNaKoncu("B")
    lista2.dodajNaKoncu("C")
    lista2.dodajNaPoczatku("START")

    lista2.wyswietlOdPoczatku()
    lista2.wyswietlOdKonca()

    lista2.usunNaPoczatku()
    lista2.wyswietlOdPoczatku()

    lista2.usunNaKoncu()
    lista2.wyswietlOdPoczatku()
