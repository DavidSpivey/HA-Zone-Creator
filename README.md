# HA-Zone-Creator

This is a companion app for 60GHz eMotion mmWave sensors such as eMotion Max and eMotion Ultra connected to Home Assistant through MQTT. This app creates customized motion zones for these sensors of almost any shape to export to Home Assistant.

#### The following LinkNLink app issues are solved with this app:
- Low accuracy: The grid in the LinkNLink app is quite low resolution (large squares).
- Zones cannot overlap
- Maximum of 4 zones
- Poor 45-degree angle support (most of my sensors are in the corner of the room)

#### This app features:
* Significantly higher resolution: 100x100 grid across 8 meters square
* Motion trails to "trace" a zone by physically moving to the area in question
* Polygon selection tool in additive or subtractive mode, to create a zone of almost any shape
* Diagonal rectangular selection for corner sensor placement (45 degree angle)
* Export and Import to/from the clipboard or a txt file for easy import into Home Assistant
* Unlimited number of zones

## Requirements
- eMotion Max or Ultra sensors
- MQTT connected in LinkNLink app
- Home Assistant connected to MQTT
- Minimum firmware v61511 for eMotion Max sensors (IDK about Ultra)

## Usage:
- Open the app and Home Assistant.
- Enter your MQTT ip address in Broker
- If your MQTT instance is password protected, enter your username / password
- Find your device ID in HA:
	- Go to Settings > Devices & services > MQTT
	- Click on your eMotion device
	- Click on the first sensor
	- Click the gear
	- Copy the portion of the Entity ID that is just the unique sensor number. For example, if your Entity ID is "sensor.lnlinkha_e04b410156c8000000000000d6ac0000_2", you only want to copy "e04b410156c8000000000000d6ac0000"
- Paste the Device ID into the app
- Click Connect.

If everything is connected successfully, you will begin to see a blue dot where there is motion, and a red trail where motion has been

1. Move into the area where you want to create a zone, and move around in all the places the zone should be created.
2. Consider yourself to be "outlining" the zone with your body.
3. Come back to the app and uncheck Movement trail to start defining the zone without altering your outline

You can click individial squares to create a zone

You can click and drag to create rectangular areas

You can click select diagonally to create diagonal rectangular areas if your sensor is at a 45-degree angle to the room

You can use the Polygon selection tool by clicking once, moving to a new spot, and clicking again to create the first line<br>
Then, after you have outlined the zone you wish to create, double click to complete the outline and highight your zone in orange.

If you make a mistake and wish to remove squares from your zone, click "+ Adding to selection" and it will change to "- Removing from selection"<br>
Then use any of the tools to remove squares from the highlighted area.

Once you are finished creating the zone, it's time to export it to Home Assistant.
1. For simplicity, click "Copy Template".
2. Go to Home Assistant > Settings > Devices & services > Helpers > + Create Helper > Template > Template a binary sensor.
3. Paste the copied jinja template in "State"
4. Name your zone at the top
5. For Device Class, select motion
6. Click submit

Congratulations! You have made a custom zone for your eMotion sensor in Home Assistant. Now you can start making automations based on your new zone.

## Notes
### Multiple people
This app uses the "Target 1 X" and "Target 1 Y" values from the eMotion MQTT values. This means the zone only tracks the **first person** in the room. This can be modified in the output template for multiple persons.
For example:
```
{% set x = states('sensor.lnlinkha_e04b410156ad000000000000d6ac0000_7') | float(0) %}
{% set y = states('sensor.lnlinkha_e04b410156ad000000000000d6ac0000_8') | float(0) %}
```
In this example, _7 and _8 represent "Target 1 X" and "Target 1 Y". "Target 2 X" and "Target 2 Y" are _11 and _12. Click on the Target (whatever) X and Y in Home Assistant, then click the gear to get the Entity ID you wish to track.

### You can temporarily increase the speed of detection for the purpose of outlining a zone.
- Go to Settings > Devices & services > MQTT
- Click on your eMotion device
- Scroll down to configuration and drag Radar target update frequency (sec) to 0.5
- **DON'T FORGET** to reset this value to 2 (default) when finished, as leaving it at a half second can make your MQTT messages significantly verbose and might hinder performance.
	- (Ignore this if you have a high performance broker and desire near-instant zone updates)

### Editing a zone
You can edit an existing zone by copying it from the Binary Sensor State in Home Assistant, and clicking Load from Clipboard.<br>
When you've made necessary changes, Copy Template again and overwrite the one in Home Assistant.

### MQTT password is saved in plain text
For quick access, when MQTT settings are changed, they are immediately saved in settings.ini in the same folder as the app. The MQTT password is saved in plain text in this file, although it is hidden in the UI.
