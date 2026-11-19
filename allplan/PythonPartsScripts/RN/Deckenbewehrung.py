"""Allplan 2026 diagnostic entry point. Never writes or hides model elements.

Prismatic geometry extraction is implemented but not locally validated in Allplan. Keep creation disabled, rather than offering an unsafe success path.
See docs/API-NACHWEIS.md for verified source references.
"""
from pathlib import Path
import sys
# Explicitly add our sibling package root, not the working directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rn_deckenbewehrung.asf import read_allplot
from rn_deckenbewehrung.model import ValidationError
from RN.SlabGeometry import extract_slab
import NemAll_Python_BaseElements as Base
import NemAll_Python_IFW_ElementAdapter as Adapter
from BaseScriptObject import BaseScriptObject
from CreateElementResult import CreateElementResult
from ScriptObjectInteractors.SingleElementSelectInteractor import (
    SingleElementSelectInteractor, SingleElementSelectResult,
)
from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult


def check_allplan_version(build_ele, version):
    return str(version).startswith('2026')


def create_script_object(build_ele, script_object_data):
    return Deckenbewehrung(build_ele, script_object_data)


class Deckenbewehrung(BaseScriptObject):
    def __init__(self, build_ele, script_object_data):
        super().__init__(script_object_data)
        self.build_ele = build_ele
        self.selection = SingleElementSelectResult()

    def start_input(self):
        self.script_object_interactor = SingleElementSelectInteractor(
            self.selection, [Adapter.Slab_TypeUUID], 'Stahlbetondecke auswählen')

    def start_next_input(self):
        self.script_object_interactor = None
        slab = Base.GetElement(self.selection.sel_element)
        props = slab.Properties
        self.build_ele.Thickness.value = 'Noch nicht ermittelt'
        self.build_ele.BottomZ.value = 'Noch nicht ermittelt'
        self.build_ele.TopZ.value = 'Noch nicht ermittelt'
        if props.TierCount != 1:
            self.build_ele.Status.value = 'Mehrschichtige Decken werden noch nicht unterstützt.'
            return
        try:
            snapshot = extract_slab(self.selection.sel_element)
            self.build_ele.Thickness.value = f'{snapshot.thickness:g} mm'
            self.build_ele.BottomZ.value = f'{snapshot.bottom_z:g} mm'
            self.build_ele.TopZ.value = f'{snapshot.bottom_z+snapshot.thickness:g} mm'
            self.build_ele.Status.value = f'Prismatische Decke: {len(snapshot.contours)} Randkonturen. Erzeugung noch gesperrt.'
        except (ValidationError, RuntimeError, TypeError, AttributeError) as exc:
            self.build_ele.Status.value = f'Deckenauswertung abgebrochen: {exc}'

    def modify_element_property(self, name, value):
        if name != 'AsfPath':
            return False
        self.build_ele.ImportStatus.value = 'Keine Datei gewählt.'
        if not value:
            return True
        try:
            model = read_allplot(value)
            self.build_ele.ImportStatus.value = (
                f'{len(model.nodes)} Knoten; {len(model.elements)} Elemente; '
                f'{len(model.results)} QM1-Wertezeilen. Spaltenzuordnung noch ungeprüft.')
        except (OSError, UnicodeError, ValidationError) as exc:
            self.build_ele.ImportStatus.value = f'ASF nicht verwendbar: {exc}'
        return True

    def execute(self):
        return CreateElementResult([])

    def on_cancel_function(self):
        return OnCancelFunctionResult.CANCEL_INPUT
