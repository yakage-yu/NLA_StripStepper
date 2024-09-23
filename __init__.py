# Copyright © 2024 弥影祐 (yakage_yu)
# Released under the MIT license
# https://opensource.org/license/mit

bl_info = {
	"name": "NLA Strip Stepper",
	"description": "Changes the active NLA strip to transition at the specified interval",
	"author": "yakage_yu [X(twitter):@yakage_yu]",
	"version": (0, 1),
	"blender": (4, 0, 0),
	"category": "Animation",
	"location": "Dope Sheet",
	"warning": "Executing Reload Scripts in Blender System may cause instability issues",
	"wiki_url": "",
	"tracker_url": "",
}

if "bpy" in locals():
	import importlib
	importlib.reload(nla_strip_stepper)
	importlib.reload(translation)
else:
	from . import nla_strip_stepper
	from . import translation

import bpy


def register():
	try:
		bpy.app.translations.register(__name__, translation.translation_dict)
	except: pass

	nla_strip_stepper.register()


def unregister():
	try:
		bpy.app.translations.unregister(__name__)
	except: pass

	nla_strip_stepper.unregister()


if __name__ == "__main__":
	register()
