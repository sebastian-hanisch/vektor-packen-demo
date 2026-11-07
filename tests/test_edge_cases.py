"""Randfälle: leere Eingabe, ein Teil, Teil gleich Kapazität, gleiche Teile, Gleichstände, ungültige Eingaben."""

import pytest

import vkp_algorithm as A
import vkp_constants as C
from vkp_scenario import Instance, mess_seed, zufallsinstanz


@pytest.mark.parametrize("regel", [0, 1, 2])
def test_leere_eingabe_ergibt_keine_behaelter(regel):
    assert A.pack((), [], 10, regel) == []
    assert A.schranke((), 10) == 0 and A.optimum((), 10) == 0


@pytest.mark.parametrize("regel", [0, 1, 2])
def test_ein_teil_und_teil_gleich_kapazitaet(regel):
    assert A.pack(((7, 3),), [0], 10, regel) == [[0]]
    assert A.pack(((10, 1), (1, 10)), [0, 1], 10, regel) == [[0], [1]]      # Volumen 11 beziehungsweise Gewicht 11: passt nicht zusammen
    assert A.pack(((10, 10), (1, 1)), [0, 1], 10, regel) == [[0], [1]]      # beide Maße voll


@pytest.mark.parametrize("regel", [0, 1, 2])
def test_zwei_teile_die_in_einem_mass_passen_und_im_anderen_nicht(regel):
    assert A.pack(((5, 6), (5, 5)), [0, 1], 10, regel) == [[0], [1]]        # Gewicht 11
    assert A.pack(((5, 5), (5, 5)), [0, 1], 10, regel) == [[0, 1]]         # genau voll in beiden Maßen (inklusive Grenze)


def test_gleichstand_beim_sortieren_haelt_die_lieferreihenfolge():
    # Summe 10 für alle vier Teile: die Lieferreihenfolge bleibt; mit der Gleichstandsregel „volumen“ entscheidet zuerst das größere Volumen, dann das größere Gewicht
    items = ((4, 6), (6, 4), (5, 5), (6, 4))
    assert A.reihenfolge(items, 4) == [0, 1, 2, 3]
    assert A.reihenfolge(items, 4, "volumen") == [1, 3, 2, 0]
    with pytest.raises(ValueError):
        A.reihenfolge(items, 4, "zufall")


def test_lieferreihenfolge_ist_die_identitaet():
    assert A.reihenfolge(((3, 3), (9, 1), (1, 9)), 0) == [0, 1, 2]


def test_schranke_nimmt_das_groessere_mass():
    assert A.schranke(((10, 1), (10, 1), (1, 10)), 10) == 3         # Volumen 21 -> 3, Gewicht 12 -> 2
    assert A.schranke(((1, 10), (1, 10), (10, 1)), 10) == 3         # umgekehrt
    assert A.schranke(((5, 5), (5, 5)), 10) == 1                    # genau voll: kein Aufrunden


def test_ungueltige_eingaben_werfen():
    with pytest.raises(ValueError):
        A.pack(((11, 1),), [0], 10, 0)         # Volumen größer als die Kapazität
    with pytest.raises(ValueError):
        A.pack(((1, 11),), [0], 10, 0)         # Gewicht größer als die Kapazität
    with pytest.raises(ValueError):
        A.pack(((0, 1),), [0], 10, 0)          # Maß null
    with pytest.raises(ValueError):
        A.pack(((3, 4), (2, 2)), [0, 0], 10, 0)    # keine Permutation
    with pytest.raises(ValueError):
        A.pack(((3, 4), (2, 2)), [0], 10, 0)       # unvollständige Reihenfolge
    with pytest.raises(ValueError):
        A.pack(((3, 4),), [0], 10, 7)              # unbekannte Regel
    with pytest.raises(ValueError):
        A.reihenfolge(((3, 4),), 9)                # unbekannter Schlüssel
    with pytest.raises(ValueError):
        Instance(((3, 4),), 0)
    with pytest.raises(ValueError):
        Instance(((3, 11),), 10)
    with pytest.raises(ValueError):
        zufallsinstanz(0, 5, 1)                    # Zusammenhang 0 gibt es nicht (das Handbeispiel ist keine Zufallsinstanz)


def test_optimum_ueber_dem_limit_ist_none():
    items = tuple((1, 1) for _ in range(C.OPT_LIMIT + 1))
    assert A.optimum(items, 10) is None and A.optimum(items, 10, limit=C.OPT_LIMIT + 1) == 2


def test_zufallsinstanz_ist_deterministisch_und_haelt_die_grenzen():
    for zus in C.ZUSAMMENHAENGE:
        inst = zufallsinstanz(zus, 50, 123)
        assert inst == zufallsinstanz(zus, 50, 123) and inst != zufallsinstanz(zus, 50, 124)
        assert all(C.LO <= x <= C.HI for t in inst.items for x in t)
    assert mess_seed(1, 0, 0) == 1_001_000 and mess_seed(3, 2, 99) == 3_003_099
