"""Allplan 2026 diagnostic entry point. Never writes or hides model elements.

The production geometry extraction (including openings and global Z) is not yet
validated. Keep creation disabled, rather than offering an unsafe success path.
See docs/API-NACHWEIS.md for verified source references.
"""
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
        if props.TierCount != 1:
            self.build_ele.Status.value = 'Mehrschichtige Decken werden noch nicht unterstützt.'
            return
        self.build_ele.Thickness.value = f'{props.GetSlabTierProperties(0).Thickness:g} mm'
        self.build_ele.Status.value = 'Decke erkannt. Öffnungen und Höhenbezug noch ungeprüft; Erzeugung gesperrt.'

    def execute(self):
        return CreateElementResult([])

    def on_cancel_function(self):
        return OnCancelFunctionResult.CANCEL_INPUT
