# HA-Zone-Creator (this readme is not finished)

This is a companion app for 60GHz eMotion mmWave sensors such as eMotion Max and eMotion Ultra connected to Home Assistant through MQTT. This app will allow one to create customized zones for these sensors of almost any shape and export to Home Assistant.

I noticed the grid offered in the LinkNLink app was quite low resolution (large squares), so I decided to make a companion app that would allow me to resolve some issues.

This is the result of those efforts.

This app features:
* Significantly higher resolution: 100x100 grid across 8 meters square
* Motion trails to "trace" a zone by moving to the area in question
* Polygon selection tool in additive or subtractive mode, to create a zone of almost any shape
* Diagonal rectangular selection for placing the sensor in a corner
* Export and Import to/from the clipboard or a txt file for easy import into Home Assistant

# Usage:
Open the app and Home Assistant.
Enter your MQTT ip address in Broker, username and password (if your MQTT instance is password protected)
Find your device ID in HA:
  Go to Settings > Devices & services > MQTT
  Click on your eMotion device
  Click on the first sensor
  Click the gear
  Copy the portion of the Entity ID that is just the unique sensor number. For example, if your Entity ID is "sensor.lnlinkha_e04b410156c8000000000000d6ac0000_2", you only want to copy "e04b410156c8000000000000d6ac0000"
Paste the Device ID into the app and click Connect.

If everything is connected successfully, you will begin to see
  A blue dot where there is motion
  A red trail where motion has been

Move into the area where you want to create a zone, and move around in all the places the zone should be created.
Consider yourself to be "outlining" the zone with your body.
Come back to the app and uncheck Movement trail to start defining the zone without altering your outline

You can click individial squares to create a zone

You can click and drag to create rectangular areas

You can click select diagonally to create diagonal rectangular areas if your sensor is at a 45-degree angle to the room

You can use the Polygon selection tool by clicking once, moving to a new spot, and clicking again to create the first line
Then, after you have outlined the zone you wish to create, double click to complete the outline and highight your zone in orange.

If you make a mistake and wish to remove squares from your zone, click "+ Adding to selection" and it will change to "- Removing from selection"
Then use any of the tools to remove squares from the highlighted area.

Once you are finished creating the zone, it's time to export it to Home Assistant.
For simplicity, click "Copy Template".
Go to Home Assistant > Settings > Devices & services > Helpers > + Create Helper > Template > Template a binary sensor.
Paste the copied jinja template in "State"
Name your zone at the top
For Device Class, select motion
Click submit

Congratulations! You have made a custom zone for your eMotion sensor in Home Assistant. Now you can start making automations based on your new zone.
