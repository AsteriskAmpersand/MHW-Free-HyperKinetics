![Project Logo](https://github.com/AsteriskAmpersand/MHW-Free-HyperKinetics/blob/main/icons/HKLogo.fw.png?raw=true)

Free Hyperkinetics is a Blender Plugin for use in animation editing for the game Monster Hunter World. 

# Introduction

Free Hyperkinetics is a Blender Extension for editing MHW's LMT, TIML and EFX files. Free Hyperkinetics consists of 3 interconected modules. The titular Free Hyperkinectics (FreeHK) which consists of an extension of Blender's skeleton, actions and fcurves to MHW LMT animations and tracks. Independent TIML Works (IndependentTW) which extends Blender's actions and keyframes to MHW TIML animations and tracks. And finally an extension to Blender's node system to unify the two and interact with MHW Animation metadata hierarchies.

FreeHK attempts to be a WYISWYG tool. Whenever the exporter has to fill in missing data it will attempt to do so in a way that it matches what's visible in blender. In cases where the metadata conflicts with what's presented it will defer to what's visible. There's tools for ensuring visual and metadata coincide and also to coerce visuals to fall in line with metadata, and it's possible to change exporter settings to modify part of this behaviour.

# Important
This requires Blender 2.79**c**. You most likely have 2.79**b**. 2.79c never hit stable and has some significant features related to how blender operates, you can get it from [here](https://download.blender.org/release/Blender2.79/latest/) 2.79c is retrocompatible so you can just outright replace your existing 2.79b install.

# Background and Credits

The entirety of Free Hyperkinetics was written by one person AsteriskAmpersand (me). It was a year long ordeal of wrestling Blender into doing something sane with the animation format of MHW. During this period I also had to research a lot of missing parts and pieces of the animation format and additionally provide actual editing and transfer support for animations. 

## Thanks
* **Stracker** and **PredatorCZ** for doing a SIGNIFICANT amount of the background format work including most of figuring the datatypes.
* **Silvris** for his work on TIMLs which forms the basis of the TIMLWorks (TW) engine. 
* **DMQW ICE** for his work on EFX which was part of the TIMLWorks (TW) engine dealing with EFX.
* **LyraVeil** for particular edge cases and issues with previous import only tools.

# A Simple Request
![TinyLogo](https://github.com/AsteriskAmpersand/MHW-Free-HyperKinetics/blob/main/icons/TinyLogo.fw.png)

If you use this tool and find it useful, please credit its use appropiately on mods and link to it so people interested can also give it a try. You can even use the small version of the FreeHK logo if you wish. 

Additionaly I'd ask that you avoid posting mods made with this tool on Nexusmods. Given this tool is released with an Open Source License, nothing really stops you, but I just request that you avoid using a site that has taken so many anti-modding attitudes as of late and done so much damage to many small modding communities in the process. 

Furthermore, please do not use this to produce in-game pornography. There's already thousands of tools and platforms for that sort of thing, and the last thing I want is to have my tool or my game of modding choice to further be associated and stereotyped with that sort of content. Again, I can't stop you, it's an open source license, but I am asking nicely.

# Contributing
You can contribute to this repository through a well documented or founded PR.
You can log issues or bugs through the issue tracker on this project page.

Alternatively you can DM me on Discord \*&#7932.

If you wish to contribute directly to me so I can keep making more modding tools for the MH Series I have a [patreon page](https://www.patreon.com/members?membershipType=active_patron).
