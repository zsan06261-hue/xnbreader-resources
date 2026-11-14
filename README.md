# XNB English Reader — resource download mirrors

Public, versioned **GitHub Releases** mirrors for the XNB English Reader. The primary original source remains `https://download.xnbreader.tech/resources/v1/`. This repository stores release manifests and a verified mirror workflow; large assets are hosted as **Release attachments**, not Git blobs.

## Downloads

| Release | Files | Purpose |
|---|---:|---|
| [resources-exams-v1](https://github.com/zsan06261-hue/xnbreader-resources/releases/tag/resources-exams-v1) | 432 | 148 exam PDFs, 148 explanation JSON, 136 original-option JSON |
| [resources-listening-v1](https://github.com/zsan06261-hue/xnbreader-resources/releases/tag/resources-listening-v1) | 78 | CET4/CET6 M4A audio |
| [resources-dictionary-v1](https://github.com/zsan06261-hue/xnbreader-resources/releases/tag/resources-dictionary-v1) | 8 | Longman 6 MDX, two MDD assets, CSS/JS and metadata |
| [resources-speech-macos-v1](https://github.com/zsan06261-hue/xnbreader-resources/releases/tag/resources-speech-macos-v1) | 1 | Kokoro macOS Apple Silicon Python runtime archive |

**519 resources; 1,481,561,203 original bytes.** Every attachment has been compared against its expected SHA-256 digest and length after uploading. See [download-map.json](download-map.json) for the exact mapping from the reader's resource paths to these immutable GitHub Release URLs; [assets.json](assets.json) is the SHA-pinned source manifest used by the mirror workflow.

Kokoro's FP32 model and voice file are not duplicated here; use the [upstream kokoro-onnx official model-files-v1.1 release](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.1).

## Client integration status

These are **available for manual download** today. The existing reader does **not yet** automatically select this GitHub mirror: the downloader needs a larger alternate-source mapping limit, explicit trust handling for GitHub's Release-asset HTTPS redirects, and a server-published mapping. Do not treat this repository's download-map.json as a drop-in client configuration. Keep the primary Korean download source working until the client update is released and tested.

Dictionary Release asset names are stable ASCII identifiers; the reader will need to map them back to canonical dictionary filenames during installation.

## Integrity and rights

- Release assets are immutable by convention: publish a **new version/tag** if file bytes change; never silently replace a pinned SHA.
- The original sources may include material governed by third-party intellectual-property terms. Ownership and redistribution permissions remain the publisher's responsibility; this repository does not assert that such material is open source or grant a blanket license.
- The source vault, user notes, personal books and listening transcript working files have not been uploaded. The Mac runtime archive does not support Windows or Intel Mac.

The [workflow](.github/workflows/mirror-resources.yml) downloads only exact pinned resources from the primary HTTPS origin, checks sizes and SHA-256, and publishes via the repository-scoped GitHub Actions token.
