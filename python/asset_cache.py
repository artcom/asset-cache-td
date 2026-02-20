import copy
import json
import logging
import os
from pathlib import Path
from urllib.parse import urlparse
import requests


class AssetCache:

    def __init__(self, ownerComp):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._owner_comp = ownerComp

    def DownloadAssets(self):
        self._logger.info("Downloading assets...")
        manifest = op('manifest').result
        if manifest is None:
            manifest = {}

        assets_dir = str(self._owner_comp.par.Assetcachedir)
        self._create_cache_dir(assets_dir)

        operator = self._owner_comp.par.Assetconfig
        asset_config = op(operator).result
        assets = copy.deepcopy(asset_config)

        updated_assets = []
        self._process_assets(assets, assets_dir, manifest, updated_assets)
        self._purge_cache(manifest, assets_dir, updated_assets)
        self._save_manifest(manifest)

        self._rewrite_asset_urls(assets, assets_dir)
        self._save_assets(assets)

    def _create_cache_dir(self, cache_dir: str):
        Path(cache_dir).mkdir(parents=True, exist_ok=True)

    def _process_assets(self, node: any, assets_dir: str, manifest: dict, updated_assets: list):
        if isinstance(node, list):
            for element in node:
                self._process_assets(element, assets_dir,
                                     manifest, updated_assets)
        elif isinstance(node, dict):
            for value in node.values():
                self._process_assets(
                    value, assets_dir, manifest, updated_assets)
        elif isinstance(node, str):
            if self._is_url(node):
                self._download_asset(
                    node, assets_dir, manifest, updated_assets)

    def _download_asset(self, url: str,  assets_dir: str, manifest: dict, updated_assets: list):
        headers = self._get_asset_headers(url)
        if headers is None:
            return
        filename = self._get_filename(url)
        updated_assets.append(filename)
        if not self._is_asset_outdated(manifest, headers, filename):
            return

        filepath = self._get_filepath(assets_dir, url)
        headers = self._download_file(url, filepath)
        if headers:
            manifest[filename] = headers

    def _rewrite_asset_urls(self, node, assets_dir: str):
        if isinstance(node, list):
            for element in node:
                self._rewrite_asset_urls(element, assets_dir)
        elif isinstance(node, dict):
            for key, value in node.items():
                if isinstance(value, str) and self._is_url(value):
                    node[key] = self._get_filepath(assets_dir, value)
                else:
                    self._rewrite_asset_urls(value, assets_dir)

    def _purge_cache(self, manifest: dict, assets_dir: str, updated_assets: list):
        files_to_delete = []
        for filename in manifest.keys():
            if filename not in updated_assets:
                files_to_delete.append(filename)

        for filename in files_to_delete:
            self._purge_file(filename, manifest, assets_dir)

    def _purge_file(self, filename: str, manifest: dict, assets_dir: str):
        del manifest[filename]
        filepath = os.path.join(assets_dir, filename)
        os.remove(filepath)

    def _save_manifest(self, manifest: dict):
        op('manifest_text').text = json.dumps(manifest)
        op('manifest_save').par.write.pulse()

    def _save_assets(self, assets: dict):
        op('assets_text').text = json.dumps(assets)
        op('assets_save').par.write.pulse()

    def _download_file(self, url: str, filepath: str) -> dict:
        try:
            with requests.get(url, stream=True, timeout=10) as r:
                r.raise_for_status()
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                    return self._extract_headers(r.headers)
        except requests.Timeout as e:
            self._logger.error(e)
        except Exception as e:
            self._logger.error(e)

    def _extract_headers(self, headers: dict) -> dict:
        return {
            'ETag': headers['ETag'],
            'Last-Modified': headers['Last-Modified']
        }

    def _get_asset_headers(self, url: str) -> dict:
        try:
            with requests.head(url, allow_redirects=True, timeout=10) as r:
                return self._extract_headers(r.headers)
        except requests.Timeout as e:
            self._logger.error(e)
        except Exception as e:
            self._logger.error(e)

    def _is_asset_outdated(self, manifest: dict, headers: dict, filename: str) -> bool:
        if filename not in manifest:
            return True

        entry = manifest[filename]
        if 'ETag' in headers and headers['ETag'] != entry['ETag']:
            return True

        if 'Last-Modified' in headers and headers['Last-Modified'] != entry['Last-Modified']:
            return True

        return False

    def _is_url(self, string: str) -> bool:
        try:
            result = urlparse(string)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def _get_filename(self, url: str) -> str:
        filepath = urlparse(url).path
        return os.path.basename(filepath)

    def _get_filepath(self, assets_dir: str, url: str) -> str:
        filename = self._get_filename(url)
        return os.path.join(assets_dir, filename)
