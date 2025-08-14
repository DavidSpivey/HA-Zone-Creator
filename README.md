# HA-Zone-Creator
(readme unfinished)

This is a companion app for 60GHz eMotion mmWave sensors such as eMotion Max and eMotion Ultra which are connected to Home Assistant through MQTT. This app will allow one to create customized zones for these sensors of almost any shape and export to Home Assistant.

I noticed the grid offered in the LinkNLink app was quite low resolution (large squares), so I decided to make a companion app that would allow me to resolve some issues.

This is the result of those efforts.

This app features:
* Significantly higher resolution: 100x100 grid across 8 meters square
* Motion trails to "trace" a zone by moving to the area in question
* Polygon selection tool in additive or subtractive mode, to create a zone of almost any shape
* Diagonal rectangular selection for placing the sensor in a corner
* Export and Import to/from the clipboard or a txt file for easy import into Home Assistant
