# TouchDesigner Asset Cache Component

Component to download and cache asset from ACMS.

## Requirements

- Touchdesigner  >= 2023.12370
- Python 3.11

## Installation

Copy this directory into the "external" folder on the base directory of your project:

```sh
./external/asset-cache
```

Load the tox into your project

In the "Common" page set "Reload custom parameters" to "OFF"

## Usage

Parameters on page "Input":

| Parameter       | Description                                                                                   |
| :-------------- | :-------------------------------------------------------------------------------------------- |
| `AssetCacheDir` | The root directory of the asset cache. Directory structure will be created on first download |
| `AssetConfig`   | JSON DAT containing the asset description                                                     |
| `Download`      | Manual trigger for download                                                                   |

To download assets use method call:

```py
op.AssetCache.DownloadAssets()
```
