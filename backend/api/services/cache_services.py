import time
from fastapi.responses import JSONResponse
import threading
import os
import sys
import pickle
import gzip
import shutil
from datetime import datetime, timedelta
from backend.api.schemas.models import CodeRequest, CodeResponse, BatchCodeRequest, IDERequest, IDEResponse, ContextAwareFixRequest
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global caches (to be shared across the app)
LLM_CACHE = {}
LLM_CACHE_EXPIRY = {}
ANALYSIS_CACHE = {}
FIX_CACHE = {}
HINT_CACHE = {}
OPTIMIZATION_CACHE = {}
CACHE_USAGE = {}
CACHE_HITS = {"analysis": 0, "fix": 0, "hint": 0, "optimize": 0, "general": 0}
CACHE_MISSES = {"analysis": 0, "fix": 0, "hint": 0, "optimize": 0, "general": 0}
CACHE_TTL = timedelta(hours=3)
CACHE_MAX_SIZE = 500

class CacheManager:
    def __init__(self):
        self.cache_lock = threading.Lock()
        self.dirty = False
        self.last_save_time = time.time()
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size": 0,
            "last_eviction_time": None,
            "last_save_time": None,
            "cache_efficiency": 0.0,
            "avg_lookup_time": 0.0,
            "total_lookups": 0,
            "lookup_time_sum": 0.0
        }
        self.cache_files = {
            "general": os.path.join("backend/api/checkpoint", "general_cache.gz"),
            "analysis": os.path.join("backend/api/checkpoint", "analysis_cache.gz"),
            "fix": os.path.join("backend/api/checkpoint", "fix_cache.gz"),
            "hint": os.path.join("backend/api/checkpoint", "hint_cache.gz"),
            "optimize": os.path.join("backend/api/checkpoint", "optimize_cache.gz"),
            "usage": os.path.join("backend/api/checkpoint", "cache_usage.gz"),
            "hits": os.path.join("backend/api/checkpoint", "cache_hits.gz"),
            "expiry": os.path.join("backend/api/checkpoint", "cache_expiry.gz"),
            "stats": os.path.join("backend/api/checkpoint", "cache_stats.gz")
        }
        self.backup_dir = os.path.join("backend/api/checkpoint", "backups")
        os.makedirs(self.backup_dir, exist_ok=True)
        self.init_auto_save()
    def init_auto_save(self):
        self.auto_save_thread = threading.Thread(target=self._auto_save_loop, daemon=True)
        self.auto_save_thread.start()
    def _auto_save_loop(self):
        while True:
            current_time = time.time()
            if self.dirty or (current_time - self.last_save_time > 1800):
                self.save_cache_to_disk()
                self.dirty = False
                self.last_save_time = current_time
                if not hasattr(self, 'last_backup_time') or (current_time - getattr(self, 'last_backup_time', 0) > 86400):
                    self._create_backup()
                    self.last_backup_time = current_time
            time.sleep(300)
    def _create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"cache_backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)
        try:
            for cache_type, file_path in self.cache_files.items():
                if os.path.exists(file_path):
                    shutil.copy2(file_path, os.path.join(backup_path, os.path.basename(file_path)))
            logger.info(f"Cache backup created at {backup_path}")
            backups = sorted([os.path.join(self.backup_dir, d) for d in os.listdir(self.backup_dir) if os.path.isdir(os.path.join(self.backup_dir, d))], key=os.path.getmtime)
            if len(backups) > 5:
                for old_backup in backups[:-5]:
                    shutil.rmtree(old_backup)
                    logger.info(f"Removed old cache backup: {old_backup}")
        except Exception as e:
            logger.error(f"Error creating cache backup: {str(e)}")
    def _update_stats(self, hit=False, eviction=False, lookup_time=None):
        if hit:
            self.cache_stats["hits"] += 1
        else:
            self.cache_stats["misses"] += 1
        if eviction:
            self.cache_stats["evictions"] += 1
            self.cache_stats["last_eviction_time"] = time.time()
        if lookup_time is not None:
            self.cache_stats["total_lookups"] += 1
            self.cache_stats["lookup_time_sum"] += lookup_time
            self.cache_stats["avg_lookup_time"] = self.cache_stats["lookup_time_sum"] / self.cache_stats["total_lookups"]
        total_lookups = self.cache_stats["hits"] + self.cache_stats["misses"]
        if total_lookups > 0:
            self.cache_stats["cache_efficiency"] = (self.cache_stats["hits"] / total_lookups) * 100
    def _cleanup_expired_entries(self):
        global LLM_CACHE, LLM_CACHE_EXPIRY
        current_time = datetime.now()
        expired_keys = []
        for key, expiry_time in LLM_CACHE_EXPIRY.items():
            if expiry_time < current_time:
                expired_keys.append(key)
        eviction_count = 0
        for key in expired_keys:
            if key in LLM_CACHE:
                del LLM_CACHE[key]
                eviction_count += 1
            if key in LLM_CACHE_EXPIRY:
                del LLM_CACHE_EXPIRY[key]
        if len(LLM_CACHE) > CACHE_MAX_SIZE:
            sorted_keys = sorted(
                CACHE_USAGE.items(),
                key=lambda x: x[1],
                reverse=False
            )
            keys_to_remove = sorted_keys[:len(LLM_CACHE) - CACHE_MAX_SIZE + 10]
            for key, _ in keys_to_remove:
                if key in LLM_CACHE:
                    del LLM_CACHE[key]
                    eviction_count += 1
                if key in LLM_CACHE_EXPIRY:
                    del LLM_CACHE_EXPIRY[key]
                if key in CACHE_USAGE:
                    del CACHE_USAGE[key]
        if eviction_count > 0:
            self._update_stats(eviction=True)
            self.cache_stats["evictions"] += eviction_count
            logger.info(f"Cleaned up {eviction_count} expired or least used cache entries")
            self.dirty = True
        return eviction_count
    def get_cache_stats(self):
        with self.cache_lock:
            self.cache_stats["size"] = (
                len(LLM_CACHE) + 
                len(ANALYSIS_CACHE) + 
                len(FIX_CACHE) + 
                len(HINT_CACHE) + 
                len(OPTIMIZATION_CACHE)
            )
            hit_ratios = {}
            for cache_type in CACHE_HITS.keys():
                total_lookups = CACHE_HITS[cache_type] + CACHE_MISSES[cache_type]
                hit_ratio = (CACHE_HITS[cache_type] / total_lookups * 100) if total_lookups > 0 else 0
                hit_ratios[cache_type] = round(hit_ratio, 2)
            cache_sizes = {
                "general": len(LLM_CACHE),
                "analysis": len(ANALYSIS_CACHE),
                "fix": len(FIX_CACHE),
                "hint": len(HINT_CACHE),
                "optimize": len(OPTIMIZATION_CACHE)
            }
            memory_usage = sum(sys.getsizeof(pickle.dumps(cache)) for cache in [
                LLM_CACHE, ANALYSIS_CACHE, FIX_CACHE, HINT_CACHE, OPTIMIZATION_CACHE
            ])
            current_time = time.time()
            last_save_time = datetime.fromtimestamp(self.last_save_time).strftime('%Y-%m-%d %H:%M:%S') if hasattr(self, 'last_save_time') else None
            last_eviction_time = None
            if self.cache_stats["last_eviction_time"]:
                last_eviction_time = datetime.fromtimestamp(self.cache_stats["last_eviction_time"]).strftime('%Y-%m-%d %H:%M:%S')
            return {
                "cache_summary": {
                    "total_entries": self.cache_stats["size"],
                    "hit_ratio": f"{self.cache_stats.get('cache_efficiency', 0):.1f}%",
                    "memory_usage": f"{memory_usage / (1024 * 1024):.2f} MB",
                    "last_save": last_save_time,
                    "last_eviction": last_eviction_time,
                    "uptime": f"{(current_time - self.cache_stats.get('start_time', current_time)) / 3600:.1f} hours"
                },
                "cache_hits": CACHE_HITS,
                "cache_misses": CACHE_MISSES,
                "hit_ratios": hit_ratios,
                "cache_sizes": cache_sizes,
                "detailed_stats": self.cache_stats
            }
    def load_cache_from_disk(self):
        global LLM_CACHE, LLM_CACHE_EXPIRY, ANALYSIS_CACHE, FIX_CACHE, HINT_CACHE
        global OPTIMIZATION_CACHE, CACHE_USAGE, CACHE_HITS, CACHE_MISSES
        with self.cache_lock:
            try:
                if os.path.exists(self.cache_files["general"]):
                    with gzip.open(self.cache_files["general"], 'rb') as f:
                        LLM_CACHE = pickle.load(f)
                        logger.info(f"Loaded {len(LLM_CACHE)} general cache entries")
                if os.path.exists(self.cache_files["expiry"]):
                    with gzip.open(self.cache_files["expiry"], 'rb') as f:
                        LLM_CACHE_EXPIRY = pickle.load(f)
                if os.path.exists(self.cache_files["analysis"]):
                    with gzip.open(self.cache_files["analysis"], 'rb') as f:
                        ANALYSIS_CACHE = pickle.load(f)
                        logger.info(f"Loaded {len(ANALYSIS_CACHE)} analysis cache entries")
                if os.path.exists(self.cache_files["fix"]):
                    with gzip.open(self.cache_files["fix"], 'rb') as f:
                        FIX_CACHE = pickle.load(f)
                        logger.info(f"Loaded {len(FIX_CACHE)} fix cache entries")
                if os.path.exists(self.cache_files["hint"]):
                    with gzip.open(self.cache_files["hint"], 'rb') as f:
                        HINT_CACHE = pickle.load(f)
                        logger.info(f"Loaded {len(HINT_CACHE)} hint cache entries")
                if os.path.exists(self.cache_files["optimize"]):
                    with gzip.open(self.cache_files["optimize"], 'rb') as f:
                        OPTIMIZATION_CACHE = pickle.load(f)
                        logger.info(f"Loaded {len(OPTIMIZATION_CACHE)} optimization cache entries")
                if os.path.exists(self.cache_files["usage"]):
                    with gzip.open(self.cache_files["usage"], 'rb') as f:
                        CACHE_USAGE = pickle.load(f)
                if os.path.exists(self.cache_files["hits"]):
                    with gzip.open(self.cache_files["hits"], 'rb') as f:
                        stats = pickle.load(f)
                        CACHE_HITS = stats["hits"]
                        CACHE_MISSES = stats["misses"]
                self._cleanup_expired_entries()
                logger.info("Successfully loaded cache from disk")
                return True
            except Exception as e:
                logger.error(f"Error loading cache from disk: {str(e)}")
                LLM_CACHE = {}
                LLM_CACHE_EXPIRY = {}
                ANALYSIS_CACHE = {}
                FIX_CACHE = {}
                HINT_CACHE = {}
                OPTIMIZATION_CACHE = {}
                CACHE_USAGE = {}
                return False
    def save_cache_to_disk(self):
        with self.cache_lock:
            try:
                self._cleanup_expired_entries()
                self.cache_stats["size"] = (
                    len(LLM_CACHE) + 
                    len(ANALYSIS_CACHE) + 
                    len(FIX_CACHE) + 
                    len(HINT_CACHE) + 
                    len(OPTIMIZATION_CACHE)
                )
                self.cache_stats["last_save_time"] = time.time()
                with gzip.open(self.cache_files["general"], 'wb') as f:
                    pickle.dump(LLM_CACHE, f)
                with gzip.open(self.cache_files["expiry"], 'wb') as f:
                    pickle.dump(LLM_CACHE_EXPIRY, f)
                with gzip.open(self.cache_files["analysis"], 'wb') as f:
                    pickle.dump(ANALYSIS_CACHE, f)
                with gzip.open(self.cache_files["fix"], 'wb') as f:
                    pickle.dump(FIX_CACHE, f)
                with gzip.open(self.cache_files["hint"], 'wb') as f:
                    pickle.dump(HINT_CACHE, f)
                with gzip.open(self.cache_files["optimize"], 'wb') as f:
                    pickle.dump(OPTIMIZATION_CACHE, f)
                with gzip.open(self.cache_files["usage"], 'wb') as f:
                    pickle.dump(CACHE_USAGE, f)
                with gzip.open(self.cache_files["hits"], 'wb') as f:
                    pickle.dump({"hits": CACHE_HITS, "misses": CACHE_MISSES}, f)
                with gzip.open(self.cache_files["stats"], 'wb') as f:
                    pickle.dump(self.cache_stats, f)
                total_size_before = 0
                total_size_after = 0
                for file_path in self.cache_files.values():
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        total_size_after += file_size
                for cache_dict in [LLM_CACHE, ANALYSIS_CACHE, FIX_CACHE, HINT_CACHE, OPTIMIZATION_CACHE]:
                    for k, v in cache_dict.items():
                        if isinstance(v, str):
                            total_size_before += len(v.encode('utf-8'))
                        else:
                            total_size_before += len(pickle.dumps(v))
                compression_ratio = total_size_before / max(1, total_size_after)
                detailed_cache_stats = {
                    "general": len(LLM_CACHE),
                    "analysis": len(ANALYSIS_CACHE),
                    "fix": len(FIX_CACHE),
                    "hint": len(HINT_CACHE),
                    "optimize": len(OPTIMIZATION_CACHE),
                    "compression_ratio": f"{compression_ratio:.2f}x",
                    "total_entries": self.cache_stats["size"],
                    "hit_ratio": f"{self.cache_stats.get('cache_efficiency', 0):.1f}%"
                }
                logger.info(f"Cache saved to disk. Stats: {detailed_cache_stats}")
                return True
            except Exception as e:
                logger.error(f"Error saving cache to disk: {str(e)}")
                return False

cache_manager = CacheManager()

async def clear_cache():
    global LLM_CACHE, LLM_CACHE_EXPIRY, ANALYSIS_CACHE, FIX_CACHE, HINT_CACHE
    global OPTIMIZATION_CACHE, CACHE_USAGE
    with cache_manager.cache_lock:
        LLM_CACHE = {}
        LLM_CACHE_EXPIRY = {}
        ANALYSIS_CACHE = {}
        FIX_CACHE = {}
        HINT_CACHE = {}
        OPTIMIZATION_CACHE = {}
        CACHE_USAGE = {}
        for key in CACHE_HITS:
            CACHE_HITS[key] = 0
            CACHE_MISSES[key] = 0
        cache_manager.save_cache_to_disk()
        return {"success": True, "message": "All caches cleared successfully"} 