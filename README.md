# TouchDesigner Asset Cache Component

TD Component to download and cache asset from ACMS.

## Requirements

- Touchdesigner  >= 2025
- Python 3.11

## Installation

Add this dependency to your `requirements.txt`:

```sh
asset-cache-td @ git+https://github.com/artcom/asset-cache-td.git@0.1.0#egg=asset-cache-td
```

Load the tox into your project:

1. create a baseCOMP
2. Common -> External .tox Path = `mod.asset_cache_td.ToxFile`
3. Common -> Enable External .tox = ON
4. Common -> Reload custom parameters = OFF


## Usage

Parameters on page "Input":

| Parameter       | Description                                                                                  |
| :-------------- | :------------------------------------------------------------------------------------------- |
| `AssetCacheDir` | The root directory of the asset cache. Directory structure will be created on first download |
| `AssetConfig`   | JSON DAT containing the asset description                                                    |
| `Offline`       | Asset cache works offline and does not sync data from ACMS. Calls `onUpdateFinished`.        |
| `Download`      | Manual trigger for download                                                                  |

To download assets use method call:

```py
op.AssetCache.DownloadAssets()
```

Callbacks will inform over status:

| Callback             | Description                        |
| :------------------- | :--------------------------------- |
| `onUpdateStart`      | Update of asset cache started      |
| `onUpdateFinished`   | Update of asset cache finished     |
| `onDownloadStart`    | Download of a single file started  |
| `onDownloadFinished` | Download of a single file finished |
| `onDownloadFailure`  | Download of a single file failed   |
