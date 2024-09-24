# Copyright © 2024 弥影祐 (yakage_yu)
# Released under the MIT license
# https://opensource.org/license/mit

if "bpy" in locals():
	import importlib
	importlib.reload(translation)
else:
	from . import translation as Tr

import bpy
from bpy.props import IntProperty
import inspect

pgt = bpy.app.translations.pgettext
pgt_t = bpy.app.translations.pgettext_tip


class ACTION_PT_FrameStepperPanel(bpy.types.Panel):
	#bl_translation_context = Tr.ctx1
	bl_label = "NLA Strip Stepper"
	bl_description = pgt_t("Changes the active NLA strip to transition at the specified interval")
	bl_space_type = "DOPESHEET_EDITOR"
	bl_region_type = "UI"
	bl_category = "Action"

	def draw(self, context):
		layout = self.layout
		strip = get_active_nla_strip(context)
		if strip is None:
			layout.column().label(text=pgt("No active NLA Strip"), text_ctxt=Tr.ctx1)
			return

		fcurve = strip.fcurves.find("strip_time")
		column = layout.column(align=False)
		row = column.row(align=False)
		row.scale_x = 2.0
		row.operator(STRIP_OT_UseAnimatedStripTime.bl_idname, text=pgt("Use Limited Animation"), depress=strip.use_animated_time, text_ctxt=Tr.ctx1)
		row.scale_x = 1.2
		if fcurve is not None and fcurve.lock:
			row.operator(STRIP_OT_LockStripTimeChannel.bl_idname, text="", icon="LOCKED", depress=True)
		else:
			row.operator(STRIP_OT_LockStripTimeChannel.bl_idname, text="", icon="UNLOCKED", depress=False)
		column.separator(factor=0.5)

		split = layout.split(factor=0.75)
		col_left = split.column(align=True)
		row = col_left.row(align=True)
		op = row.operator(ACTION_OT_SetStripTime.bl_idname, text=pgt("2 frames"), text_ctxt=Tr.ctx1)
		op.frames = 2
		op = row.operator(ACTION_OT_SetStripTime.bl_idname, text=pgt("3 frames"), text_ctxt=Tr.ctx1)
		op.frames = 3

		col_left.separator(factor=1.5)
		row = col_left.row(align=True)
		row.operator(ACTION_OT_InsertStripTime.bl_idname, text=pgt("Insert"), text_ctxt=Tr.ctx1)
		row.operator(ACTION_OT_AdjustStripTime.bl_idname, text=pgt("Adjust!"), text_ctxt=Tr.ctx1)

		col_right = split.column(align=True)
		col_right.separator(factor=1.5)
		col_right.row().label(text="")
		col_right.operator(ACTION_OT_ClearStripTime.bl_idname, text=pgt("CA"), text_ctxt=Tr.ctx1)


class ACTION_OT_SetStripTime(bpy.types.Operator):
	bl_idname = "action.setstriptime"
	bl_label = "Set Strip Time"
	bl_description = pgt_t("Changes the active NLA strip to transition at the specified interval")
	bl_options = {"REGISTER", "UNDO"}

	frames: IntProperty(default=0, min=0, options={"HIDDEN"})

	def execute(self, context):
		strip = get_active_nla_strip(context)
		if strip is None:
			self.report({"WARNING"}, "No active NLA strip found")
			return {"CANCELLED"}

		if not clear_keyframe_strip_time(self, context, strip):
			return {"CANCELLED"}
		frame_start = strip.frame_start
		strip_length = int(strip.frame_end - frame_start)
		action_frame_start = strip.action_frame_start
		action_length = int(strip.action_frame_end - action_frame_start)

		i = 0
		while i < strip_length:
			strip.strip_time = int(action_frame_start + i % action_length)
			strip.keyframe_insert(data_path="strip_time", frame=int(frame_start + i))
			#print(f"Processing frame {i} in strip {strip.name}")
			i += self.frames

		change_fcurve_constant(self, strip.fcurves.find("strip_time"))
		return {"FINISHED"}


class ACTION_OT_InsertStripTime(bpy.types.Operator):
	bl_idname = "action.insertstriptime"
	bl_label = "Insert Strip Time"
	bl_description = pgt_t("Insert a Strip Time Keyframe at the current frame")
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		strip = get_active_nla_strip(context)
		if strip is None:
			self.report({"WARNING"}, "No active NLA strip found")
			return {"CANCELLED"}

		frame_start = strip.frame_start
		frame_end = strip.frame_end
		current_frame = context.scene.frame_current
		if current_frame < frame_start and current_frame >= frame_end:
			self.report({"WARNING"}, "Keyframes cannot be inserted outside the range of the NLA Strip")
			return {"CANCELLED"}

		action_frame_start = strip.action_frame_start
		action_frame_end = strip.action_frame_end
		action_frame = (current_frame - frame_start) % (action_frame_end - action_frame_start) + action_frame_start
		strip.strip_time = int(action_frame)
		strip.keyframe_insert(data_path="strip_time", frame=int(current_frame))

		change_fcurve_constant(self, strip.fcurves.find("strip_time"))
		return {"FINISHED"}


class ACTION_OT_AdjustStripTime(bpy.types.Operator):
	bl_idname = "action.adjuststriptime"
	bl_label = "Adjust Strip Time"
	bl_description = pgt_t("Align Strip Time Keyframe with NLA Strip Start")
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		strip = get_active_nla_strip(context)
		if strip is None:
			self.report({"WARNING"}, "No active NLA strip found")
			return {"CANCELLED"}

		if not adjust_strip_time(self, context, strip):
			return {"CANCELLED"}
		return {"FINISHED"}


class ACTION_OT_ClearStripTime(bpy.types.Operator):
	bl_idname = "strip.clearstriptime"
	bl_label = "Clear Strip Time"
	bl_description = pgt_t("Clear the keyframes of the Strip Time")
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		strip = get_active_nla_strip(context)
		if strip is None:
			self.report({"WARNING"}, "No active NLA strip found")
			return {"CANCELLED"}

		if not clear_keyframe_strip_time(self, context, strip):
			return {"CANCELLED"}
		return {"FINISHED"}


class STRIP_OT_UseAnimatedStripTime(bpy.types.Operator):
	bl_idname = "strip.useanimatedstriptime"
	bl_label = pgt("Use Animated Strip Time")
	bl_description = pgt_t("Use Animated Strip Time")
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		strip = get_active_nla_strip(context)
		if strip is None:
			self.report({"WARNING"}, "No active NLA strip found")
			return {"CANCELLED"}
		strip.use_animated_time = not strip.use_animated_time
		return {"FINISHED"}


class STRIP_OT_LockStripTimeChannel(bpy.types.Operator):
	bl_idname = "strip.lockstriptimechannel"
	bl_label = pgt("Lock Strip Time Channel")
	bl_description = pgt_t("Lock Strip Time Channel")
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		strip = get_active_nla_strip(context)
		if strip is None:
			self.report({"WARNING"}, "No active NLA strip found")
			return {"CANCELLED"}
		fcurve = strip.fcurves.find("strip_time")
		if fcurve is None:
			self.report({"WARNING"}, "No keyframes for Strip Time are set in the active NLA Strip")
			return {"CANCELLED"}

		fcurve.lock = not fcurve.lock
		return {"FINISHED"}


def get_active_nla_strip(
		context:bpy.types.Context) -> bpy.types.NlaStrip:

	obj = context.object
	nla_tracks = obj.animation_data.nla_tracks
	for track in nla_tracks:
		for strip in track.strips:
			if strip.select:
				return strip
	return None


def clear_keyframe_strip_time(
		self:bpy.types.Operator,
		context:bpy.types.Context,
		strip:bpy.types.NlaStrip) -> bool:

	fname = inspect.currentframe().f_code.co_name
	if strip is None:
		self.report({"WARNING"}, f"'strip is None' in function '{fname}'")
		return False
	fcurve = strip.fcurves.find("strip_time")
	if fcurve is None:
		self.report({"WARNING"}, f"'fcurve is None' in function '{fname}'")
		return False
	if fcurve.lock:
		self.report({"WARNING"}, "The Strip Time channel is locked")
		return False

	fcurve.keyframe_points.clear()
	fcurve.update()
	context.area.tag_redraw()
	return True


def adjust_strip_time(
		self:bpy.types.Operator,
		context:bpy.types.Context,
		strip:bpy.types.NlaStrip) -> bool:

	fcurve = strip.fcurves.find("strip_time")
	if fcurve is None or fcurve.keyframe_points is None:
		self.report({"WARNING"}, "No keyframes for Strip Time are set in the active NLA Strip")
		return False

	frame_start = strip.frame_start
	first_keyframe = min(fcurve.keyframe_points, key=lambda kf: kf.co.x)
	offset = frame_start - first_keyframe.co.x
	if offset != 0:
		for keyframe in fcurve.keyframe_points:
			keyframe.co.x += offset

	# NLAストリップの末尾をストリップ時間の最終キーフレームに合わせる
	last_keyframe = max(fcurve.keyframe_points, key=lambda kf: kf.co.x)
	strip_action_length = strip.action_frame_end - strip.action_frame_start
	target_length = last_keyframe.co.x - first_keyframe.co.x
	strip.repeat = target_length / strip_action_length

	context.area.tag_redraw()
	return True


def change_fcurve_constant(
		self:bpy.types.Operator,
		fcurve:bpy.types.FCurve) -> bool:

	if fcurve is None:
		self.report({"WARNING"}, "The Strip Time channel is locked")
		return False

	for keyframe_point in fcurve.keyframe_points:
		keyframe_point.interpolation = "CONSTANT"
	fcurve.update()
	return True


classes = [
	ACTION_PT_FrameStepperPanel,
	ACTION_OT_SetStripTime,
	ACTION_OT_InsertStripTime,
	ACTION_OT_AdjustStripTime,
	ACTION_OT_ClearStripTime,
	STRIP_OT_UseAnimatedStripTime,
	STRIP_OT_LockStripTimeChannel,
]


def register():
	for c in classes:
		bpy.utils.register_class(c)


def unregister():
	for c in classes:
		bpy.utils.register_class(c)
