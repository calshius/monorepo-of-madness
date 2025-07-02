### Project Summary

This application is an **automated data pipeline for extracting, cleaning, and geolocating UFO sighting reports from UK government PDFs**. It works as follows:

1. **Fetches** all UFO report PDFs from a UK government website.
2. **Extracts** sighting data from each PDF using an LLM (or a fallback non-LLM method), ensuring only UK sightings are included.
3. **Converts** each PDF’s data into a structured CSV file.
4. **Geolocates** each sighting using best-effort matching of town and area to latitude/longitude, again using an LLM or a deterministic method.
5. **Aggregates** all cleaned and geolocated data into a single JSON file for easy use in mapping or analytics.
6. **Cleans up** all temporary files to keep your environment tidy.

The pipeline is robust, parallelized, and designed to recover gracefully from errors or model overloads. It’s ideal for researchers, data journalists, or hobbyists interested in mapping and analyzing UFO sightings across the UK.