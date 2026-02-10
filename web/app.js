/**
 * Talk2Scene Frontend Viewer
 * Loads JSONL events and animates layered scene composition.
 * Modes: Replay (from first event) and Realtime (tail latest events).
 */

class Talk2SceneViewer {
    constructor() {
        this.events = [];
        this.currentIndex = 0;
        this.mode = 'idle'; // idle | replay | realtime
        this.speed = 1.0;
        this.playing = false;
        this.timer = null;
        this.assetBase = 'assets';
        this.audioPlayer = document.getElementById('audio-player');
        this.realtimeInterval = null;

        this._bindElements();
        this._bindEvents();
    }

    _bindElements() {
        this.layers = {
            bg: document.getElementById('layer-bg'),
            sta: document.getElementById('layer-sta'),
            act: document.getElementById('layer-act'),
            exp: document.getElementById('layer-exp'),
            cg: document.getElementById('layer-cg'),
        };
        this.subtitle = document.getElementById('subtitle');
        this.slider = document.getElementById('timeline-slider');
        this.speedInput = document.getElementById('speed');
        this.speedVal = document.getElementById('speed-val');
        this.eventLog = document.getElementById('event-log');
        this.infoEvent = document.getElementById('info-event');
        this.infoTime = document.getElementById('info-time');
        this.infoMode = document.getElementById('info-mode');
        this.infoSpeaker = document.getElementById('info-speaker');
    }

    _bindEvents() {
        document.getElementById('jsonl-input').addEventListener('change', (e) => this._loadFile(e));
        document.getElementById('btn-replay').addEventListener('click', () => this.startReplay());
        document.getElementById('btn-realtime').addEventListener('click', () => this.startRealtime());
        document.getElementById('btn-pause').addEventListener('click', () => this.pause());
        document.getElementById('btn-stop').addEventListener('click', () => this.stop());
        document.getElementById('audio-input').addEventListener('change', (e) => this._loadAudio(e));

        this.speedInput.addEventListener('input', (e) => {
            this.speed = parseFloat(e.target.value);
            this.speedVal.textContent = this.speed + 'x';
        });

        this.slider.addEventListener('input', (e) => {
            const idx = Math.round((parseInt(e.target.value) / 100) * (this.events.length - 1));
            this.seekTo(idx);
        });

        document.getElementById('asset-base').addEventListener('change', (e) => {
            this.assetBase = e.target.value;
        });
    }

    _loadFile(e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (ev) => {
            const text = ev.target.result;
            this.events = [];
            const lines = text.split('\n');
            for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed) continue;
                try {
                    const event = JSON.parse(trimmed);
                    if (event.type === 'scene') {
                        this.events.push(event);
                    }
                } catch (err) {
                    // skip invalid lines
                }
            }
            this.slider.max = 100;
            this._log(`Loaded ${this.events.length} scene events`);
            this._updateInfo();

            if (this.events.length > 0) {
                this._renderEvent(this.events[0]);
            }
        };
        reader.readAsText(file);
    }

    _loadAudio(e) {
        const file = e.target.files[0];
        if (!file) return;
        const url = URL.createObjectURL(file);
        this.audioPlayer.src = url;
        this._log('Audio loaded: ' + file.name);
    }

    startReplay() {
        this.stop();
        this.mode = 'replay';
        this.currentIndex = 0;
        this.playing = true;
        this._updateInfo();
        this._log('Replay started');

        if (this.audioPlayer.src) {
            this.audioPlayer.currentTime = 0;
            this.audioPlayer.play();
        }

        this._playNext();
    }

    startRealtime() {
        this.stop();
        this.mode = 'realtime';
        this.playing = true;
        this.currentIndex = Math.max(0, this.events.length - 1);
        this._updateInfo();
        this._log('Realtime mode started (showing latest events)');

        if (this.events.length > 0) {
            this._renderEvent(this.events[this.currentIndex]);
        }

        // In realtime mode, we poll for the latest event
        this.realtimeInterval = setInterval(() => {
            if (this.currentIndex < this.events.length - 1) {
                this.currentIndex = this.events.length - 1;
                this._renderEvent(this.events[this.currentIndex]);
                this._updateInfo();
            }
        }, 500);
    }

    pause() {
        this.playing = false;
        if (this.timer) {
            clearTimeout(this.timer);
            this.timer = null;
        }
        if (this.realtimeInterval) {
            clearInterval(this.realtimeInterval);
            this.realtimeInterval = null;
        }
        if (this.audioPlayer.src) {
            this.audioPlayer.pause();
        }
        this._log('Paused');
        this.infoMode.textContent = 'paused';
    }

    stop() {
        this.playing = false;
        this.mode = 'idle';
        if (this.timer) {
            clearTimeout(this.timer);
            this.timer = null;
        }
        if (this.realtimeInterval) {
            clearInterval(this.realtimeInterval);
            this.realtimeInterval = null;
        }
        if (this.audioPlayer.src) {
            this.audioPlayer.pause();
            this.audioPlayer.currentTime = 0;
        }
        this._updateInfo();
    }

    seekTo(index) {
        if (index < 0 || index >= this.events.length) return;
        this.currentIndex = index;
        this._renderEvent(this.events[index]);
        this._updateInfo();

        // Sync audio if available
        const event = this.events[index];
        if (this.audioPlayer.src && event.start !== undefined) {
            this.audioPlayer.currentTime = event.start;
        }
    }

    _playNext() {
        if (!this.playing || this.currentIndex >= this.events.length) {
            if (this.currentIndex >= this.events.length) {
                this._log('Replay complete');
                this.mode = 'idle';
                this._updateInfo();
            }
            return;
        }

        const event = this.events[this.currentIndex];
        this._renderEvent(event);
        this._updateInfo();

        // Calculate delay to next event
        let delay = 1000; // default 1s
        if (this.currentIndex + 1 < this.events.length) {
            const next = this.events[this.currentIndex + 1];
            if (event.start !== undefined && next.start !== undefined) {
                delay = Math.max(100, (next.start - event.start) * 1000);
            }
        }

        delay = delay / this.speed;
        this.currentIndex++;

        this.timer = setTimeout(() => this._playNext(), delay);
    }

    _renderEvent(event) {
        // CG is a full-scene illustration that REPLACES the normal layers.
        // Normal layering (no CG): BG -> STA -> ACT -> EXP
        const hasCG = event.cg && event.cg !== 'CG_None';

        if (hasCG) {
            // CG mode: show only the CG illustration, hide everything else
            const cgSrc = `${this.assetBase}/cg/${event.cg}.png`;
            const cgEl = this.layers.cg;
            if (!cgEl.src.endsWith(cgSrc)) {
                cgEl.src = cgSrc;
            }
            cgEl.style.opacity = '1';

            // Hide normal layers
            for (const layer of ['bg', 'sta', 'act', 'exp']) {
                this.layers[layer].style.opacity = '0';
            }
        } else {
            // Normal mode: compose BG -> STA -> ACT -> EXP, hide CG
            this.layers.cg.style.opacity = '0';

            const normalLayers = {
                bg: event.bg,
                sta: event.sta,
                act: event.act,
                exp: event.exp,
            };

            for (const [layer, code] of Object.entries(normalLayers)) {
                const el = this.layers[layer];
                if (code && !code.endsWith('_None')) {
                    const src = `${this.assetBase}/${layer}/${code}.png`;
                    if (!el.src.endsWith(src)) {
                        el.src = src;
                        el.style.opacity = '1';
                    }
                } else {
                    el.style.opacity = '0';
                    el.removeAttribute('src');
                }
            }
        }

        // Update subtitle
        this.subtitle.textContent = event.text || '';
        this.infoSpeaker.textContent = event.speaker_id || '-';

        // Update slider
        if (this.events.length > 1) {
            const pct = (this.currentIndex / (this.events.length - 1)) * 100;
            this.slider.value = pct;
        }
    }

    _updateInfo() {
        this.infoEvent.textContent = `${this.currentIndex + 1}/${this.events.length}`;
        this.infoMode.textContent = this.mode;

        if (this.events.length > 0 && this.currentIndex < this.events.length) {
            const ev = this.events[this.currentIndex];
            this.infoTime.textContent = (ev.start !== undefined ? ev.start.toFixed(1) : '0.0') + 's';
        }
    }

    _log(msg) {
        const entry = document.createElement('div');
        entry.className = 'event-entry';
        const ts = new Date().toLocaleTimeString();
        entry.textContent = `[${ts}] ${msg}`;
        this.eventLog.prepend(entry);

        // Limit log entries
        while (this.eventLog.children.length > 100) {
            this.eventLog.removeChild(this.eventLog.lastChild);
        }
    }
}

// Initialize
const viewer = new Talk2SceneViewer();
