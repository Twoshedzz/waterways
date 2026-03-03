# River Status Dashboard

## Overview

The River Status Dashboard is a simple, easy-to-use web application designed to help river users—like boaters, paddleboarders, and fishermen—quickly understand the current conditions of their local waterways.

It acts like a "traffic light" system for rivers, tracking the water levels and flow rates at various points along the river. By condensing complex environmental data into straightforward Green (Good), Amber (Warning), and Red (Danger) statuses, it allows anyone to instantly see if a stretch of river is safe or experiencing adverse conditions.

## The Original Problem

Before the River Status Dashboard, accessing river condition data was often a highly technical and frustrating process for the average person. River users historically had to manually search through difficult government databases, parse complex raw measurements, and try to individually compare various data points to understand the safety of the river they intended to use.

There was no unified, at-a-glance dashboard that stripped away the scientific complexity and just presented the simple question: *Is this stretch of river safe right now?*

We built this app to provide that centralized, easy-to-read, near real-time traffic-light map and bulletin board.

## How It Works

The app runs continuously in the background, acting as an automated data fetcher and processor.

Here is what it does:

1. Every 15 minutes, it reaches out to the internet to ask for the latest water measurements.
2. It looks at our configuration list of specific monitoring stations along the river (currently focusing heavily on 21 stations across the River Thames).
3. It takes these raw water level and flow measurements and compares them against predefined safe thresholds.
4. It paints the results onto a highly interactive map, coloring the actual geographical path of the river Red, Amber, or Green so users can physically see the status of the water route.
5. Every hour, it generates a text summary bulletin reporting anything that has changed for the worse since the last update.

## APIs Used

The Dashboard relies on two external Application Programming Interfaces (APIs) to provide its data and visualizations:

1. **The UK Environment Agency (EA) Flood-Monitoring API**
   - *What it is:* A live, publicly-accessible UK government database providing real-time telemetry data from sensors placed in rivers across the country.
   - *How we use it:* This is the core "brain" of our operation. Our app queries this API every 15 minutes to ask for the latest water level and water flow readings for the specific river stations we have configured. This is where we get the raw numbers that drive our Green/Amber/Red logic.

2. **OpenStreetMap (OSM) via the Overpass API**
   - *What it is:* OpenStreetMap is a free, editable geographic database of the world, built by a community of mappers. The Overpass API is a service that allows us to query and download very specific geographic shapes and points from that database.
   - *How we use it:* We used this API to download the actual structural geometry of the River Thames (how it twists, turns, and flows physically) into our application. We also use Leaflet.js (a mapping library) relying on OpenStreetMap's visual map "tiles" to display the background map you see when looking at the dashboard.

## Progress Summary

We have recently made several updates to improve the application:

- **Map Locks**: We integrated river lock locations onto the map view, which can be toggled on or off to help boaters navigate their routes.
- **Background Startup**: Optimized the server startup by moving the initial data fetch to a background task. This allows the API to serve requests instantly upon boot, resolving deployment timeouts.
- **Multiple Rivers**: Upgraded the app's configuration to dynamically support multiple UK navigable rivers natively. *Note: One of the supported rivers is currently missing its geographical shape data trace.*

## Future Features

Looking ahead, we are considering several functional and visual enhancements:

- **Water Quality APIs**: Consider incorporating additional APIs to monitor and display environmental water quality or pollution metrics.
- **Trend Indicators**: Improve the current trend arrows (Rising / Falling / Steady) to be more informative, less vague, and possibly reflect the rate of change.
- **Mobile Experience**: Revisit the overall UI layout and behaviors to provide a more robust and optimized experience for mobile phone users.
- **Card Design**: Re-evaluate the data card design hierarchy to improve user experience, data density, and aesthetic appeal.
- **RAG Status Explainers**: Add educational content that clearly explains what the underlying metrics mean and outlines the conditions represented by the Green, Amber, and Red safety statuses.
- **Proactive Alerts**: Explore integrating **GOV.UK Notify** to automatically push notifications (email/SMS) to users when a tracked river station reaches the Red (Danger) threshold.
