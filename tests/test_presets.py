"""Presets: Vollständigkeit, gültige Werte, erstes Preset = Standardeinstellungen, jedes Preset liefert die versprochene Aussage."""

import vkp_algorithm as A
import vkp_constants as C
import vkp_evaluation as ev
import vkp_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_widget_bounds():
    for name, preset in C.PRESETS.items():
        for key, state_key in P.PRESET_KEYS.items():
            spec = P.SETTING_SPECS[state_key]
            assert spec.lo <= preset[key] <= spec.hi, (name, key)


def test_first_preset_equals_the_default_settings():
    assert ev.Settings(**next(iter(C.PRESETS.values()))) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_defaults_of_the_widgets_equal_the_default_settings():
    s = ev.Settings()
    assert [P.SETTING_SPECS[k].default for k in ("quelle_select", "n_select", "seed_input", "schluessel_select", "regel_select")] == [s.quelle, s.n_index, s.seed, s.schluessel, s.regel]


def test_presets_behaupten_nur_was_stimmt():
    """Die Hilfetexte der Presets sagen Volumen: zwei Behälter schlechter als das Optimum; Summe: optimal; die beiden Zufallsinstanzen: gegenläufig bzw. gleichlaufend."""
    volumen = ev.analyse(ev.Settings(**C.PRESETS["Handbeispiel, nach Volumen"]))
    summe = ev.analyse(ev.Settings(**C.PRESETS["Handbeispiel, nach der Summe"]))
    assert volumen.count - volumen.opt == 2 and "zwei Behälter schlechter" in C.PRESET_HELP["Handbeispiel, nach Volumen"]
    assert summe.count == summe.opt and "optimal" in C.PRESET_HELP["Handbeispiel, nach der Summe"]
    for name, quelle in (("Gegenläufige Maße, nach Gewicht", 3), ("Gleichlaufende Maße, nach Volumen", 2)):
        assert C.PRESETS[name]["quelle"] == quelle
    gegen = ev.analyse(ev.Settings(**C.PRESETS["Gegenläufige Maße, nach Gewicht"]))
    assert all(v + w >= 45 for v, w in gegen.inst.items)           # Gewicht ≈ 55 − Volumen
    assert A.container_pruefen(gegen.inst.items, [list(b) for b in gegen.bins], gegen.inst.cap)
