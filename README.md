# homeassistant-whirlpool-oven

Home Assistant custom component for interfacing with Whirlpool/Maytag/KitchenAid ovens.

Home Assistant already supports air conditioners, washing machines, and dryers from these manufacturers through the `whirlpool` integration.
This custom integration only provides additional support for ovens (ranges, stoves) from the same manufacturers.

I've created this as a custom integration because updating the built-in `whirlpool` integration would have been messy. The current code does not easily extend to accomodate mutiple appliance types, or multiple entity types for those appliances. One of the goals of this integration is provide an extensible foundation for all Whirlpool appliances. It will start with ovens, but in time, the other appliance types could be re-integrated as well.

# Installation via HACS

This custom component can be integrated into [HACS](https://github.com/hacs/integration), so you can track future updates. If you have do not have have HACS installed, please see [their installation guide](https://hacs.xyz/docs/installation/manual).

1. Select HACS from the left-hand navigation menu.

2. Click _Integrations_.

3. Click the three dots in the upper right-hand corner and select _Custom Repositories_.

4. Paste "https://github.com/MizterB/homeassistant-whirpool-oven" into _Repository_, select "Integration" as _Category_, and click Add.

5. Close the Custom repositories dialog after it updates with the new integration.

6. "Whirlpool Oven" will appear in your list of repositories. Click to open, click the following Download buttons.

# Configuration

Configuration is done via the UI. Add the "Whirlpool Oven" integration via the Integration settings, then provide the username, password, and region in the configuration dialog.

## Changelog

_Not Yet Released_

- Coming soon
