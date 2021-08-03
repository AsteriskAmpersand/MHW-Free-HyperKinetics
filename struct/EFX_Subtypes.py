import construct as C

Transform3D=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"translate" / C.XYZ(0),
	"rotate" / C.XYZ(0),
	"resize" / C.XYZ(0),
	"unkn1" / C.Int32sl,
	"Translation_Velocity" / C.XYZ(0),
	"Translation_Velocity_Modifier" / C.XYZ(0),
	"Rotation_Velocity" / C.XYZ(0),
	"Rotation_Velocity_Modifier" / C.XYZ(0),
	"Scale_Velocity" / C.XYZ(0),
	"Scale_Velocity_Modifier" / C.XYZ(0),
	"enableVelocityBitflag" / C.Int32sl,
)
ParentOptions=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"translation_tracking" / C.XYZ(1),
	"angle_tracking" / C.XYZ(1),
	"scale_tracking" / C.XYZ(1),
	"spawnTrack" / C.Int32sl,
	"unkn1" / C.Int32sl,
	"spawnLock" / C.Int32sl,
	"bleedPos" / C.Int32sl,
	"bone_lim" / C.Int32sl,
)
Spawn=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"instancesSpawnedTotal" / C.Int32sl,
	"instancesSpawnedPerFrame" / C.Int32sl,
	"randomizedSpawnsPerFrame" / C.Int32sl,
	"frameDelayBetweenSpawns" / C.Int32sl,
	"randomizedDelay" / C.Int32sl,
	"durationOfSpawnerLifespan" / C.Int32sl,
	"randomizedLifespan" / C.Int32sl,
	"unkn00" / C.Int32sl[2],
	"occur" / C.Int32sl,
	"occur2" / C.Int32sl,
	"unkn10" / C.Int32ul,
	"unkn11" / C.Int32ul,
	"repeatAtribute" / C.Int32ul,
	"unkn21" / C.Int32ul,
	"unkn30" / C.Int32ul,
	"unkn31" / C.Int32ul,
)
Life=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"fadeInDuration" / C.Int32sl,
	"fadeInDurationJitter" / C.Int32sl,
	"duration" / C.Int32sl,
	"durationJitter" / C.Int32sl,
	"unkn2" / C.Int32sl[2],
	"fadeOutDuration" / C.Int32sl,
	"fadeOutDurationJitter" / C.Int32sl,
	"unkn3" / C.Int32sl[2],
	"indefiniteLifespan" / C.Int32sl,
)
EmitterShape3D=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"transform" / C.XYZ(0),
	"patternControl" / C.Int32sl,
	"unkn2" / C.Int32sl,
	"unkn3_f0" / C.Float32l[4],
	"unkn3_i0" / C.Int32sl,
	"spawnAngleLimits" / C.Float32l,
	"unkn3_f1" / C.Float32l,
	"unkn3_i1" / C.Int32sl,
	"spawnCount" / C.Int32sl,
	"unkn3_f2" / C.Float32l[3],
	"unkn4" / C.Int32sl,
)
Velocity3D=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[3],
	"unkn1" / C.Float32l[2],
	"NULL0" / C.Int32sl[4],
	"expansion_radius_limit" / C.Float32l,
	"expansion_radius_jitter" / C.Float32l,
	"expansion_radius_elasticity" / C.Float32l,
	"expansion_radius_elasticity_jitter" / C.Float32l,
	"unkn2_04" / C.Float32l,
	"unkn2_05" / C.Float32l,
	"unkn2_06" / C.Float32l,
	"unkn2_07" / C.Float32l,
	"unkn2_08" / C.Float32l,
	"unkn2_09" / C.Float32l,
	"unkn2_10" / C.Int32sl,
	"gravity" / C.Float32l,
	"gravity_jitter" / C.Float32l,
	"NULL1" / C.Int32sl[2],
	"gravityDelay" / C.Int32sl,
	"gravityDelayJitter" / C.Int32sl,
	"NULL2" / C.Int32sl,
)
FadeByDepth=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"viewAngleLimit" / C.Float32l,
	"clipMin" / C.Float32l,
	"fadeStart" / C.Float32l,
	"clipMax" / C.Float32l,
)
RibbonBlade=C.Struct(
	"type" / C.Int32sl,
	"unkn00" / C.Int32sl,
	"unkn01" / C.Int32sl,
	"spacer0" / C.Int32sl,
	"unkn03" / C.Int32sl,
	"unkn04" / C.Float32l,
	"unkn05" / C.Int32sl[2],
	"spacer1" / C.Int32sl,
	"unkn07" / C.Int32sl[2],
	"maxLengthLimit" / C.Float32l,
	"contractionSpeed" / C.Float32l,
	"colourTransitionPoint" / C.Float32l,
	"emissiveStrength" / C.Float32l,
	"unkn08" / C.Float32l,
	"spacer2" / C.Int32sl,
	"unkn10" / C.Int32sl,
	"uvRepetition" / C.Float32l,
	"unkn12" / C.Int32sl[3],
	"spacer3" / C.Int32sl,
	"head" / C.EPVColorSlot,
	"tailEnd" / C.EPVColorSlot,
	"unkn23" / C.Float32l,
	"NULL5" / C.Int32sl,
	"unkn24" / C.Float32l,
	"NULL6" / C.Int32sl,
	"unkn25" / C.Float32l,
	"NULL7" / C.Int32sl,
	"unkn26" / C.Float32l,
	"NULL8" / C.Int32sl,
	"NULL9" / C.Int16sl,
	"path_len" / C.Int32sl,
	"p" / C.Byte[C.this.path_len],
)
dds_data=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"applicationRule" / C.Int32sl,
	"color" / C.XYZ(2)[2],
	"brightness" / C.Float32l,
	"unkn2" / C.Int32sl[3],
	"EPVColorSlot1" / C.Int32sl,
	"SlotOverride1" / C.Int32sl,
	"EPVColorSlot2" / C.Int32sl,
	"SlotOverride2" / C.Int32sl,
	"scale" / C.Float32l,
	"scaleJitter" / C.Float32l,
	"width" / C.Float32l,
	"widthJitter" / C.Float32l,
	"height" / C.Float32l,
	"heightJitter" / C.Float32l,
	"flowmapSpeed" / C.Float32l,
	"flowmapSpeedJitter" / C.Float32l,
	"flowmapAcceleration" / C.Float32l,
	"flowmapAccelerationJitter" / C.Float32l,
	"flowmapStrength" / C.Float32l,
	"flowmapStrengthJitter" / C.Float32l,
	"flowmapStrengthAcceleration" / C.Float32l,
	"flowmapStrengthAccelerationJitter" / C.Float32l,
	"path_len" / C.Int32sl,
)
billboard_data=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"applicationRule" / C.Int32sl,
	"color" / C.XYZ(2)[2],
	"brightness" / C.Float32l,
	"unkn2" / C.Int32sl[3],
	"EPVColorSlot1" / C.Int32sl,
	"SlotOverride1" / C.Int32sl,
	"unknDimension" / C.Float32l,
	"unknDimensionJitter" / C.Float32l,
	"scale" / C.Float32l,
	"scaleJitter" / C.Float32l,
	"width" / C.Float32l,
	"widthJitter" / C.Float32l,
	"height" / C.Float32l,
	"heightJitter" / C.Float32l,
	"flowmapSpeed" / C.Float32l,
	"flowmapSpeedJitter" / C.Float32l,
	"flowmapAcceleration" / C.Float32l,
	"flowmapAccelerationJitter" / C.Float32l,
	"flowmapStrength" / C.Float32l,
	"flowmapStrengthJitter" / C.Float32l,
	"flowmapStrengthAcceleration" / C.Float32l,
	"flowmapStrengthAccelerationJitter" / C.Float32l,
	"path_len" / C.Int32sl,
)
Billboard3D=C.Struct(
	"dds" / C.billboard_data,
	"unkn5" / C.Int32sl,
	"unkn6" / C.uint64,
	"unkn7" / C.Float32l,
	"unkn8" / C.Int32sl,
	"unkn9" / C.Int32sl,
	"p" / C.Byte[C.this.dds.path_len],
)
Plane=C.Struct(
	"dds" / C.dds_data,
	"unkn5" / C.Int32sl[4],
	"rotation" / C.XYZ(0),
	"unkn7" / C.uint64,
	"p" / C.Byte[C.this.dds.path_len],
)
RgbWater=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"color" / C.XYZ(2)[2],
	"brightnessSlot1" / C.Float32l,
	"emissiveMultiplier" / C.Float32l,
	"brightnessSlot2" / C.Float32l,
	"brightnessSlotMultiplier1" / C.Float32l,
	"brightnessSlotMultiplier2" / C.Float32l,
	"opacity" / C.Float32l,
	"unknownFloat" / C.Float32l,
	"unknownInt" / C.Int32sl[3],
	"unkn2" / C.Int32sl[26],
	"path_len" / C.Int32sl,
	"p" / C.Byte[C.this.path_len],
)
ScaleAnim=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"animationSpeed" / C.Float32l,
	"NULL" / C.Int32sl,
	"scaleSpeed" / C.Float32l,
	"scaleSpeedJitter" / C.Float32l,
	"unkn1" / C.Float32l[2],
	"scaleAccel" / C.Float32l,
	"scaleAccelJitter" / C.Float32l,
	"unkn2" / C.Float32l[8],
	"delay" / C.Int32sl,
	"delayJitter" / C.Int32sl,
)
UVSequence=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"uvs_index" / C.Int32sl,
	"NULL" / C.Int32sl,
	"startingFrame" / C.Int32sl,
	"startingFrameJitter" / C.Int32sl,
	"animationSpeed" / C.Float32l,
	"animationSpeedJitter" / C.Float32l,
	"animationAcceleration" / C.Float32l,
	"animationAccelerationJitter" / C.Float32l,
	"loopingEnum" / C.Int32sl,
	"path_len" / C.Int32sl,
	"p" / C.Byte[C.this.path_len],
)
AlphaCorrection=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"unkn1" / C.Float32l,
	"transparentness" / C.Float32l,
	"NULL" / C.Int32sl,
	"unkn2" / C.Int32sl,
)
ShaderSettings=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"unkn1" / C.Int32sl,
	"spacer" / C.Int32sl,
	"unkn2" / C.Int32sl,
	"zDepthModifierStart" / C.Float32l,
	"zDepthModifierEnd" / C.Float32l,
	"unkn3_0" / C.Int32sl,
	"unkn3_1" / C.Int32sl,
	"controlBitflag" / C.Int32sl,
	"unkn4" / C.Float32l[16],
	"objectInteractionFlag0" / C.Int8sl,
	"objectInteractionFlag1" / C.Int8sl,
	"objectInteractionFlag2" / C.Int8sl,
	"objectInteractionFlag3" / C.Int8sl,
	"visibleOnPreview" / C.Int32sl,
	"unkn5" / C.Int32sl[2],
)
RgbFire=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"color1" / C.XYZ(2),
	"brightness1" / C.Float32l,
	"color2" / C.XYZ(2),
	"brightness2" / C.Float32l,
	"unkn4" / C.Float32l,
	"brightness3" / C.Float32l,
	"brightness4" / C.Float32l,
	"unkn6" / C.Int32sl[10],
	"unkn7" / C.Int32sl[10],
)
Mod3Properties=C.Struct(
	"unkn0" / C.Int32sl[2],
	"CD1" / C.Int32sl,
	"emissive_saturation" / C.Float32l,
	"emissive_saturation_jitter" / C.Float32l,
	"emissive_brightness" / C.Float32l,
	"emissive_brightness_jitter" / C.Float32l,
	"rotation" / C.XYZ(0),
	"unkn5_2" / C.Float32l,
	"unkn5_3" / C.Float32l,
	"scale" / C.XYZ(0),
	"global_scale" / C.Float32l,
	"global_scale_jitter" / C.Float32l,
	"model_viscon" / C.Int32sl,
	"model_viscon_randomizer" / C.Int32sl,
	"color1" / C.colour,
	"color2" / C.colour,
	"color3" / C.colour,
	"color4" / C.colour,
	"unkn7" / C.Int32sl[3],
	"tracking_flags" / C.Int32sl,
	"unkn40" / C.Int32sl,
	"affectedByLight" / C.Int32sl,
	"shadowCastBitflag" / C.Int32sl,
	"epv_color_slot1" / C.Int32sl,
	"unkn5" / C.Int32sl,
	"epv_color_slot2" / C.Int32sl,
	"unkn6_1" / C.Int32sl,
	"colorize_material1" / C.Int8sl[4],
	"colorize_material2" / C.Int8sl[4],
	"unkn6_2" / C.Int32sl,
	"NULL1" / C.Int16sl,
)
Mesh=C.Struct(
	"type" / C.Int32sl,
	"properties" / C.Mod3Properties,
	"BeginMod3" / C.Int8sl,
	"path1" / C.CString("utf-8"),
	"path2" / C.CString("utf-8"),
)
RotateAnim=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"NULL" / C.Int32sl[2],
	"spin_velocity" / C.XYZ(0),
	"unkn1_0" / C.Float32l,
	"unkn1_1" / C.Float32l,
	"momentum_conservation" / C.Float32l,
	"spin_acceleration" / C.XYZ(0),
	"unkn1_2" / C.Float32l,
)
EFX_Behav=C.Struct(
	"unkn" / C.Int32sl,
	"const0" / C.Int32sl,
	"t" / C.Int32sl,
		C.IfThenElse(C.this.t==0x03,C.Struct(
			"NULL" / C.Int32sl,
			),
			C.IfThenElse(C.this.t==0x05,C.Struct(
				"unkn0" / C.Int16sl,
				),
				C.IfThenElse(C.this.t==0x06,C.Struct(
					"decal_epv_color_slot" / C.Int32sl,
					),
					C.IfThenElse(C.this.t==0x0C,C.Struct(
						"unkn0" / C.Float32l,
						),
						C.IfThenElse(C.this.t==0x0F,C.Struct(
							"color" / C.XYZ(2),
							),
							C.IfThenElse(C.this.t==0x14,C.Struct(
								"unkn1" / C.XYZ(3),
								),
								C.IfThenElse(C.this.t==0x15,C.Struct(
									"unkn0" / C.Float32l,
									"unkn1" / C.Int32sl,
									"unkn2" / C.Float32l,
									"unkn3" / C.Int32sl,
									),
									C.IfThenElse(C.this.t==0x40,C.Struct(
										"unkn0" / C.int64,
										),
										C.IfThenElse(C.this.t==0x80,C.Struct(
											"file_type" / C.Int32sl,
											"path_len" / C.Int32sl,
											"p" / C.Byte[C.this.path_len],
											),C.Pass		))))))))))
EFX_Behavior=C.Struct(
	"unkn0" / C.Int32sl,
	"behav_type_len" / C.Int32sl,
	"para_count" / C.Int32sl,
	"b_type" / C.Byte[C.this.behav_type_len],
	"efx_behav" / C.EFX_Behav[C.this.para_count],
)
PtBehavior=C.Struct(
	"type" / C.Int32sl,
	"efx_behav" / C.EFX_Behavior,
)
PlEmissive=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Float32l,
	"body_p" / C.Int8ul,
	"unkn4" / C.Float32l,
	"area" / C.Float32l[2],
	"bright" / C.Float32l,
	"area_of_aura" / C.Int32sl,
	"radii_effect_unkn0" / C.Float32l,
	"radii_effect_unkn1" / C.Float32l,
	"radii_effect_unkn2" / C.Float32l,
	"unkn5" / C.Float32l[5],
)
Guide=C.Struct(
	"type" / C.Int32sl,
	"initialPosition" / C.Float32l,
	"initialPositionJitter" / C.Float32l,
	"speed" / C.Float32l,
	"speedJitter" / C.Float32l,
	"accel" / C.Float32l,
	"accelJitter" / C.Float32l,
	"innerRadius" / C.Float32l,
	"innerRadiusJitter" / C.Float32l,
	"outerRadius" / C.Float32l,
	"outerRadiusJitter" / C.Float32l,
	"restitutionDelay" / C.Float32l,
	"restitutionDelayJitter" / C.Float32l,
	"restitutionEccentricity" / C.Float32l,
	"restitutionEccentricityJitter" / C.Float32l,
	"restitutionElasticity" / C.Float32l,
	"restitutionElasticityJitter" / C.Float32l,
	"unkn16" / C.Float32l,
	"unkn17" / C.Float32l,
	"unkn18" / C.Float32l,
	"unkn19" / C.Float32l,
	"unkn20" / C.Float32l,
	"unkn21" / C.Float32l,
	"unkn22" / C.Float32l,
	"int_unkn1" / C.Int32sl[2],
	"float_unkn2" / C.Float32l[3],
)

Tex_Set=C.Struct(
	"set" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"t" / C.Int32sl,
	"type" / C.Int32sl,
		C.IfThenElse(C.this.type==0x80,C.Struct(
			"head" / C.Int32sl,
			"NULL" / C.Int32sl,
			"path_len" / C.Int32sl,
			"p" / C.Byte[C.this.path_len],
		),			
		C.IfThenElse(C.this.type==0x03,C.Struct(
			"NULL" / C.Int32sl[3],
            "unkn" / C.Int32sl,
			),
			"NULL" / C.Int32sl[3],
            "unkn" / C.Int32sl,
			),                            
        C.IfThenElse(C.this.type==0x0C,C.Struct(
			"NULL" / C.Int32sl[3],
            "unkn" / C.Int32sl,
			),
			C.IfThenElse(C.this.type==0x15,C.Struct(
				"unkn" / C.Float32l[6],
				),C.Pass)
		)))
Tex_Block=C.Struct(
	"material_name_hash" / C.Int32sl,
	"material_shader_id_hash" / C.Int32sl,
	"unkn03" / C.Int32sl,
	"set_count" / C.Int32sl,
	"set" / C.Tex_Set[C.this.set_count],
)
Material=C.Struct(
	"type" / C.Int32sl,
	"unkn00" / C.int64,
	"block_count" / C.Int32sl,
	"block" / C.Tex_Block[C.this.block_count],
)
Turbulence=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"path_len" / C.Int32sl,
	"p" / C.Byte[C.this.path_len],
	"unkn1" / C.Float32l[3],
	"unkn_set_1" / C.XYZ(0),
	"NULL" / C.int64[3],
	"unkn2" / C.Float32l[12],
	"unkn_set_2" / C.XYZ(0),
	"unkn3" / C.Float32l[5],
)
FadeByEmitterAngle=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn" / C.Int32sl,
	"unkn2" / C.Float32l[4],
)
Ribbon=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"section_length" / C.Int32sl,
	"spacer0" / C.Int32sl,
	"color" / C.XYZ(2),
	"spacer1" / C.Int32sl,
	"color2" / C.XYZ(2),
	"spacer2" / C.Int32sl,
	"brightness" / C.Float32l,
	"unkn4" / C.Int32sl[2],
	"scale" / C.Float32l,
	"scale_jitter" / C.Float32l,
	"width" / C.Float32l,
	"width_jitter" / C.Float32l,
	"length" / C.Float32l,
	"length_jitter" / C.Float32l,
	"uv_map_height" / C.Int32sl,
	"material_tesselation_density" / C.Float32l,
	"material_tesselation_jitter" / C.Float32l,
	"uv_map_width" / C.Float32l,
	"horizontal_physics_subdivision_count" / C.Int32sl,
	"vertical_physics_subdivision_count" / C.Int32sl,
	"unkn15" / C.Float32l,
	"restitution_direction" / C.Int32sl,
	"unkn16" / C.Int32sl[4],
	"startingAngle" / C.Int32sl,
	"startingAngleJitter" / C.Int32sl,
	"unkn16_0" / C.Int32sl[2],
	"unkn16_1" / C.Int16sl,
	"unkn16_2" / C.Int16sl,
	"spacer3" / C.Int32sl,
	"unkn17" / C.Float32l,
	"spacer4" / C.Int32sl,
	"lengthwise_offset_relative_to_camera" / C.Float32l,
	"unknown19_0" / C.Float32l,
	"restitution" / C.Float32l,
	"restitution_jitter" / C.Float32l,
	"inertial_excess" / C.Float32l,
	"inertial_excess_jitter" / C.Float32l,
	"springiness" / C.Float32l,
	"springiness_jitter" / C.Float32l,
	"spacer5" / C.Int32sl,
	"unkn20" / C.Int32sl[4],
	"unkn21" / C.Float32l,
	"unkn22" / C.Int32sl[3],
	"spacer6" / C.Int32sl,
	"unkn23" / C.Float32l[8],
	"unkn24" / C.Int32sl,
	"epvcolor" / C.Int32sl[2],
	"spacer7" / C.Int32sl,
	"base_width_multiplier" / C.Float32l,
	"base_opacity" / C.Float32l,
	"tip_width_multiplier" / C.Float32l,
	"tip_opacity" / C.Float32l,
	"spacer8" / C.Int32sl,
	"unkn27" / C.Float32l[2],
	"visiblePreview" / C.Int16sl,
	"spacer9" / C.Int16sl,
	"base_flap_frequency" / C.Float32l,
	"base_flap_frequency_jitter" / C.Float32l,
	"base_flap_amount" / C.Float32l,
	"base_flap_amount_jitter" / C.Float32l,
	"tip_flap_frequency" / C.Float32l,
	"tip_flap_frequency_jitter" / C.Float32l,
	"tip_flap_amount" / C.Float32l,
	"tip_flap_amount_jitter" / C.Float32l,
	"ib_junk" / C.Int8sl[32],
	"path1" / C.CString("utf-8"),
)
Noise=C.Struct(
	"type" / C.Int32sl,
	"NULL" / C.Int32sl,
	"section_length" / C.Int32sl,
	"spacer" / C.Int32sl,
	"main_axis_speed" / C.Float32l,
	"secondary_axis_speed" / C.Float32l,
	"teleport_radius" / C.Float32l,
	"smooth_radius_randomized" / C.Float32l,
	"main_axis_speed2" / C.Float32l,
	"secondary_axis_speed2" / C.Float32l,
	"teleport_radius2" / C.Float32l,
	"smooth_radius_randomized2" / C.Float32l,
)
uv_transform=C.Struct(
	"u" / C.Float32l,
	"uJitter" / C.Float32l,
	"v" / C.Float32l,
	"vJitter" / C.Float32l,
)
Material_Animation_Data=C.Struct(
	"unkn0" / C.Int32sl,
	"initialPosition" / C.uv_transform,
	"speed" / C.uv_transform,
	"acceleration" / C.uv_transform,
	"scale" / C.uv_transform,
	"scaleSpeed" / C.uv_transform,
	"scaleAcceleration" / C.uv_transform,
)
UVControl=C.Struct(
	"type" / C.Int32sl,
	"uv1" / C.Material_Animation_Data,
	"uv2" / C.Material_Animation_Data,
	"unkn2" / C.Int32sl,
	"extraMaterialInitialPosition" / C.Float32l,
	"extraMaterialInitialPositionJitter" / C.Float32l,
	"extraMaterialSpeed" / C.Float32l,
	"extraMaterialSpeedJitter" / C.Float32l,
	"opacity" / C.Float32l,
	"opacityJitter" / C.Float32l,
	"opacityAcceleration" / C.Float32l,
	"opacityAccelerationJitter" / C.Float32l,
)
FadeByAngle=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Float32l[4],
	"NULL" / C.int64,
	"unkn2" / C.Int32sl[2],
)
EmitterBoundary=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Float32l[8],
)
PtLife=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int16sl,
	"unkn1" / C.Int16sl,
	"timing" / C.Int16sl,
	"unkn3" / C.Int16sl,
	"relationIndex" / C.Int16sl,
	"unkn5" / C.Int16sl,
	"unkn6" / C.Int16sl,
	"unkn7" / C.Int16sl,
	"unkn8" / C.Int16sl,
	"unkn9" / C.Int16sl,
)
ExternReference=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[9],
)
FakePlane=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Int8sl[4],
	"unkn2" / C.Float32l,
	"unkn3" / C.Int32sl,
	"unkn4" / C.Int32sl,
	"unkn5" / C.Float32l[9],
)
Dummy=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Int8sl,
)
RandomFix=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[10],
)
Transform2D=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.int64[2],
	"unkn1" / C.Float32l[2],
)
Billboard2D=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Int32sl[2],
	"unkn2" / C.Float32l[2],
	"unkn3" / C.Int32sl[4],
	"unkn4" / C.Float32l[16],
	"path_len" / C.Int32sl,
	"unkn5" / C.Int32sl[2],
	"p" / C.Byte[C.this.path_len],
)
Blink=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Float32l[11],
)
LuminanceBleed=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"unkn1" / C.Float32l[3],
)
EmitterShape2D=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"unkn1" / C.Float32l[4],
	"unkn2" / C.Int32sl[4],
)
Velocity2D=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Float32l[9],
	"unkn2" / C.Int32sl,
	"unkn3" / C.Float32l[3],
	"unkn4" / C.Int32sl[3],
)
Lightning=C.Struct(
	"type" / C.Int32sl,
	"unkn00" / C.Int32sl[2],
	"spacer0" / C.Int32sl,
	"color1" / C.XYZ(2),
	"unkn02" / C.Int32sl,
	"color2" / C.XYZ(2),
	"unkn03" / C.Int32sl,
	"emissive" / C.XYZ(2),
	"unkn04" / C.Int32sl,
	"spacer05_00" / C.Int32sl,
	"unkn05_01" / C.Int32sl,
	"sineWaveFreq" / C.Float32l,
	"sineWaveFreqJitter" / C.Float32l,
	"alphaThreshold" / C.Float32l,
	"unkn05_05" / C.Float32l,
	"unkn05_06" / C.Float32l,
	"unkn05_07" / C.Float32l,
	"outwardsExpansionSpeed" / C.Float32l,
	"outwardsExpansionSpeedJitter" / C.Float32l,
	"unkn05_10" / C.Float32l,
	"unkn05_11" / C.Int32sl,
	"unkn05_12" / C.Int32sl,
	"unkn05_13" / C.Int32sl,
	"spacer05_14" / C.Int32sl,
	"targetBoneID" / C.Int32sl,
	"unkn05_16" / C.Int32sl,
	"unkn05_17" / C.Float32l,
	"EPVColorSlot1" / C.Int32sl,
	"EPVColorSlot2" / C.Int32sl,
	"unkn05_20" / C.Int32sl,
	"unkn05_21" / C.Int32sl,
	"unkn05_22" / C.Int32sl,
	"unkn05_23" / C.Float32l,
	"unkn05_24" / C.Float32l,
	"inflectionPointCount" / C.Int32sl,
	"uInflectionAngleLimit" / C.Float32l,
	"uInflectionAngleLimitJitter" / C.Float32l,
	"vInflectionAngleLimit" / C.Float32l,
	"vInflectionAngleLimitJitter" / C.Float32l,
	"inflectionPointCount2" / C.Int32sl,
	"uInflectionAngleLimit2" / C.Float32l,
	"uInflectionAngleLimitJitter2" / C.Float32l,
	"vInflectionAngleLimit2" / C.Float32l,
	"vInflectionAngleLimitJitter2" / C.Float32l,
	"glow" / C.Float32l,
	"glowJitter" / C.Float32l,
	"length" / C.Float32l,
	"lengthJitter" / C.Float32l,
	"width" / C.Float32l,
	"widthJitter" / C.Float32l,
	"startWidth" / C.Float32l,
	"uvRepetitionStart" / C.Float32l,
	"endWidth" / C.Float32l,
	"uvRepetitionEnd" / C.Float32l,
	"unkn05_45" / C.Int32sl,
	"unkn05_46" / C.Int32sl,
	"unkn05_47" / C.Int32sl,
	"unkn05_48" / C.Int32sl,
	"unkn06" / C.Int32sl[2],
	"radiusLimit" / C.Float32l,
	"radiusLimitJitter" / C.Float32l,
	"unkn07_02" / C.Float32l,
	"unkn07_03" / C.Float32l,
	"unkn07_04" / C.Int32sl,
	"unkn07_05" / C.Float32l,
	"unkn07_06" / C.Float32l,
	"unkn07_07" / C.Float32l,
	"unkn07_08" / C.Float32l,
	"unkn07_09" / C.Float32l,
	"unkn07_10" / C.Float32l,
	"branchLength" / C.Float32l,
	"branchLengthJitter" / C.Float32l,
	"unkn07_13" / C.Float32l,
	"unkn07_14" / C.Float32l,
	"unkn07_15" / C.Float32l,
	"unkn07_16" / C.Float32l,
	"unkn07_17" / C.Float32l,
	"unkn07_18" / C.Float32l,
	"unkn07_19" / C.Float32l,
	"unkn07_20" / C.Float32l,
	"unkn07_21" / C.Float32l,
	"unkn07_22" / C.Float32l,
	"unkn07_23" / C.Float32l,
	"unkn07_24" / C.Float32l,
	"unkn07_25" / C.Float32l,
	"unkn07_26" / C.Float32l,
	"unkn07_27" / C.Float32l,
	"unkn08" / C.Int32sl[2],
	"unkn09" / C.Float32l[20],
	"unkn10" / C.Int32sl[4],
	"unkn11" / C.Float32l[2],
	"unkn12" / C.Int32sl[2],
	"unkn13" / C.Float32l[6],
	"unkn14" / C.Int32sl[3],
	"unkn15" / C.Float32l[9],
	"unkn16" / C.Int16sl,
	"path_len" / C.Int32sl,
	"p" / C.Byte[C.this.path_len],
)
Refraction=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"pixelNormalOffset" / C.Int32sl,
	"unkn2" / C.Int32sl,
)
MasterOnly=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
)
RayCast=C.Struct(
	"type" / C.Int32sl,
	"unknown0" / C.Int32sl,
	"fixed70" / C.Int32sl,
	"spacer0" / C.Int32sl,
	"distanceMod0" / C.Float32l,
	"distanceMod0Jitter" / C.Float32l,
	"prop1" / C.Float32l,
	"prop1Jitter" / C.Float32l,
	"spacer1" / C.Int32sl,
	"spacer2" / C.Int32sl,
	"spacer3" / C.Int32sl,
	"prop2" / C.Float32l,
	"prop3" / C.XYZ(3),
	"direction" / C.Int32sl,
	"distanceMod1" / C.Float32l,
	"distanceMod1Jitter" / C.Float32l,
	"spacer" / C.Int32sl,
	"unknown1" / C.Int32sl,
	"unknown2" / C.Int16sl,
)
ParentEmissive=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"unkn1" / C.Int32sl,
	"unkn2" / C.Float32l,
	"unkn3" / C.Int32sl,
	"color" / C.XYZ(2),
	"brightness" / C.Float32l,
	"rimParam" / C.Float32l[3],
	"unkn4" / C.Int32sl,
	"blendParam" / C.Float32l[3],
	"unkn8" / C.Float32l[5],
)
TubeLight=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[3],
	"unkn1" / C.Float32l[11],
	"unkn2" / C.Int32sl[2],
	"unkn3" / C.Int32sl[4],
	"unkn4" / C.Float32l[4],
	"unkn5" / C.Int32sl[2],
	"unkn6" / C.Int32sl[4],
	"unkn7" / C.Float32l,
	"path_len" / C.Int32sl,
	"p" / C.Byte[C.this.path_len],
)
ScreenSpaceCollision=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"spacer" / C.Int32sl,
	"unkn1" / C.Float32l,
	"bounce" / C.Float32l,
	"bounceJitter" / C.Float32l,
	"lifespan" / C.Int32sl,
	"lifespanJitter" / C.Int32sl,
	"bounceConditional" / C.Float32l,
)
PtCollision=C.Struct(
	"type" / C.Int32sl,
	"unkn00" / C.Int32sl,
	"physicsEnum" / C.Int32sl,
	"unkn02" / C.Int32sl,
	"unkn03" / C.Int32sl,
	"unkn04" / C.Int32sl,
	"unkn05" / C.Int32sl,
	"unkn06" / C.Float32l,
	"unkn07" / C.Int32sl,
	"unkn1" / C.Float32l[3],
	"unkn2" / C.Int32sl[2],
	"bounceElasticity" / C.Float32l,
	"bounceElasticityJitter" / C.Float32l,
	"bounceElasticityMultiplier" / C.Float32l,
	"horizontalBounce" / C.Float32l,
	"unkn34" / C.Float32l,
	"unkn35" / C.Float32l,
	"unkn36" / C.Float32l,
	"unkn37" / C.Float32l,
	"unkn38" / C.Int32sl,
	"unkn4" / C.Int32sl[2],
	"ieIndex" / C.Int32sl,
	"unkn6" / C.Int32sl[3],
)
Shovel=C.Struct(
	"type" / C.Int32sl,
	"unkn00" / C.Int32sl,
	"unkn01" / C.Int32sl,
	"spacer" / C.Int32sl,
	"width" / C.Float32l,
	"widthJitter" / C.Float32l,
	"height" / C.Float32l,
	"heightJitter" / C.Float32l,
	"length" / C.Float32l,
	"lengthJitter" / C.Float32l,
	"unkn09" / C.Int32sl,
	"unkn10" / C.Int32sl,
	"unkn11" / C.Float32l,
	"unkn12" / C.Int32sl,
	"unkn13" / C.Int32sl,
	"unkn14" / C.Int32sl,
	"pattern" / C.Int32sl,
	"unkn16" / C.Int32sl,
	"unkn17" / C.Int16sl,
)
FakeDoF=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"length" / C.Int32sl,
	"unkn1" / C.Int32sl[C.this.length/4-5],
	"unkn2" / C.Float32l[3],
	"unkn3" / C.Int32sl[2],
)
RepeatArea=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl,
	"length" / C.Int32sl,
	"unkn1" / C.Int32sl[C.this.length/4-5],
	"unkn2" / C.Float32l[3],
	"unkn3" / C.Int32sl[2],
)
LinkPartsVisible=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[3],
)
PlSnow=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"spacer" / C.Int32sl,
	"body_part_id" / C.Int32sl,
	"weapon_id" / C.Int32sl,
	"color" / C.colour,
	"epvcolorslot" / C.Int32sl,
	"alpha_effect" / C.Int32sl,
	"normal_map_strength" / C.Float32l,
	"alpha_threshold" / C.Float32l,
	"unkn4_0" / C.Float32l,
	"unkn4_1" / C.Float32l,
	"unkn5" / C.Int32sl,
	"roughness_multiplier" / C.Float32l,
	"metallicness_multiplier" / C.Float32l,
	"subsurface_multipler" / C.Float32l,
	"unkn6_0" / C.Float32l,
	"craquelure_effect_diffumination" / C.Float32l,
	"craquelure_threshold" / C.Float32l,
	"unkn6_1" / C.Float32l,
	"craquelure_smoothing_threshold" / C.Float32l,
)
PtTrigger=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Int32sl,
	"unkn2" / C.Int32sl,
)
PathChain=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Int32sl,
	"unkn2" / C.Float32l,
	"unkn3" / C.Int32sl,
	"unkn4" / C.Float32l[6],
	"unkn5" / C.Int32sl[8],
	"unkn6" / C.Int8sl,
)
Homing=C.Struct(
	"type" / C.Int32sl,
	"unknown" / C.Int32sl,
	"unknown0" / C.Int32sl,
	"spacer" / C.Int32sl,
	"f0" / C.Float32l,
	"speed" / C.Float32l,
	"speedMultiplier" / C.Float32l,
	"f3" / C.Float32l,
	"f4" / C.Float32l,
	"radius" / C.Float32l,
	"i0" / C.Int32sl,
	"i1" / C.Int32sl,
	"enableRadialVanish" / C.Int32sl,
	"unknown1" / C.Int32sl,
)
EmitterShapeMesh=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Int32sl[3],
	"unkn2" / C.Int8sl[8],
	"unkn3" / C.Int32sl,
	"path1" / C.CString("utf-8"),
)
StrainRibbon=C.Struct(
	"type" / C.Int32sl,
	"unkn00" / C.Int32sl[2],
	"spacer00" / C.Int32sl,
	"color1" / C.XYZ(2),
	"spacer01" / C.Int32sl,
	"color2" / C.XYZ(2),
	"spacer02" / C.Int32sl,
	"emissionStrength" / C.Float32l,
	"unkn03_01" / C.Float32l,
	"spacer03" / C.Int32sl,
	"unkn03_03" / C.Float32l,
	"unkn03_04" / C.Float32l,
	"unkn03_05" / C.Float32l,
	"unkn03_06" / C.Float32l,
	"endPosition" / C.XYZ(3),
	"unkn03_10" / C.Float32l,
	"width" / C.Float32l,
	"widthJitter" / C.Float32l,
	"length" / C.Float32l,
	"lengthJitter" / C.Float32l,
	"startWidth" / C.Float32l,
	"startOpacity" / C.Float32l,
	"endWidth" / C.Float32l,
	"endOpacity" / C.Float32l,
	"subdivisionCount" / C.Int32sl,
	"unkn04_01" / C.Int32sl,
	"uvRepetition" / C.Int32sl,
	"widthwiseUVScalingAlpha" / C.Float32l,
	"spacer04" / C.Int32sl,
	"widthwiseUVScalingBML" / C.Float32l,
	"color3" / C.XYZ(2),
	"unkn06_00" / C.Float32l,
	"unkn06_01" / C.Float32l,
	"unkn06_02" / C.Float32l,
	"unkn06_03" / C.Float32l,
	"unkn06_04" / C.Float32l,
	"unkn06_05" / C.Float32l,
	"unkn06_06" / C.Float32l,
	"unkn06_07" / C.Float32l,
	"unkn06_08_00" / C.Int16sl,
	"unkn06_08_01" / C.Int16sl,
	"lengthBreakpoint" / C.Float32l,
	"lengthBreakpointJitter" / C.Float32l,
	"breakpointLocation" / C.Float32l,
	"breakpointLocationJitter" / C.Float32l,
	"breakDelay" / C.Float32l,
	"breakDelayJitter" / C.Float32l,
	"tension" / C.Float32l,
	"tensionJitter" / C.Float32l,
	"unkn06_17" / C.Float32l,
	"unkn06_18" / C.Float32l,
	"gravityMultiplier" / C.Float32l,
	"gravityMultiplierJitter" / C.Float32l,
	"inertia" / C.Float32l,
	"inertiaJitter" / C.Float32l,
	"poseSnapping" / C.Float32l,
	"poseSnappingJitter" / C.Float32l,
	"endBoneID" / C.Int32sl,
	"positionalAberration_01" / C.Int32sl,
	"positionalAberration_02" / C.Int32sl,
	"positionalAberration_03" / C.Int32sl,
	"positionalAberration_04" / C.Int32sl,
	"positionalAberration_05" / C.Int32sl,
	"displacement" / C.XYZ(0),
	"displacementToggle" / C.Int32sl,
	"unkn09_01" / C.Float32l,
	"unkn09_02" / C.Float32l,
	"unkn09_03" / C.Float32l,
	"unkn09_04" / C.Float32l,
	"unkn09_05" / C.Float32l,
	"unkn10_00" / C.Int32sl,
	"unkn10_01" / C.Float32l,
	"unkn10_02" / C.Float32l,
	"unkn11" / C.Int32sl,
	"unkn12_00" / C.Int32sl,
	"unkn12_01" / C.Float32l,
	"unkn12_02" / C.Float32l,
	"unkn12_03" / C.Float32l,
	"unkn13" / C.Int32sl,
	"path_len" / C.Int32sl,
	"p" / C.Byte[C.this.path_len],
)
SpawnByAngle=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Int32sl,
	"unkn2" / C.Float32l[1],
	"unkn3" / C.Int32sl,
	"unkn4" / C.Int16sl,
)
CheckPureAttribute=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Int32sl,
	"unkn2" / C.Int32sl[7],
)
TonemapFilter=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Int32sl,
	"unkn2" / C.Float32l[3],
	"path_len" / C.Int32sl,
	"p" / C.Byte[C.this.path_len],
)
ColorCorrectFilter=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[4],
	"unkn1" / C.Float32l[168],
)
SpawnByOcclusion=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Int32sl,
	"unkn2" / C.Float32l,
	"unkn3" / C.Int32sl,
)
FadeByOcclusion=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Int32sl,
	"unkn2" / C.Float32l[3],
)
ParentSnow=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Int32sl,
	"unkn2" / C.Int32sl,
	"color" / C.XYZ(2),
	"unkn3" / C.Int32sl[2],
	"unkn4" / C.Float32l[13],
)
OtomoSnow=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Int32sl,
	"unkn2" / C.Int32sl[2],
	"color" / C.XYZ(2),
	"unkn3" / C.Int32sl,
	"unkn4" / C.Int32sl,
	"unkn5" / C.Float32l[4],
	"unkn6" / C.Int32sl,
	"unkn7" / C.Float32l[8],
)
ParentMaterial=C.Struct(
	"type" / C.Int32sl,
	"unkn0" / C.Int32sl[2],
	"unkn1" / C.Float32l,
)
PlayEFX=C.Struct(
	"unkn0" / C.Int32sl,
	"path_len" / C.Int32sl,
	"type" / C.Int32sl,
	"unkn" / C.Int32sl[7],
	"xyz" / C.XYZ(3),
	"NULL" / C.Int32sl[3],
	"p" / C.Byte[C.this.path_len],
)
PlayEmitter=C.Struct(
	"unkn" / C.Int32sl[7],
	"xyz" / C.XYZ(3),
	"NULL" / C.Int32sl[3],
	"target_count" / C.Int32sl,
	"targets" / C.Int32sl[C.this.target_count],
)
ExternTransform3D=C.Struct(
	"unkn" / C.Int32sl[57],
)
ExternVelocity3D=C.Struct(
	"unkn" / C.Int32sl[27],
)
ExternScaleAnim=C.Struct(
	"unkn" / C.Int32sl[19],
)
ExternRgbFire=C.Struct(
	"unkn" / C.Int32sl[28],
)
ExternSpawn=C.Struct(
	"unkn" / C.Int32sl[18],
)
ExternMesh=C.Struct(
	"unkn" / C.Int32sl[44],
	"unkn1" / C.Int8sl,
)
ExternBillboard3D=C.Struct(
	"unkn" / C.Int32sl[33],
	"unkn1" / C.Int8sl,
)
ExternEmitterShape3D=C.Struct(
	"unkn" / C.Int32sl[22],
)
ExternUVSequence=C.Struct(
	"unkn" / C.Int32sl[11],
	"unkn1" / C.Int8sl,
)
ExternPlEmissive=C.Struct(
	"unkn" / C.Int32sl[19],
)
ExternVelocity3D0=C.Struct(
	"unkn" / C.Int32sl[12],
)
ExternVelocity3D1=C.Struct(
	"unkn" / C.Int32sl[90],
	"unkn1" / C.Int8sl,
)
ExternVelocity3D2=C.Struct(
	"unkn" / C.Int32sl[21],
)
ExternRgbWater=C.Struct(
	"unkn" / C.Int32sl[40],
	"unkn1" / C.Int8sl,
)
ExternVelocity3D5=C.Struct(
	"unkn" / C.Int32sl[18],
)
ExternVelocity3D6=C.Struct(
	"unkn" / C.Int32sl[20],
)
ExternVelocity3D7=C.Struct(
	"unkn" / C.Int32sl[39],
	"unkn1" / C.Int8sl,
)
EffectAttrColorTbl=C.Struct(
)
MhEffectDecalBehavior=C.Struct(
)
MhEffectDecalBehavior_getTotalFireLifeFrame=C.Struct(
)
MhEffectDecalBehavior_getTotalSmokeLifeFrame=C.Struct(
)
MhEffectDecalBehavior_getTotalSpecularLifeFrame=C.Struct(
)
MhEffectDecalBehavior_getTotalSheetLifeFrame=C.Struct(
)
MhEffectDecalBehavior_getTotalGtoBLifeFrame=C.Struct(
)
cCoordParameter=C.Struct(
)
IEffectItem=C.Struct(
)
Item=C.Struct(
)
DynamicRay=C.Struct(
)
FlowmapSettings=C.Struct(
)
EffectExecutor=C.Struct(
)
ExternFadeByAngle=C.Struct(
)
ExternFadeByDepth=C.Struct(
)
ExternStrainRibbon=C.Struct(
)
ExternUVControl=C.Struct(
)
ExternTurbulence=C.Struct(
)
ExternItem=C.Struct(
)
BasicExternItem=C.Struct(
)
EffectEvent=C.Struct(
)
EventBehaviorProperty=C.Struct(
)
DecalBehavior=C.Struct(
)
Variant=C.Struct(
)
LightBehavior=C.Struct(
)
PointLightBehavior=C.Struct(
)
SpotLightBehavior=C.Struct(
)
uEffectRadialBlurFilter=C.Struct(
)
FilterBehavior=C.Struct(
)
RadialBlurFilterBehavior=C.Struct(
)
EffectData=C.Struct(
)
EmitterExecutor=C.Struct(
)
TypeMie3D=C.Struct(
)
GroupItem=C.Struct(
)
GpuPhysics=C.Struct(
)
EmitterShape3DOverrider=C.Struct(
)
MemoItem=C.Struct(
)
IItemPropertyInfo=C.Struct(
)
EffectDatabase_ItemPropertyInfo=C.Struct(
)
EffectDatabase=C.Struct(
)
TimelineResource=C.Struct(
)
TimelineListResource=C.Struct(
)
INode=C.Struct(
)
Node=C.Struct(
)
Root=C.Struct(
)
Group=C.Struct(
)
Emitter=C.Struct(
)
Action=C.Struct(
)
Field=C.Struct(
)
Node_getType=C.Struct(
)
VelocityBase=C.Struct(
)
TypeBillboardBase=C.Struct(
)
EffectGroupData=C.Struct(
)
EffectGroup=C.Struct(
)
BoundaryBase=C.Struct(
)
RenderTarget_Target=C.Struct(
)
MaterialPath=C.Struct(
)
TypeLightning_Branch=C.Struct(
)
TypeRibbonBladeSection=C.Struct(
)
TubeLightSection=C.Struct(
)
EffectSettingPreset=C.Struct(
)
EffectTimeRedeemPreset=C.Struct(
)
Material_MaterialParam=C.Struct(
)
Material_MaterialNodeData=C.Struct(
)
ShapeMeshHolder=C.Struct(
)
cEffectProviderCustomData_ActionElement=C.Struct(
)
cEffectProviderCustomData_UnitElement=C.Struct(
)
cEffectProviderCustomData=C.Struct(
)
PlEmissiveManager=C.Struct(
)
ExternGuide=C.Struct(
)
ExternParentSnow=C.Struct(
)
ExternOtomoSnow=C.Struct(
)
Guide_MoveType_AlwaysThrough=C.Struct(
)
Guide_MoveType_SkipNear=C.Struct(
)
Guide_MoveType_OldType=C.Struct(
)
typeHash = {
	1965813039:PlayEFX,
	1152332069:PlayEmitter,
	351869514:ExternReference,
	1257264016:FakePlane,
	201720946:Dummy,
	674258598:RandomFix,
	428328940:Transform2D,
	1524169119:Billboard2D,
	1354601878:Blink,
	71967929:LuminanceBleed,
	584030352:EmitterShape2D,
	341394325:Velocity2D,
	957228464:Refraction,
	1616705008:MasterOnly,
	252064274:TubeLight,
	1240420851:Shovel,
	212167510:FakeDoF,
	842043995:RepeatArea,
	812022019:LinkPartsVisible,
	2115227124:PtTrigger,
	1217635032:PathChain,
	1535857470:Homing,
	1111321825:EmitterShapeMesh,
	1916268445:SpawnByAngle,
	283684959:CheckPureAttribute,
	845585410:TonemapFilter,
	1293936879:ColorCorrectFilter,
	10286765:Transform3D,
	368199626:ParentOptions,
	1921765292:Spawn,
	1320868484:Life,
	1003792849:EmitterShape3D,
	222458580:Velocity3D,
	859243212:FadeByDepth,
	319363982:RibbonBlade,
	1136904414:Billboard3D,
	480396424:ScaleAnim,
	1698970185:UVSequence,
	61219887:AlphaCorrection,
	1978267738:ShaderSettings,
	459578090:RgbFire,
	276670093:Mesh,
	1774142981:RotateAnim,
	597394907:PlEmissive,
	1123011591:Guide,
	1558046267:Lightning,
	14579343:ParentEmissive,
	280719621:PtCollision,
	1267346617:PlSnow,
	1179069619:PtBehavior,
	1659025771:Material,
	37870541:Plane,
	1660327299:RgbWater,
	937428146:Turbulence,
	2116359897:FadeByEmitterAngle,
	733291506:Ribbon,
	523015778:Noise,
	2020068998:UVControl,
	1226136492:FadeByAngle,
	873436648:EmitterBoundary,
	493311524:PtLife,
	1062052310:StrainRibbon,
	697457224:ScreenSpaceCollision,
	275476317:RayCast,
	1690896576:EffectAttrColorTbl,
	1128324015:MhEffectDecalBehavior,
	1250245974:MhEffectDecalBehavior_getTotalFireLifeFrame,
	409149100:MhEffectDecalBehavior_getTotalSmokeLifeFrame,
	173467491:MhEffectDecalBehavior_getTotalSpecularLifeFrame,
	1969325070:MhEffectDecalBehavior_getTotalSheetLifeFrame,
	1296538020:MhEffectDecalBehavior_getTotalGtoBLifeFrame,
	1892103853:cCoordParameter,
	19434345:IEffectItem,
	1215086948:Item,
	1708014292:DynamicRay,
	1184613359:FlowmapSettings,
	1213896611:EffectExecutor,
	1415485201:ExternFadeByAngle,
	779931249:ExternFadeByDepth,
	167781675:ExternStrainRibbon,
	1243935109:ExternUVControl,
	777721399:ExternTurbulence,
	1226458230:ExternItem,
	1771113640:BasicExternItem,
	1923506186:EffectEvent,
	346395602:EventBehaviorProperty,
	657374606:DecalBehavior,
	588732697:Variant,
	603167555:LightBehavior,
	110612213:PointLightBehavior,
	804054309:SpotLightBehavior,
	1183727815:uEffectRadialBlurFilter,
	618247822:FilterBehavior,
	1161774816:RadialBlurFilterBehavior,
	1135895459:EffectData,
	2097355886:EmitterExecutor,
	1771758423:TypeMie3D,
	2043222009:GroupItem,
	393634900:GpuPhysics,
	1105989980:EmitterShape3DOverrider,
	1484483739:MemoItem,
	716000960:IItemPropertyInfo,
	997811050:EffectDatabase_ItemPropertyInfo,
	1987779161:EffectDatabase,
	610766284:TimelineResource,
	1650401859:TimelineListResource,
	881621517:INode,
	1376259135:Node,
	1099111713:Root,
	256197774:Group,
	668609413:Emitter,
	1956806151:Action,
	963659027:Field,
	1929273712:Node_getType,
	261120345:VelocityBase,
	1590369728:TypeBillboardBase,
	1608814288:EffectGroupData,
	617098856:EffectGroup,
	1100150108:BoundaryBase,
	1478767196:RenderTarget_Target,
	2120416030:TypeLightning_Branch,
	19293690:TypeRibbonBladeSection,
	292704954:TubeLightSection,
	712996915:EffectSettingPreset,
	916096233:EffectTimeRedeemPreset,
	312479394:Material_MaterialParam,
	1851897063:Material_MaterialNodeData,
	738773001:ShapeMeshHolder,
	510816299:cEffectProviderCustomData_ActionElement,
	1178760989:cEffectProviderCustomData_UnitElement,
	1867843721:cEffectProviderCustomData,
	910471525:PlEmissiveManager,
	766474541:ExternGuide,
	74649634:ExternParentSnow,
	1181241355:ExternOtomoSnow,
	1168412664:Guide_MoveType_AlwaysThrough,
	889775412:Guide_MoveType_SkipNear,
	594406925:Guide_MoveType_OldType,
	1913890808:SpawnByOcclusion,
	64111316:FadeByOcclusion,
	215153612:ParentSnow,
	180261702:OtomoSnow,
	638869640:ParentMaterial,
	500644368:ExternTransform3D,
	1850314036:ExternMesh,
	725249589:ExternPlEmissive,
	482524730:ExternRgbWater,
	351887441:ExternVelocity3D,
	1880343637:ExternEmitterShape3D,
	705591903:ExternVelocity3D5,
	28559457:ExternSpawn,
	2069124466:ExternRgbFire,
	839790967:ExternVelocity3D1,
	1879331968:ExternVelocity3D6,
	693979274:ExternBillboard3D,
	786529163:ExternScaleAnim,
	1338793878:ExternVelocity3D0,
	2097096908:ExternUVSequence,
	805496014:ExternVelocity3D7,
	283026906:ExternVelocity3D2,
}