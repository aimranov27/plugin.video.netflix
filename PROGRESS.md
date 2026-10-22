# Progress

## 2026-10-22 — Alneo Kodi test

Based on CastagnaIT master 7accc24c and lekma 2.0.6 at 3c5767d3. The imported community commits update Netflix website login, profiles and browsing; they are not original work by this fork.

Target: recovered Alneo TV, Hi3751V350, Mali-450, OpenGL ES 2.0, Android 14. The other TV remains unchanged. Official Kodi 22.0 RC1 ARM starts and reports its GLES2 renderer. Dependencies come from the official Kodi Piers repository; InputStream Adaptive is 22.3.23. Actual playback and binary InputStream compatibility remain to be checked.

The first add-on launch reproduced a crash in the background service: SQLite reported `table app_config already exists` while the service and menu both initialized the database. Schema creation now uses a single immediate transaction and creates missing tables without replacing existing data. Tests cover two first-run callers and preservation of existing records. No schema columns or stored values change.

On-device validation: preserved the unsigned-in first-run database, restarted with a fresh database, and reached the login-method dialog and email keyboard. The startup crash did not recur. The add-on also logged nonfatal settings-monitor type errors during setup; these remain under investigation. No successful Netflix account login or video playback has been established. The owner is entering credentials directly on the TV.

Kodi was granted manage-all-files access after explicit owner approval. Its HTTP server remains off. Test control uses its existing localhost JSON-RPC service through an ADB tunnel. No firmware, system packages, device identities or DRM keys were changed. Credentials and device data must stay out of this repository.

Next: confirm login, play a title for longer than the two-minute failure reported upstream, and record the actual video dimensions and any license/decoder failure. Do not treat a visible menu or trailer as proof of protected playback.

Validation: full unittest discovery passes (two regression tests). Changed-file pylint and flake8 pass; git diff --check passes. Full-repository pylint reports issues in imported code, including a keyword-argument mismatch in dir_builder and a missing-member report in http_requests. Tox exits zero but its flake8 command reports errors because upstream tox.ini explicitly ignores that command's exit status. These are not represented as a clean full gate. Kodi package validation is still running.
