# Progress

## 2026-10-22 — DRM handshake diagnosis

Confirmed that the TV-format identity causes error 207006 on the recovered Alneo. Using its own hardware details in the mobile `NFANDROID1-PRV-B-L3-` format passes key exchange and loads the returned keys. The comparison was repeated with the same identifier suffix. This is an existing ESN configuration option, so no production code change was needed. See [the investigation record](docs/alneo-drm-investigation.md).

Playback remains blocked: the mobile path's stored email/password was rejected (205007), and the add-on then cleared those saved credentials. Web cookies used with the mobile identity fail identity validation (205032). A separate browser-identity/RSA experiment authenticated and loaded manifests for two titles, but both license requests failed with 1044; DRM pre-initialization did not resolve that error. InputStream Adaptive loaded and parsed the manifests. No protected playback or resolution is verified.

Restored all temporary code changes on the TV and kept the verified mobile ESN configuration, automatic regeneration disabled, and a fresh Android Widevine session. Next: establish whether the prior login used an email code, test account-password authentication directly on the TV, and then test playback. No firmware, system packages, donor credentials or the other TV were changed. The main tv-setup checkout is unchanged.

## 2026-10-22 — Alneo Kodi test

Based on CastagnaIT master 7accc24c and lekma 2.0.6 at 3c5767d3. The imported community commits update Netflix website login, profiles and browsing; they are not original work by this fork.

Target: recovered Alneo TV, Hi3751V350, Mali-450, OpenGL ES 2.0, Android 14. The other TV remains unchanged. Official Kodi 22.0 RC1 ARM starts and reports its GLES2 renderer. Dependencies come from the official Kodi Piers repository; InputStream Adaptive is 22.3.23. Actual playback and binary InputStream compatibility remain to be checked.

The first add-on launch reproduced a crash in the background service: SQLite reported `table app_config already exists` while the service and menu both initialized the database. Schema creation now uses a single immediate transaction and creates missing tables without replacing existing data. Tests cover two first-run callers and preservation of existing records. No schema columns or stored values change.

On-device validation: preserved the unsigned-in first-run database, restarted with a fresh database, and reached the login-method dialog and email keyboard. The startup crash did not recur. The add-on also logged nonfatal settings-monitor type errors during setup; these remain under investigation. The owner signed in directly on the TV. Profiles and episode browsing work. Playback fails at the MSL key exchange with Netflix internal error 207006, "Request failed validation during key exchange"; later attempts also report CryptoSession getKeyRequest failed. Kodi reads Widevine L3, system ID 22589 and unprotected HDCP. No video playback or resolution has been verified.

Kodi was granted manage-all-files access after explicit owner approval. Its HTTP server remains off. Test control uses its existing localhost JSON-RPC service through an ADB tunnel. No firmware, system packages, device identities or DRM keys were changed. Credentials and device data must stay out of this repository.

Next: confirm login, play a title for longer than the two-minute failure reported upstream, and record the actual video dimensions and any license/decoder failure. Do not treat a visible menu or trailer as proof of protected playback.

Validation: full unittest discovery passes (seven regression tests). New test files pass pylint and flake8; imported modules retain their pre-existing lint findings; git diff --check passes. Full-repository pylint reports issues in imported code, including a keyword-argument mismatch in dir_builder and a missing-member report in http_requests. Tox exits zero but its flake8 command reports errors because upstream tox.ini explicitly ignores that command's exit status. These are not represented as a clean full gate. Kodi package validation passed with four warnings (two external link responses, Python dependency version advice and an unpinned requests minimum).

Review fixes: preserve long seasons by expanding the episode selector count, falling back to the existing paginated request if the server caps it; reuse cached My List membership in search; refresh context actions after My List changes; keep automatic watched updates in the bookmark cache instead of the persistent manual override table. Regression tests reproduced all four findings before the changes and pass afterward.
