"""
Lazy Provider Registry for CutWire Drift AI.
Eliminates memory waste and high idle RAM at startup by deferring import and instantiation
of media providers until specifically queried on-demand.
"""
import importlib
from typing import Dict, List, Optional, Type, Any
from providers.base import BaseMediaProvider

# Mapping provider key -> (module_relative_path, class_name)
PROVIDER_CATALOG: Dict[str, tuple[str, str]] = {
    "pexels": ("providers.pexels", "PexelsProvider"),
    "pixabay": ("providers.pixabay", "PixabayProvider"),
    "wikimedia": ("providers.wikimedia", "WikimediaProvider"),
    "nasa": ("providers.nasa", "NasaProvider"),
    "unsplash": ("providers.unsplash", "UnsplashProvider"),
    "coverr": ("providers.coverr", "CoverrProvider"),
    "freesound": ("providers.freesound", "FreesoundProvider"),
    "archive_org": ("providers.archive_org", "ArchiveOrgProvider"),
    "openverse": ("providers.openverse", "OpenverseProvider"),
    "met_museum": ("providers.met_museum", "MetMuseumProvider"),
    "artic": ("providers.artic", "ArtInstituteChicagoProvider"),
    "smithsonian": ("providers.smithsonian", "SmithsonianProvider"),
    "loc": ("providers.loc", "LibraryOfCongressProvider"),
    "europeana": ("providers.europeana", "EuropeanaProvider"),
    "free_music_archive": ("providers.free_music_archive", "FreeMusicArchiveProvider"),
    "mixkit": ("providers.mixkit", "MixkitProvider"),
    "rijksmuseum": ("providers.rijksmuseum", "RijksmuseumProvider"),
    "cleveland_art": ("providers.cleveland_art", "ClevelandArtProvider"),
    "wellcome_collection": ("providers.wellcome_collection", "WellcomeCollectionProvider"),
    "biodiversity": ("providers.biodiversity", "BiodiversityProvider"),
    "usgs": ("providers.usgs", "UsgsProvider"),
    "noaa": ("providers.noaa", "NoaaProvider"),
    "jamendo": ("providers.jamendo", "JamendoMusicProvider"),
    "ccmixter": ("providers.ccmixter", "CcMixterProvider"),
    "incompetech": ("providers.incompetech", "IncompetechProvider"),
    "rawpixel": ("providers.rawpixel", "RawpixelProvider"),
    "mazwai": ("providers.mazwai", "MazwaiProvider"),
    "esa": ("providers.esa", "EsaProvider"),
    "dvids": ("providers.dvids", "DvidsProvider"),
    "cern": ("providers.cern", "CernProvider"),
    "videvo": ("providers.videvo", "VidevoProvider"),
    "nara": ("providers.nara", "NaraProvider"),
    "getty_open": ("providers.getty_open", "GettyOpenProvider"),
    "paris_musees": ("providers.paris_musees", "ParisMuseesProvider"),
    "dareful": ("providers.dareful", "DarefulProvider"),
    "nga": ("providers.nga", "NgaProvider"),
    "prelinger": ("providers.prelinger", "PrelingerProvider"),
    "british_library": ("providers.british_library", "BritishLibraryProvider"),
    "kaboompics": ("providers.kaboompics", "KaboompicsProvider"),
    "mauritshuis": ("providers.mauritshuis", "MauritshuisProvider"),
    "videezy": ("providers.videezy", "VideezyProvider"),
    "burst": ("providers.burst", "BurstProvider"),
    "nypl": ("providers.nypl", "NyplProvider"),
    "vam": ("providers.vam", "VamProvider"),
    "splitshire": ("providers.splitshire", "SplitShireProvider"),
    "picjumbo": ("providers.picjumbo", "PicjumboProvider"),
    "isorepublic": ("providers.isorepublic", "IsoRepublicProvider"),
    "gratisography": ("providers.gratisography", "GratisographyProvider"),
    "yale": ("providers.yale", "YaleProvider"),
    "reshot": ("providers.reshot", "ReshotProvider"),
    "lifeofpix": ("providers.lifeofpix", "LifeOfPixProvider"),
    "flickr_commons": ("providers.flickr_commons", "FlickrCommonsProvider"),
    "nps": ("providers.nps", "NpsProvider"),
    "foodiesfeed": ("providers.foodiesfeed", "FoodiesfeedProvider"),
    "walters_art": ("providers.walters_art", "WaltersArtProvider"),
    "cdc_phil": ("providers.cdc_phil", "CdcPhilProvider"),
    "old_book_illustrations": ("providers.old_book_illustrations", "OldBookIllustrationsProvider"),
    "morguefile": ("providers.morguefile", "MorguefileProvider"),
    "smk": ("providers.smk", "SmkProvider"),
    "dpla": ("providers.dpla", "DplaProvider"),
    "usfws": ("providers.usfws", "UsfwsProvider"),
    "skitterphoto": ("providers.skitterphoto", "SkitterphotoProvider"),
    "foca_stock": ("providers.foca_stock", "FocaStockProvider"),
    "stockvault": ("providers.stockvault", "StockvaultProvider"),
    "trove": ("providers.trove", "TroveProvider"),
    "artvee": ("providers.artvee", "ArtveeProvider"),
    "magdeleine": ("providers.magdeleine", "MagdeleineProvider"),
    "wp_photos": ("providers.wp_photos", "WpPhotosProvider"),
    "goodfreephotos": ("providers.goodfreephotos", "GoodFreePhotosProvider"),
    "jay_mantri": ("providers.jay_mantri", "JayMantriProvider"),
}

class LazyProviderRegistry:
    """
    On-demand provider factory and singleton cache.
    Zero memory overhead until a provider is explicitly requested.
    """
    _instances: Dict[str, BaseMediaProvider] = {}

    @classmethod
    def get_provider(cls, name: str) -> Optional[BaseMediaProvider]:
        key = name.lower()
        if key in cls._instances:
            return cls._instances[key]

        if key not in PROVIDER_CATALOG:
            return None

        mod_path, cls_name = PROVIDER_CATALOG[key]
        try:
            mod = importlib.import_module(mod_path)
            provider_cls = getattr(mod, cls_name)
            instance = provider_cls()
            cls._instances[key] = instance
            return instance
        except Exception as e:
            print(f"[LazyProviderRegistry] Failed to load provider {name}: {e}")
            return None

    @classmethod
    def get_all_active(cls) -> List[BaseMediaProvider]:
        """Returns only providers that have been loaded so far."""
        return list(cls._instances.values())

    @classmethod
    def get_or_load_all(cls) -> List[BaseMediaProvider]:
        """Loads all providers if needed (e.g. for exhaustive system search or audits)."""
        for key in PROVIDER_CATALOG:
            if key not in cls._instances:
                cls.get_provider(key)
        return list(cls._instances.values())

    @classmethod
    def unload_idle(cls):
        """Releases cached provider instances to free memory."""
        cls._instances.clear()

    @classmethod
    def available_providers(cls) -> List[str]:
        return list(PROVIDER_CATALOG.keys())

