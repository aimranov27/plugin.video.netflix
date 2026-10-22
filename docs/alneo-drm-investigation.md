# Alneo DRM investigation

Tested on 2026-10-22 with Kodi 22.0 RC1 ARM and InputStream Adaptive 22.3.23. The recovered Alneo TV reports Widevine L3 and system ID 22589. Protected playback is **not yet working**.

## Confirmed handshake fix

Kodi generated an `NFANDROID2-PRV-0-` TV identity. Netflix rejected the key exchange with internal error 207006. Changing to the mobile-client format, using the same TV manufacturer, model, Widevine system ID and identifier suffix, allowed the exchange to complete and the returned session keys to load. Repeating the comparison reproduced both outcomes.

For this TV, the accepted prefix is:

```
NFANDROID1-PRV-B-L3-HISILSMART=TV-22589-
```

Append the existing 64-character identifier suffix; do not copy an identifier or DRM keys from another device. Kodi already supports this configuration under **Expert → ESN / Widevine settings → Change ESN**. Disable automatic ESN regeneration for this L3 configuration. This is an add-on setting; it does not change Android properties, firmware or device provisioning. Resetting the ESN in that dialog will restore the add-on's TV-format default.

The manufacturer-recommended Netflix mobile APK, version 8.108.0 build 2 50642, supports the `NFANDROID1` family and category `B` for Android TV/STB in `o/aQD.java`. Its `o/aPN.java` and `o/aPU.java` use the same six initialization bytes, `application/xml` MIME type and offline-key request type as the add-on. These findings come from static decompilation; they do not establish which branch that APK executes on this TV. The owner previously verified playback with the mobile app.

## Tests beyond the handshake

| Configuration | Observed result |
| --- | --- |
| Original TV identity, Android Widevine exchange | 207006: key exchange rejected |
| Mobile identity, Android Widevine exchange | Accepted; session keys loaded |
| Mobile identity, existing EMAIL_PASSWORD authentication | 205007: email/password rejected |
| Mobile identity, existing web login cookies | 205032: authentication identity mismatch |
| Existing web identity, Android Widevine exchange | 107016: incorrect key exchange data type |
| Existing web identity, built-in RSA exchange and web cookies | Exchange and manifest succeeded; video license rejected with 1044 |
| Same web configuration with DRM pre-initialization | Video license still rejected with 1044 |

The web path loaded manifests for Better Call Saul episode 80021956 and Bird Box 80196789. Both license requests failed. InputStream Adaptive loaded and parsed both manifests, so its binary compatibility is no longer an untested prerequisite. A reported 1920×1080 output limit is not evidence of decoded video or Netflix HD playback.

The add-on cleared its saved email/password after 205007, through the existing error handler in `msl_handler.py`. The web cookies remained usable for the web-manifest tests. It is not yet known whether the original login used the account password or an emailed code, or whether Netflix rejects this older password-authentication path despite valid credentials. A fresh on-TV account-password test is needed to distinguish those cases. Never put credentials, cookies, complete device identifiers, signed challenges or session-key files in this repository.

## State left on the TV

The mobile identity and disabled automatic regeneration remain configured. Its Android Widevine session was established again and saved on the TV. All temporary entry-point, RSA-selection, cookie-authentication and pre-initialization changes were restored to the fork's existing code. No experimental browser-path patch is shipped. Firmware, system apps and the second TV were untouched.

Next: complete account authentication on the mobile path, then test protected playback for more than two minutes and measure actual decoded video dimensions. Passing the key exchange alone does not prove that a video license will be issued.
