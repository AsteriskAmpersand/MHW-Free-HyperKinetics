# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 08:56:13 2021

@author: AsteriskAmpersand
"""

import os
import bpy
import bpy.utils.previews

from pathlib import Path

pcoll = bpy.utils.previews.new()
pcoll.load("FREEHK", str(Path(__file__).parent.parent/"icons/FreeHKIcon.png"), "IMAGE")
pcoll.load("FREEHK_TOTAL", str(Path(__file__).parent.parent/"icons/FreeHKIcon.png"), "IMAGE")

pcoll.load("FREEHK_CLEAR", str(Path(__file__).parent.parent/"icons/FreeHKIconTetherClearPartial.png"), "IMAGE")
pcoll.load("FREEHK_CLEAR_TOTAL", str(Path(__file__).parent.parent/"icons/FreeHKIconTetherClearTotal.png"), "IMAGE")
pcoll.load("FREEHK_TRANSFER", str(Path(__file__).parent.parent/"icons/FreeHKIconTransfer.png"), "IMAGE")
pcoll.load("FREEHK_TRANSFER_TOTAL", str(Path(__file__).parent.parent/"icons/FreeHKIconTransferAll.png"), "IMAGE")
pcoll.load("FREEHK_TRANSFER_SILENT", str(Path(__file__).parent.parent/"icons/FreeHKIconTransferSilent.png"), "IMAGE")
pcoll.load("FREEHK_TRANSFER_SILENT_TOTAL", str(Path(__file__).parent.parent/"icons/FreeHKIconTransferSilentAll.png"), "IMAGE")

pcoll.load("FREEHK_BONES", str(Path(__file__).parent.parent/"icons/FreeHKIconBone.png"), "IMAGE")
pcoll.load("FREEHK_BONES_TOTAL", str(Path(__file__).parent.parent/"icons/FreeHKIconBoneAll.png"), "IMAGE")
pcoll.load("FREEHK_NAMES", str(Path(__file__).parent.parent/"icons/FreeHKIconNames.png"), "IMAGE")
pcoll.load("FREEHK_NAMES_TOTAL", str(Path(__file__).parent.parent/"icons/FreeHKIconNamesAll.png"), "IMAGE")
pcoll.load("FREEHK_CHANNELS", str(Path(__file__).parent.parent/"icons/FreeHKIconChannels.png"), "IMAGE")
pcoll.load("FREEHK_CHANNELS_TOTAL", str(Path(__file__).parent.parent/"icons/FreeHKIconChannelsAll.png"), "IMAGE")
pcoll.load("FREEHK_SYNCRHONIZE", str(Path(__file__).parent.parent/"icons/FreeHKIconSynchro.png"), "IMAGE")
pcoll.load("FREEHK_SYNCRHONIZE_TOTAL", str(Path(__file__).parent.parent/"icons/FreeHKIconSynchroAll.png"), "IMAGE")
pcoll.load("FREEHK_RESAMPLE", str(Path(__file__).parent.parent/"icons/FreeHKIconResample.png"), "IMAGE")
pcoll.load("FREEHK_RESAMPLE_TOTAL", str(Path(__file__).parent.parent/"icons/FreeHKIconResampleAll.png"), "IMAGE")
pcoll.load("FREEHK_CHECK", str(Path(__file__).parent.parent/"icons/FreeHKIconCheckExport.png"), "IMAGE")
pcoll.load("FREEHK_CHECK_TOTAL", str(Path(__file__).parent.parent/"icons/FreeHKIconCheckExportAll.png"), "IMAGE")
pcoll.load("FREEHK_CLEAR_ENCODE", str(Path(__file__).parent.parent/"icons/FreeHKIconClearQuality.png"), "IMAGE")
pcoll.load("FREEHK_CLEAR_ENCODE_TOTAL", str(Path(__file__).parent.parent/"icons/FreeHKIconClearQualityAll.png"), "IMAGE")
pcoll.load("FREEHK_MAX_ENCODE", str(Path(__file__).parent.parent/"icons/FreeHKIconMaxQuality.png"), "IMAGE")
pcoll.load("FREEHK_MAX_ENCODE_TOTAL", str(Path(__file__).parent.parent/"icons/FreeHKIconMaxQualityAll.png"), "IMAGE")
pcoll.load("FREEHK_PREVIEW", str(Path(__file__).parent.parent/"icons/FreeHKIconPreview.png"), "IMAGE")



pcoll.load("FREEHK_NONE_TYPE", str(Path(__file__).parent.parent/"icons/FreeHKIconNoneType.png"), "IMAGE")
pcoll.load("FREEHK_LMT_TYPE", str(Path(__file__).parent.parent/"icons/FreeHKIconLMTType.png"), "IMAGE")
pcoll.load("FREEHK_TIML_TYPE", str(Path(__file__).parent.parent/"icons/FreeHKIconTIMLType.png"), "IMAGE")

pcoll.load("FREEHK_FILE", str(Path(__file__).parent.parent/"icons/FreeHKFile.png"), "IMAGE")
pcoll.load("FREEHK_SELECTED_FILE", str(Path(__file__).parent.parent/"icons/FreeHKSelectedFile.png"), "IMAGE")
pcoll.load("FREEHK_LMT_FILE", str(Path(__file__).parent.parent/"icons/FreeHKLMTFile.png"), "IMAGE")
pcoll.load("FREEHK_TIML_FILE", str(Path(__file__).parent.parent/"icons/FreeHKTIMLFile.png"), "IMAGE")
pcoll.load("FREEHK_EFX_FILE", str(Path(__file__).parent.parent/"icons/FreeHKEFXFile.png"), "IMAGE")

pcoll.load("FREEHK_ERR_ERROR", str(Path(__file__).parent.parent/"icons/FreeHKIconErrorError.png"), "IMAGE")
pcoll.load("FREEHK_ERR_OMIT", str(Path(__file__).parent.parent/"icons/FreeHKIconErrorOmit.png"), "IMAGE")
pcoll.load("FREEHK_ERR_FIX", str(Path(__file__).parent.parent/"icons/FreeHKIconErrorFix.png"), "IMAGE")