"""
FIREGUARD AI - NASA FIRMS API Service & Data Ingestion
Fetches live satellite thermal anomalies from NASA FIRMS API (MODIS / VIIRS)
or generates high-fidelity tactical mock feeds during DEMO MODE.
"""
import csv
import io
import logging
from datetime import datetime, timedelta
import random
import requests
from app.config import Config

logger = logging.getLogger(__name__)

class FIRMSService:
    @staticmethod
    def is_live_configured() -> bool:
        """Check if NASA FIRMS MAP_KEY is provided and demo mode is disabled."""
        return bool(Config.FIRMS_MAP_KEY and not Config.DEMO_MODE)

    @classmethod
    def fetch_hotspots(cls, country: str = "IND", day_range: int = 1, source: str = None) -> list:
        """
        Fetch hotspots from NASA FIRMS API if configured; otherwise generate high-fidelity tactical demo data.
        """
        source = source or Config.FIRMS_DEFAULT_SOURCE

        if cls.is_live_configured():
            try:
                return cls._fetch_from_nasa_api(country, day_range, source)
            except Exception as e:
                logger.error(f"NASA FIRMS API request failed: {e}. Falling back to demo feed.")

        return cls._get_demo_hotspots()

    @classmethod
    def _fetch_from_nasa_api(cls, country: str, day_range: int, source: str) -> list:
        """
        Query official NASA FIRMS country CSV API:
        https://firms.modaps.eosdis.nasa.gov/api/country/csv/[MAP_KEY]/[SOURCE]/[COUNTRY]/[DAY_RANGE]
        """
        url = f"{Config.FIRMS_API_BASE}/country/csv/{Config.FIRMS_MAP_KEY}/{source}/{country}/{day_range}"
        response = requests.get(url, timeout=12)
        response.raise_for_status()

        reader = csv.DictReader(io.StringIO(response.text))
        hotspots = []
        for row in reader:
            try:
                lat = float(row.get("latitude", 0))
                lon = float(row.get("longitude", 0))
                bright = float(row.get("bright_ti4", row.get("brightness", 320.0)))
                frp = float(row.get("frp", 15.0))
                conf_val = row.get("confidence", "nominal")

                # Normalize confidence to 0-100
                if str(conf_val).lower() == "l" or str(conf_val).lower() == "low":
                    confidence = 35
                elif str(conf_val).lower() == "n" or str(conf_val).lower() == "nominal":
                    confidence = 70
                elif str(conf_val).lower() == "h" or str(conf_val).lower() == "high":
                    confidence = 92
                else:
                    try:
                        confidence = int(conf_val)
                    except ValueError:
                        confidence = 65

                hotspots.append({
                    "source_satellite": source,
                    "latitude": lat,
                    "longitude": lon,
                    "brightness_k": bright,
                    "frp_mw": frp,
                    "confidence": confidence,
                    "acquisition_date": row.get("acq_date", datetime.utcnow().strftime("%Y-%m-%d")),
                    "acquisition_time": row.get("acq_time", "1200"),
                    "daynight": row.get("daynight", "D"),
                    "is_live_nasa": True
                })
            except Exception as ex:
                continue

        return hotspots

    @classmethod
    def _get_demo_hotspots(cls) -> list:
        """
        High-fidelity realistic thermal hotspots located around major industrial clusters in India.
        Includes industrial fires, routine flare stacks, persistent blast furnaces, and false positives.
        """
        now = datetime.utcnow()
        today_str = now.strftime("%Y-%m-%d")
        
        # Coordinated hotspots mapped directly to key petrochemical/industrial facilities
        base_points = [
            # Jamnagar Reliance / Nayara Complex (Gujarat)
            {
                "latitude": 22.3854, "longitude": 69.8712, "brightness_k": 388.4, "frp_mw": 84.5,
                "confidence": 94, "source": "VIIRS_SNPP", "daynight": "N",
                "label": "Jamnagar FCCU Unit-4 Uncontrolled Thermal Anomaly", "type": "INDUSTRIAL_FIRE"
            },
            {
                "latitude": 22.3921, "longitude": 69.8650, "brightness_k": 348.2, "frp_mw": 26.8,
                "confidence": 88, "source": "VIIRS_NOAA20", "daynight": "N",
                "label": "Jamnagar Flare Stack Elevated Gas Flaring", "type": "GAS_FLARE"
            },
            {
                "latitude": 22.3420, "longitude": 69.8210, "brightness_k": 331.0, "frp_mw": 14.2,
                "confidence": 75, "source": "MODIS_Aqua", "daynight": "D",
                "label": "Jamnagar Peripheral Agricultural Burning", "type": "AGRI_FIRE"
            },

            # Dahej PCPIR Petrochemical Hub (Gujarat)
            {
                "latitude": 21.7124, "longitude": 72.5488, "brightness_k": 395.1, "frp_mw": 96.2,
                "confidence": 96, "source": "VIIRS_SNPP", "daynight": "D",
                "label": "Dahej Petrochemical Polymer Storage Unit Blaze", "type": "INDUSTRIAL_FIRE"
            },
            {
                "latitude": 21.7018, "longitude": 72.5312, "brightness_k": 352.0, "frp_mw": 32.4,
                "confidence": 89, "source": "VIIRS_NOAA21", "daynight": "N",
                "label": "Dahej Cracker Routine Flaring Source", "type": "PERSIST_IND"
            },
            {
                "latitude": 21.6840, "longitude": 72.5890, "brightness_k": 312.4, "frp_mw": 6.8,
                "confidence": 38, "source": "MODIS_Terra", "daynight": "D",
                "label": "Dahej Coastal Mudflats Solar Glint Reflection", "type": "FALSE_POS"
            },

            # Visakhapatnam Industrial & Port Belt (Andhra Pradesh)
            {
                "latitude": 17.6892, "longitude": 83.2514, "brightness_k": 382.6, "frp_mw": 72.0,
                "confidence": 91, "source": "VIIRS_SNPP", "daynight": "N",
                "label": "Vizag HPCL Refinery Tank Farm Heavy Thermal Signature", "type": "INDUSTRIAL_FIRE"
            },
            {
                "latitude": 17.6250, "longitude": 83.1840, "brightness_k": 361.5, "frp_mw": 48.0,
                "confidence": 85, "source": "VIIRS_NOAA20", "daynight": "D",
                "label": "RINL Vizag Steel Continuous Blast Furnace Tapping", "type": "PERSIST_IND"
            },
            {
                "latitude": 17.7510, "longitude": 83.3100, "brightness_k": 324.0, "frp_mw": 9.5,
                "confidence": 62, "source": "MODIS_Aqua", "daynight": "D",
                "label": "Vizag Urban Municipal Solid Waste Smolder", "type": "WASTE_BURN"
            },

            # Chembur / Trombay Petrochemical Corridor (Mumbai)
            {
                "latitude": 19.0145, "longitude": 72.9023, "brightness_k": 376.8, "frp_mw": 64.3,
                "confidence": 89, "source": "VIIRS_SNPP", "daynight": "N",
                "label": "Chembur BPCL Hydrocracker Thermal Anomaly", "type": "INDUSTRIAL_FIRE"
            },
            {
                "latitude": 19.0080, "longitude": 72.8940, "brightness_k": 344.2, "frp_mw": 22.1,
                "confidence": 82, "source": "VIIRS_NOAA21", "daynight": "D",
                "label": "RCF Trombay Fertilizer Ammonia Flare", "type": "GAS_FLARE"
            },

            # Manali Petrochemical Complex (Chennai)
            {
                "latitude": 13.1672, "longitude": 80.2641, "brightness_k": 371.4, "frp_mw": 58.7,
                "confidence": 87, "source": "VIIRS_SNPP", "daynight": "N",
                "label": "CPCL Manali Desulfurization Thermal Anomaly", "type": "INDUSTRIAL_FIRE"
            },
            {
                "latitude": 13.1890, "longitude": 80.2450, "brightness_k": 339.0, "frp_mw": 18.5,
                "confidence": 78, "source": "MODIS_Terra", "daynight": "D",
                "label": "Manali Industrial Estate Routine Heat Sink", "type": "PERSIST_IND"
            },

            # Non-Industrial Forest / Stubble baselines for comparison
            {
                "latitude": 21.8450, "longitude": 73.2100, "brightness_k": 341.2, "frp_mw": 29.5,
                "confidence": 82, "source": "MODIS_Aqua", "daynight": "D",
                "label": "Narmada River Foothill Forest Fire", "type": "FOREST_FIRE"
            }
        ]

        result = []
        for i, pt in enumerate(base_points):
            # Introduce small natural jitter
            jitter_lat = pt["latitude"] + random.uniform(-0.002, 0.002)
            jitter_lon = pt["longitude"] + random.uniform(-0.002, 0.002)
            time_offset = random.randint(10, 180)
            det_time = (now - timedelta(minutes=time_offset)).strftime("%H%M")

            result.append({
                "source_satellite": pt["source"],
                "latitude": round(jitter_lat, 5),
                "longitude": round(jitter_lon, 5),
                "brightness_k": pt["brightness_k"],
                "frp_mw": pt["frp_mw"],
                "confidence": pt["confidence"],
                "acquisition_date": today_str,
                "acquisition_time": det_time,
                "daynight": pt["daynight"],
                "is_live_nasa": False,
                "preset_type": pt.get("type", "UNKNOWN"),
                "preset_label": pt.get("label", "")
            })

        return result
