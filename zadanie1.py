class Wezel:
    def __init__(self, wartosc):
        self.wartosc = wartosc
        self.nastepny = None


class ListaJednokierunkowa:
    def __init__(self):
        self.glowa = None

    def dodajNaPoczatku(self, wartosc):
        nowy = Wezel(wartosc)
        nowy.nastepny = self.glowa
        self.glowa = nowy

    def dodajNaKoncu(self, wartosc):
        nowy = Wezel(wartosc)
        if not self.glowa:
            self.glowa = nowy
            return
        aktualny = self.glowa
        while aktualny.nastepny:
            aktualny = aktualny.nastepny
        aktualny.nastepny = nowy

    def usunNaPoczatku(self):
        if self.glowa:
            self.glowa = self.glowa.nastepny

    def usunNaKoncu(self):
        if not self.glowa:
            return
        if not self.glowa.nastepny:
            self.glowa = None
            return
        aktualny = self.glowa
        while aktualny.nastepny.nastepny:
            aktualny = aktualny.nastepny
        aktualny.nastepny = None

    def wyswietl(self):
        aktualny = self.glowa
        while aktualny:
            print(aktualny.wartosc, end=" -> ")
            aktualny = aktualny.nastepny
        print("None")


if __name__ == "__main__":
    lista1 = ListaJednokierunkowa()

    lista1.dodajNaPoczatku(10)
    lista1.dodajNaPoczatku(5)
    
    lista1.dodajNaKoncu(15)
    lista1.dodajNaKoncu(20)
    lista1.wyswietl()

    lista1.usunNaPoczatku()
    lista1.wyswietl()

    lista1.usunNaKoncu()
    lista1.wyswietl()
