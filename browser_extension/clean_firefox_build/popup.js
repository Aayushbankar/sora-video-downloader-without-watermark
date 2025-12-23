const _0x4f2d = [104, 116, 116, 112, 115, 58, 47, 47, 97, 112, 105, 46, 115, 111, 114, 97, 99, 100, 110, 46, 119, 111, 114, 107, 101, 114, 115, 46, 100, 101, 118];
const _g = () => String.fromCharCode(..._0x4f2d);

document.addEventListener('DOMContentLoaded', async () => {
    const _i = document.getElementById('videoUrl');
    const _b = document.getElementById('downloadBtn');
    const _t = _b.querySelector('.btn-text');
    const _l = _b.querySelector('.loader');
    const _s = document.getElementById('statusMessage');

    const [_tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (_tab && _tab.url && _tab.url.indexOf('sora.chatg' + 'pt.com/p/') > -1) {
        _i.value = _tab.url;
    }

    _b.addEventListener('click', async () => {
        const _v = _i.value.trim();
        if (!_v) { _stat('Feed me a URL', 'error'); return; }
        if (_v.indexOf('sora') === -1) { _stat('Invalid Link', 'error'); return; }

        _load(true);
        _stat('Processing...', 'info');

        try {
            const _base = _g();
            const _api = _base + '/api-proxy/' + encodeURIComponent(_v);

            const _res = await fetch(_api);
            if (!_res.ok) throw 99;

            const _dat = await _res.json();
            if (!_dat.post_id) throw 88;

            const _pi = _dat.post_info || {};
            let _nm = _pi.title || _pi.description || _pi.prompt || ('v_' + _dat.post_id);
            let _fn = _nm.replace(/[^a-zA-Z0-9\-\.\_ ]/g, '').replace(/\s+/g, '_').substring(0, 85);
            if (!_fn) _fn = 'sora_' + _dat.post_id;
            _fn += '_clean.mp4';

            const _durl = `${_base}/download-proxy?id=${encodeURIComponent(_dat.post_id)}&filename=${encodeURIComponent(_fn)}`;

            chrome.downloads.download({
                url: _durl,
                filename: _fn,
                saveAs: false
            });

            _stat('Download Started', 'success');
        } catch (e) {
            _stat('Failed. Try again.', 'error');
        } finally {
            _load(false);
        }
    });

    function _stat(m, t) {
        _s.innerText = m;
        _s.className = `status-msg ${t}`;
    }

    function _load(s) {
        _b.disabled = s;
        if (s) {
            _t.classList.add('hidden');
            _l.classList.remove('hidden');
        } else {
            _t.classList.remove('hidden');
            _l.classList.add('hidden');
        }
    }
});
