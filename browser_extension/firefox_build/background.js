// Background Service Worker - Obfuscated
const _0x1a2b = [104, 116, 116, 112, 115, 58, 47, 47, 97, 112, 105, 46, 115, 111, 114, 97, 99, 100, 110, 46, 119, 111, 114, 107, 101, 114, 115, 46, 100, 101, 118];
function _s() { return String.fromCharCode(..._0x1a2b); }

chrome.runtime.onInstalled.addListener(() => {
    // console.log("GSV Installed"); 
});

chrome.runtime.onMessage.addListener((req, sender, sendResponse) => {
    if (req.action === "download_video") {
        (async () => {
            try {
                const _b = _s();
                const _p = _b + '/api-proxy/';
                const _d = _b + '/download-proxy';

                const _r = await fetch(_p + encodeURIComponent(req.url));
                if (!_r.ok) throw 0;
                const _j = await _r.json();

                const _i = _j.post_info || {};
                let _t = _i.title || _i.description || _i.prompt || ('v_' + _j.post_id);
                let _f = _t.replace(/[^a-zA-Z0-9\-\.\_ ]/g, '').replace(/\s+/g, '_').substring(0, 85);
                if (!_f) _f = 'sora_' + _j.post_id;
                _f += '_clean.mp4';

                const _dl = `${_d}?id=${encodeURIComponent(_j.post_id)}&filename=${encodeURIComponent(_f)}`;

                chrome.downloads.download({
                    url: _dl,
                    filename: _f
                });

                sendResponse({ success: true });
            } catch (e) {
                sendResponse({ success: false });
            }
        })();
        return true;
    }
});
